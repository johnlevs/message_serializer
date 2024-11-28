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

        modules = ""
        for module in self.tree.tree:
            modules += self._generate_module(module)

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
        for module in self.tree.tree:
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
        line = f"{self.tab()}{constant['name'].upper()}: {resolvedType} = {constant['default_value']}\n"
        return line + "\n"

    def _generate_module(self, module):
        line = f"class {module['name']}:\n"
        self.indent()
        for constant in module["constants"]:
            line += self._generate_constants(constant)

        for enum in module["states"]:
            line += self._generate_enum(enum)

        for message in module["messages"]:
            line += self._generate_message(message)

        self.dedent()
        return line + "\n"

    def _generate_message_deserialization_helper(self, message):
        line = f"{self.tab()}def deserialize(self, byteArr):\n"
        self.indent()
        line += f"{self.tab()}{self.bStrVName} = BitStream(bytes=byteArr)\n"
        line += self._message_field_worker(
            message,
            on_bf_open=lambda field: "",
            on_bf_close=lambda field: "",
            on_bf=lambda field: f"{self.tab()}self.{self._field_name(field)} = {self.bStrVName}.read('uint:{field['count']}')\n",
            on_udf=lambda field: self._deserialize_user_defined(field),
            on_df=lambda field: self._deserialize_builtin(field, self.bStrVName),
        )
        self.dedent()
        return line + "\n"

    def _generate_message_serialization_helper(self, message):
        line = f"{self.tab()}def serialize(self) -> bytes:\n"
        self.indent()
        line += f"{self.tab()}{self.bStrVName} = BitStream()\n"
        line += self._message_field_worker(
            message,
            on_bf_open=lambda field: f"{self.tab()}{self.bfBstrVName} = BitStream()\n",
            on_bf_close=lambda field: f"{self.tab()}{self.bStrVName}.append({self.bfBstrVName})\n",
            on_bf=lambda field: f"{self.tab()}{self.bfBstrVName}.append(BitStream(uint=self.{self._field_name(field)}, length={field['count']}))\n",
            on_udf=lambda field: self._serialize_user_defined(field),
            on_df=lambda field: self._serialize_builtin(field, self.bStrVName),
        )
        line += f"{self.tab()}return {self.bStrVName}.bytes\n"
        self.dedent()
        return line + "\n"

    def _serialize_user_defined(self, field):
        name = self._field_name(field)

        if not is_number(field["count"]) or field["count"] > 1:
            count = self.retrieve_constant_hierarchy(field["count"])
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
            count = self.retrieve_constant_hierarchy(field["count"])
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

    def _generate_message_deserialization(self, message):
        pass

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
            member = self.tree.find_member(field["type"])
            resolvedType = member[0][0] + "."
            if member[2] is not None:
                resolvedType += (
                    +self.tree.tree[member[0][1]][member[1][1]]["name"] + "."
                )
            resolvedType += field["type"]
            line += f"{resolvedType}"

        return line

    def _generate_message_initializer(self, message):
        line = f"{self.tab()}def __init__(self):\n"
        self.indent()
        for field in message["fields"]:
            if field["type"] != BF and (
                not is_number(field["count"]) or int(field["count"]) > 1
            ):
                count = self.retrieve_constant_hierarchy(field["count"])
                line += f"{self.tab()}self.{field['name']} = [{self.get_type(field)}() for _ in range({count})]\n"

            else:
                if field["default_value"] is not None:
                    line += f"{self.tab()}self.{field['name']}{self.get_default_value(field)}"
                elif field["type"] not in BUILTIN_TO_PYTHON.keys():
                    line += (
                        f"{self.tab()}self.{field['name']} = {self.get_type(field)}()\n"
                    )
        self.dedent()
        return f"{line}\n\n"

    def get_default_value(self, field):
        line = ""
        # determine default value
        if field["default_value"] is not None:
            if is_number(field["default_value"]):
                line += f" = {field['default_value']}"
            else:
                # this should resolve to a constant as determined by the validator
                logger.debug(f"Searching for default value of {field['default_value']}")
                line += f" = {self.retrieve_constant_hierarchy(field['default_value'])}"
        return line

    def retrieve_constant_hierarchy(self, name):
        member = self.tree.find_member(name)
        line = ""
        if member is None:
            line += f" = {name}"
        else:
            hierarchy = (
                self.tree.tree[member[0][1]]["name"]
                + "."
                + self.tree.tree[member[0][1]][member[1][0]][member[1][1]]["name"]
            )
            if len(member) == 3 and member[2] is not None:
                hierarchy += "." + name
            line += f"{hierarchy}"
        return line

    def _field_name(self, field):
        # needed so python doesn't mangle names with __
        name = field["name"]
        if field["name"][0:2] == "__":
            name = field["name"][1:]
        return name
