from message_serializer.ast import ast
from message_serializer.generator import Generator, logger
from message_serializer.python_config import *
from message_serializer.parser import is_number


class pythonGenerator(Generator):
    def __init__(self, tree: ast):
        self.inlineCommentChar = "#"
        super().__init__(tree)

    def generate(self):

        imports = [
            "import numpy as np",
            "import bitstring",
            "from serializer.serializer import serializableMessage",
        ]
        importStr = "\n".join(imports) + "\n\n\n"

        modules = ""
        for module in self.tree.tree:
            modules += self._generate_module(module)

        return self.get_license() + importStr + modules

    def _generate_message(self, message):
        line = f"{self.tab()}class {message['name']}" + "(serializableMessage):\n"
        self.indent()
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
        line = f"{self.tab()}def deserialize(self, bitstream: bitstring.BitStream):\n"
        self.indent()
        for field in message["fields"]:
            if field["type"] in BUILTINS.keys():
                line += self._deserialize_builtin(field)
            else:
                line += self._deserialize_user_defined(field)
        self.dedent()
        return line + "\n"

    def _generate_message_serialization_helper(self, message):
        # cases to check for:
        # 1. built-in type
        # 2. user-defined type
        line = f"{self.tab()}def serialize(self) -> bytes:\n"
        self.indent()
        line += f"{self.tab()}bitstream = bitstring.BitStream()\n"
        for field in message["fields"]:
            if field["type"] in BUILTINS.keys():
                line += self._serialize_builtin(field)
            else:
                line += self._serialize_user_defined(field)
        line += f"{self.tab()}return bitstream.bytes\n"
        self.dedent()
        return line + "\n"

    def _serialize_user_defined(self, field):
        if not is_number(field["count"]) or field["count"] > 1:
            count = self.retrieve_constant_hierarchy(field["count"])
            line = f"{self.tab()}for i in range({count}):\n"
            self.indent()
            line += f"{self.tab()}bitstream.append(bitstring.BitArray(bytes=self.{field['name']}[i].serialize()))\n"
            self.dedent()
        else:
            line = f"{self.tab()}bitstream.append(bitstring.BitArray(bytes=self.{field['name']}.serialize()))\n"
        return line

    def _deserialize_user_defined(self, field):
        if not is_number(field["count"]) or field["count"] > 1:
            count = self.retrieve_constant_hierarchy(field["count"])
            line = f"{self.tab()}for i in range({count}):\n"
            self.indent()
            line += f"{self.tab()}self.{field['name']}[i].deserialize(bitstream)\n"
            self.dedent()
        else:
            line = f"{self.tab()}self.{field['name']}.deserialize(bitstream)\n"
        return line

    def _deserialize_builtin(self, field):
        # bitfield case
        if field["type"] == BF:
            line = f"{self.tab()}self.{field['name']} = bitstream.read('uint:{field['count']}')\n"
        # array case
        elif field["count"] > 1:
            line = f"{self.tab()}for i in range({field['count']}):\n"
            self.indent()
            line += f"{self.tab()}self.{field['name']}[i] = bitstream.read('{BUILTIN_TO_BIT_STRINGS[field['type']]}')\n"
            self.dedent()
        # single case
        else:
            line = f"{self.tab()}self.{field['name']} = bitstream.read('{BUILTIN_TO_BIT_STRINGS[field['type']]}')\n"
        return line

    def _serialize_builtin(self, field):
        # bitfield case
        if field["type"] == BF:
            line = f"{self.tab()}bitstream.append(bitstring.BitStream(uint=self.{field['name']}, length={field['count']}))\n"
        # array case
        elif field["count"] > 1:
            line = f"{self.tab()}for i in range({field['count']}):\n"
            self.tab()
            line += f"{self.tab()}bitstream.append(bitstring.BitStream(uint=self.{field['name']}[i], length={BUILTINS[field['type']][BITLENGTH]}))\n"
            self.dedent()
        # single case
        else:
            line = f"{self.tab()}bitstream.append(bitstring.BitStream(uint=self.{field['name']}, length={BUILTINS[field['type']][BITLENGTH]}))\n"
        return line

    def _generate_message_deserialization(self, message):
        pass

    def generate_source_files(self, output_dir, source_name=None):
        self._copy_template_file(
            f"{output_dir}/serializer", "templates/python", "serializer.py"
        )

        with open(f"{output_dir}/{source_name}.py", "w") as f:
            f.write(self.generate())

    def _print_variable(self, field):
        line = f"{self.tab()}{field['name']}: "
        if field["type"] != BF and (
                not is_number(field["count"]) or int(field["count"]) > 1
            ):
            line += f"list['{self.get_type(field)}']\n"
        else:
            line += f"{self.get_type(field)}\n"
        # determine type
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
