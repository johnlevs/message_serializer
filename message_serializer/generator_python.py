from message_serializer.ast import ast
from message_serializer.generator import Generator, logger
from message_serializer.python_config import *
from message_serializer.parser import is_number

import os


class pythonGenerator(Generator):
    # common variable names
    bStrVName = "bStr"
    bfBstrVName = "bfBstr"

    def __init__(self, tree: ast):
        self.inlineCommentChar = "#"
        super().__init__(tree)

    def generate(self):

        imports = [
            "import numpy as np",
            "from typing import List",
            "from bitstring import BitArray, BitStream",
            "from serializer.serializer import serializableMessage",
        ]
        importStr = "\n".join(imports) + "\n\n\n"

        msgIds = self._generate_message_id_list()
        modules = self._generate_module_members(
            [
                self.ast_tree.constant_iterator(),
                self.ast_tree.state_iterator(),
                self.ast_tree.message_iterator(),
            ],
            [
                self._generate_constants,
                self._generate_enum,
                self._generate_message,
            ],
        )

        return self.get_license() + importStr + msgIds + modules

    def _generate_message(self, message):
        line = f"{self.tab()}class {message['name']}" + "(serializableMessage):\n"
        self.indent()
        line += self._generate_message_docs(message)
        line += (
            self.tab()
            + '"""############################################ USER DATA ############################################"""\n\n'
        )

        for field in message["fields"]:
            line += self._print_variable(field)

        line += (
            self.tab()
            + '"""########################################## SERIALIZATION ##########################################"""\n\n'
        )

        line += self._generate_message_initializer(message)
        line += self._generate_message_serialization_helper(message)
        line += self._generate_message_deserialization_helper(message)
        self.dedent()
        return line

    def _generate_message_docs(self, message):
        line = f'{self.tab()}"""\n'
        if DOC in message.keys():
            line += f"{self.tab()}{message[DOC][1:-1]}"
        line += f"\n"

        # add parameters
        self.indent()
        for field in message["fields"]:
            line += f"{self.tab()}:param {field['name']}:"
            if DOC in field.keys():
                line += f" {field[DOC][1:-1]}\n"
            else:
                line += f" \n"
            line += f"{self.tab()}:type {field['name']}: {self.get_type(field)}\n"
        self.dedent()

        line += f'\n {self.tab()}"""\n'
        return line

    def _generate_message_id_list(self):
        line = f"{self.tab()}class wordIds:\n"
        self.indent()
        index = 0
        for module in self.ast_tree.tree:
            for message in module["messages"]:
                line += f"{self.tab()}{module['name'].upper()}_{message['name'].upper()} = {index}\n"
                index += 1
        self.dedent()
        return line + "\n"

    def _generate_enum(self, enum):
        # since there aren't enumerated values in python, we will use a class with constants and increment values as they are added like in C++
        line = f"{self.tab()}class {enum['name']}:\n"
        self.indent()
        enumValue = 0
        for parameter in enum["fields"]:
            line += f"{self.tab()}{parameter['name']} = {str(enumValue)}\n"
            enumValue += 1
        self.dedent()
        return f"{line}\n"

    def _generate_constants(self, constant):
        resolvedType = (
            BUILTIN_TO_PYTHON[constant["type"]]
            if constant["type"] in BUILTIN_TO_PYTHON.keys()
            else constant["type"]
        )
        if is_number(constant["default_value"]):
            dv = constant["default_value"]
        else:
            dv = self._msg_name_w_scope_from_name(constant["default_value"])
        line = f"{self.tab()}{constant['name'].upper()}: {resolvedType} = {dv}\n"
        return line + "\n"

    def _generate_module_members(self, iterators, generators):
        line = ""
        moduleName = None
        for iterator, generator in zip(iterators, generators):
            for member in iterator:
                if moduleName != member["parent"]["name"]:
                    if moduleName is not None:
                        self.dedent()

                    line += f"class {member['parent']['name']}:\n"
                    self.indent()
                    moduleName = member["parent"]["name"]
                line += f"{generator(member)}\n"
        if moduleName is not None:
            self.dedent()

        return line

    def _generate_message_deserialization_helper(self, message):
        line = f"{self.tab()}def deserialize(self, byteArr):\n"
        self.indent()
        line += f"{self.tab()}{self.bStrVName} = BitStream(bytes=byteArr)\n"
        line += self._message_field_worker(
            message,
            on_bf_open=lambda field, *args: "",
            on_bf_close=lambda field, *args: "",
            on_bf=lambda field, *args: f"{self.tab()}self.{self._field_name(field)} = {self.bStrVName}.read('uint:{field['count']}')\n",
            on_udf=lambda field, *args: self._deserialize_user_defined(field),
            on_df=lambda field, *args: self._deserialize_builtin(field, self.bStrVName),
        )
        self.dedent()
        return line + "\n"

    def _generate_message_serialization_helper(self, message):
        line = f"{self.tab()}def serialize(self) -> bytes:\n"
        self.indent()
        line += f"{self.tab()}{self.bStrVName} = BitStream()\n"
        line += self._message_field_worker(
            message,
            on_bf_open=lambda field, *args: f"{self.tab()}{self.bfBstrVName} = BitStream()\n",
            on_bf_close=lambda field, *args: f"{self.tab()}{self.bStrVName}.append(self.reverse_bits({self.bfBstrVName}))\n",
            on_bf=lambda field, *args: f"{self.tab()}{self.bfBstrVName}.append(BitStream(uint=self.{self._field_name(field)}, length={field['count']}))\n",
            on_udf=lambda field, *args: self._serialize_user_defined(field),
            on_df=lambda field, *args: self._serialize_builtin(field, self.bStrVName),
        )
        line += f"{self.tab()}return {self.bStrVName}.bytes\n"
        self.dedent()
        return line + "\n"

    def _serialize_user_defined(self, field):
        name = self._field_name(field)

        if not is_number(field["count"]) or field["count"] > 1:
            count = self._msg_name_w_scope_from_name(field["count"])
            line = f"{self.tab()}for i in range({count}):\n"
            self.indent()
            line += (
                f"{self.tab()}bStr.append(BitArray(bytes=self.{name}[i].serialize()))\n"
            )
            self.dedent()
        else:
            line = f"{self.tab()}bStr.append(BitArray(bytes=self.{name}.serialize()))\n"
        return line

    def _deserialize_user_defined(self, field):
        name = self._field_name(field)

        if not is_number(field["count"]) or field["count"] > 1:
            count = self._msg_name_w_scope_from_name(field["count"])
            line = f"{self.tab()}for i in range({count}):\n"
            self.indent()
            line += f"{self.tab()}self.{name}[i].deserialize({self.bStrVName})\n"
            self.dedent()
        else:
            line = f"{self.tab()}self.{name}.deserialize({self.bStrVName})\n"
        return line

    def _deserialize_builtin(self, field, bStrVName):
        name = self._field_name(field)

        # bitfield case
        if field["type"] == BF:
            line = (
                f"{self.tab()}self.{name} = {bStrVName}.read('uint:{field['count']}')\n"
            )
        # array case
        elif field["count"] > 1:
            line = f"{self.tab()}for i in range({field['count']}):\n"
            self.indent()
            line += f"{self.tab()}self.{name}[i] = {bStrVName}.read('{BUILTIN_TO_BIT_STRINGS[field['type']]}')\n"
            self.dedent()
        # single case
        else:
            line = f"{self.tab()}self.{name} = {bStrVName}.read('{BUILTIN_TO_BIT_STRINGS[field['type']]}')\n"
        return line

    def _serialize_builtin(self, field, bStrVName):
        name = self._field_name(field)

        # bitfield case
        if field["type"] == BF:
            line = f"{self.tab()}{bStrVName}.append(BitStream(uint=self.{name}, length={field['count']}))\n"
        # array case
        elif field["count"] > 1:
            line = f"{self.tab()}for i in range({field['count']}):\n"
            self.tab()
            line += f"{self.tab()}{bStrVName}.append(BitStream(uint=self.{name}[i], length={BUILTINS[field['type']][BITLENGTH]}))\n"
            self.dedent()
        # single case
        else:
            line = f"{self.tab()}{bStrVName}.append(BitStream(uint=self.{name}, length={BUILTINS[field['type']][BITLENGTH]}))\n"
        return line

    def generate_source_files(self, output_dir, source_name=None):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        template_dir = os.path.join(this_dir, "..", "templates", "python")

        self._copy_template_file(
            f"{output_dir}/serializer", template_dir, "serializer.py"
        )

        with open(f"{output_dir}/{source_name}.py", "w") as f:
            f.write(self.generate())

    def _print_variable(self, field):
        # add variable
        name = self._field_name(field)
        line = f"{self.tab()}{name}: "
        if field["type"] != BF and (
            not is_number(field["count"]) or int(field["count"]) > 1
        ):
            line += f"List['{self.get_type(field)}']\n"
        else:
            line += f"{self.get_type(field)}\n"

        # add docs
        line += f'{self.tab()}"""'
        if DOC in field.keys():
            line += f"{self.tab()}{field[DOC][1:-1]}"
        line += f'{self.tab()}"""\n'

        return line

    def get_type(self, field):
        line = ""
        if field["type"] in BUILTIN_TO_PYTHON.keys():
            line += f"{BUILTIN_TO_PYTHON[field['type']]}"
        else:
            # this should have a valid type as determined by the validator
            logger.debug("Resolving type for " + field["type"])
            member = self.ast_tree.find_member(field["type"])
            resolvedType = member[0][0] + "."
            if member[2] is not None:
                resolvedType += (
                    +self.ast_tree.tree[member[0][1]][member[1][1]]["name"] + "."
                )
            resolvedType += field["type"]
            line += f"{resolvedType}"

        return line

    def _generate_message_initializer(self, message):
        line = f"{self.tab()}def __init__(self):\n"
        self.indent()
        for field in message["fields"]:
            name = self._field_name(field)
            if field["type"] != BF and (
                not is_number(field["count"]) or int(field["count"]) > 1
            ):
                count = self._msg_name_w_scope_from_name(field["count"])
                line += f"{self.tab()}self.{name} = [{self._msg_name_w_scope_from_name(field['type'])}] * {count}\n"

            else:
                if field["default_value"] is not None:
                    if is_number(field["default_value"]):
                        dv = field["default_value"]
                    else:  # user defined type
                        dv = self._msg_name_w_scope_from_name(field["default_value"])
                    line += f"{self.tab()}self.{name} = {dv}\n"
                elif field["type"] not in BUILTIN_TO_PYTHON.keys():
                    line += f"{self.tab()}self.{name} = {self._msg_name_w_scope_from_name(field['type'])}()\n"
                else:
                    line += f"{self.tab()}self.{name} = {BUILTINS[field['type']][DEFAULT_VALUE]}\n"
        self.dedent()
        return f"{line}\n\n"

    def _field_name(self, field):
        # needed so python doesn't mangle names with __
        name = field["name"]
        if field["name"][0:2] == "__":
            name = field["name"][1:]
        return name

    def _msg_name_w_scope(self, message):
        temp = f"{message['parent']['name']}.{message['name']}"
        if "parent" in message["parent"]:
            temp = f"{message['parent']['parent']['name']}.{temp}"
        return temp;

    def _msg_name_w_scope_from_name(self, name):
        return self._msg_name_w_scope(self.ast_tree.find_member_reference(name))