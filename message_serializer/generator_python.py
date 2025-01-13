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
        super().__init__(
            tree,
            "#",
            lambda higher, lower: f"{higher}.{lower}",
            BUILTIN_TO_PYTHON,
        )

    def generate(self):

        imports = [
            "import numpy as np",
            "from typing import List",
            "from bitstring import BitArray, BitStream",
            "from serializer.serializer import serializableMessage",
        ]
        importStr = "\n".join(imports) + "\n\n\n"

        msgIds = self._generate_message_id_list()
        modules = self._generate_module_members()

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
            line += self._print_variable_declaration(field)

        line += (
            "\n"
            + self.tab()
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
            line += f"{self.tab()}{message[DOC]}"
        line += f"\n"

        # add parameters
        self.indent()
        for field in message["fields"]:
            line += f"{self.tab()}:param {field['name']}:"
            line += f" {field[DOC]}\n" if DOC in field.keys() else "\n"
            line += f"{self.tab()}:type {field['name']}: '{self.get_language_type(field)}'\n"
        self.dedent()

        line += f'\n {self.tab()}"""\n'
        return line

    def _generate_message_id_list(self):
        line = f"{self.tab()}class wordIds:\n"
        self.indent()
        index = 0
        for message in self.ast_tree.message_iterator():
            line += f"{self.tab()}{self.msg_2_wordID(message)} = {index}\n"
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
        dv = self.get_default_value(constant)
        e_type = self.get_language_type(constant)
        line = f"{self.tab()}{constant['name'].upper()}: {e_type} = {dv}\n"
        return line + "\n"

    def _generate_module_members(self):
        generators = {
            "MSG": self._generate_message,
            STATE: self._generate_enum,
            CONST: self._generate_constants,
        }
        line = ""
        moduleName = None
        newName = None

        for element in self.ast_tree.print_order_iterator():
            e_type = self.ast_tree.get_type(element)
            newName = self.get_module_name(element)
            generator = (
                generators[CONST] if e_type in BUILTINS.keys() else generators[e_type]
            )
            if moduleName != element["parent"]["name"]:
                if moduleName is not None:
                    self.dedent()

                line += f"class {newName}:\n"
                self.indent()
                moduleName = newName
            line += f"{generator(element)}\n"

        if moduleName is not None:
            self.dedent()

        return line

    def _generate_message_deserialization_helper(self, message):

        deseralize_bf_members = lambda bf: "".join(
            f"{self.tab()}self.{self._field_name(field)} = {self.bStrVName}.read('uint:{field['count']}')\n"
            for field in bf["fields"]
        )

        line = f"{self.tab()}def deserialize(self, byteArr):\n"
        self.indent()
        line += f"{self.tab()}{self.bStrVName} = BitStream(bytes=byteArr)\n"
        line += self._message_field_worker(
            message,
            on_bf_open=lambda field, *args: "",
            on_bf_close=lambda field, *args: "",
            on_bf=lambda field, *args: deseralize_bf_members(field),
            on_udf=lambda field, *args: self._deserialize_user_defined(field),
            on_df=lambda field, *args: self._deserialize_builtin(field, self.bStrVName),
        )
        self.dedent()
        return line + "\n"

    def _generate_message_serialization_helper(self, message):

        serialize_bf_members = lambda bf: "".join(
            f"{self.tab()}{self.bfBstrVName}.append(BitStream(uint=self.{self._field_name(field)}, length={field['count']}))\n"
            for field in bf["fields"]
        )

        line = f"{self.tab()}def serialize(self) -> bytes:\n"
        self.indent()
        line += f"{self.tab()}{self.bStrVName} = BitStream()\n"
        line += self._message_field_worker(
            message,
            on_bf_open=lambda field, *args: f"{self.tab()}{self.bfBstrVName} = BitStream()\n",
            on_bf_close=lambda field, *args: f"{self.tab()}{self.bStrVName}.append(self.reverse_bits({self.bfBstrVName}))\n",
            on_bf=lambda field, *args: serialize_bf_members(field),
            on_udf=lambda field, *args: self._serialize_user_defined(field),
            on_df=lambda field, *args: self._serialize_builtin(field, self.bStrVName),
        )
        line += f"{self.tab()}return {self.bStrVName}.bytes\n"
        self.dedent()
        return line + "\n"

    def _serialize_user_defined(self, field):
        line = ""
        name = self._field_name(field)
        count = self.get_count(field)
        if not is_number(count) or count != 1:
            line += f"{self.tab()}[bStr.append(BitArray(bytes={name}.serialize())) for {name} in self.{name}]\n"
        else:
            line = f"{self.tab()}bStr.append(BitArray(bytes=self.{name}.serialize()))\n"
        return line

    def _deserialize_user_defined(self, field):
        line = ""
        name = self._field_name(field)
        count = self.get_count(field)
        if not is_number(count) or count != 1:
            line += f"{self.tab()}[{name}.deserialize({self.bStrVName}) for {name} in self.{name}]\n"
        else:
            line = f"{self.tab()}self.{name}.deserialize({self.bStrVName})\n"
        return line

    def _deserialize_builtin(self, field, bStrVName):
        line = ""
        name = self._field_name(field)
        count = self.get_count(field)
        e_type = self.get_language_type(field)
        # bitfield case
        if e_type == BF:
            line = f"{self.tab()}self.{name} = {bStrVName}.read('uint:{count}')\n"
        # array case
        elif count != 1:
            line += f"{self.tab()}self.{name} = [{bStrVName}.read('{BUILTIN_TO_BIT_STRINGS[field['type']['name']]}') for _ in range({count})]\n"
        # single case
        else:
            line = f"{self.tab()}self.{name} = {bStrVName}.read('{BUILTIN_TO_BIT_STRINGS[field['type']['name']]}')\n"
        return line

    def _serialize_builtin(self, field, bStrVName):
        line = ""
        name = self._field_name(field)
        e_type = self.get_language_type(field)
        count = self.get_count(field)
        # bitfield case
        if e_type == BF:
            line = f"{self.tab()}{bStrVName}.append(BitStream(uint=self.{name}, length={count}))\n"
        # array case
        elif count != 1:
            line += f"{self.tab()}[{bStrVName}.append(BitStream(uint={name}, length={field['type'][BITLENGTH]})) for {name} in self.{name}]\n"
        # single case
        else:
            line = f"{self.tab()}{bStrVName}.append(BitStream(uint=self.{name}, length={field['type'][BITLENGTH]}))\n"
        return line

    def generate_source_files(self, output_dir, source_name=None):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        template_dir = os.path.join(this_dir, "..", "templates", "python")

        self._copy_template_file(
            f"{output_dir}/serializer", template_dir, "serializer.py"
        )

        with open(f"{output_dir}/{source_name}.py", "w") as f:
            f.write(self.generate())

    def _print_variable_declaration(self, field):
        # add variable
        name = self._field_name(field)
        count = self.get_count(field)
        e_type = self.get_language_type(field)

        line = f"{self.tab()}{name}: "
        if e_type != BF and (not is_number(count) or int(count) > 1):
            line += f"List['{e_type}']\n"
        else:
            line += f"'{e_type}'\n"

        # add docs
        line += (
            f'{self.tab()}"""{self.tab()}{field[DOC]}{self.tab()}"""\n'
            if DOC in field
            else ""
        )
        return line

    def _generate_message_initializer(self, message):
        line = f"{self.tab()}def __init__(self):\n"
        self.indent()
        for field in message["fields"]:
            name = self._field_name(field)
            count = self.get_count(field)
            e_type = self.get_language_type(field)
            dv = self.get_default_value(field)

            if e_type != BF and (not is_number(count) or int(count) > 1):
                line += f"{self.tab()}self.{name} = [{e_type}] * {count}\n"
            elif dv is not None:
                line += f"{self.tab()}self.{name} = {dv}\n"
            elif e_type not in BUILTIN_TO_PYTHON.keys():
                line += f"{self.tab()}self.{name} = {e_type}()\n"
            else:
                line += f"{self.tab()}self.{name} = {BUILTINS[e_type][DEFAULT_VALUE]}\n"
        self.dedent()
        return f"{line}\n\n"

    def _field_name(self, field):
        # needed so python doesn't mangle names with __
        name = field["name"]
        if field["name"][0:2] == "__":
            name = field["name"][1:]
        return name
