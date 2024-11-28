from message_serializer.generator import Generator, logger
from message_serializer.cpp_config import *
from message_serializer.parser import is_number
import os


def is_cpp_reserved_keywords(name):
    return name in CPPKEYWORDS


class CppGenerator(Generator):
    NAME = "message"
    SOURCE_FILE_NAME = f"{NAME}.cpp"
    HEADER_FILE_NAME = f"{NAME}.h"

    def __init__(
        self,
        ast,
    ):
        self.inlineCommentChar = "//"
        self.messageList = []
        super().__init__(ast)

    def generate(self, source_name=None):
        if source_name is None:
            source_name = self.NAME

        lic = self.get_license() + "\n"
        includeGuard = (
            f"#ifndef _{source_name.upper()}_H_\n"
            f"#define _{source_name.upper()}_H_\n\n"
        )
        includes = '#include "serializer/serializer.h"\n\n' "#include <stdint.h>\n\n"

        self.indent()

        modules = ""
        for module in self.tree.tree:
            modules += self._generate_module(module)
        # needs to be called after all messages are generated
        wordIDs = self._generate_wordIDList(self.messageList) + "\n"
        max_size_constant = self._get_max_message_size()

        self.dedent()

        headerFile = (
            lic
            + includeGuard
            + includes
            + f"namespace {source_name.upper()} {{\n"
            + wordIDs
            + modules
            + max_size_constant
            + "} // namespace icd\n\n"
            + f"#endif\t//_{source_name.upper()}_H_\n\n"
        )

        serializers = ""
        for module in self.tree.tree:
            module_impl = ""
            for message in module["messages"]:
                module_impl += (
                    f"{self.tab()}int {source_name.upper()}::{module['name']}::"
                    + self._generate_message_serialization(message)
                    + "\n"
                )
                module_impl += (
                    f"{self.tab()}int {source_name.upper()}::{module['name']}::"
                    + self._generate_message_deserialization(message)
                    + "\n"
                )

            serializers += module_impl

        impl_includes = f'#include "{source_name}.h"\n\n'
        implementationFile = lic + impl_includes + serializers

        return headerFile, implementationFile

    def generate_source_files(self, output_dir, source_name=None):
        # copy template files
        if source_name is None:
            source_name = self.NAME

        logger.info(f"Copying C++ template files to {output_dir}")

        this_dir = os.path.dirname(os.path.realpath(__file__))
        template_dir = os.path.join(this_dir, "..", "templates", "cpp")

        self._copy_template_file(
            f"{output_dir}/serializer", template_dir, "serializer.h"
        )
        self._copy_template_file(
            f"{output_dir}/serializer", template_dir, "serializer.cpp"
        )

        # generate code
        logger.info(f"Generating C++ Source files...")
        header, impl = self.generate(source_name)
        with open(output_dir + "/" + source_name + ".h", "w") as f:
            f.write(header)
        logger.debug(f"Generated " + output_dir + "/" + source_name + ".h")
        with open(output_dir + "/" + source_name + ".cpp", "w") as f:
            f.write(impl)
        logger.debug(f"Generated " + output_dir + "/" + source_name + ".cpp")

    def _generate_message(self, message, module):
        line = (
            self.tab() + f"struct {message['name']} : public serializableMessage" " {\n"
        )
        docTab = self.tab()
        self.indent()
        line += (
            self.tab()
            + "/******************************************** USER DATA ********************************************/\n\n"
        )
        # bit field parameters
        bfOpen = False
        prevBFname = None
        bfSize = 0

        tempDoc = message[DOC] if DOC in message.keys() else ""
        tempDoc = tempDoc.replace('"', "")
        docString = f"{docTab}/**\n{docTab}* @brief {tempDoc}\n"

        for field in message["fields"]:
            tempDoc = field[DOC] if DOC in field.keys() else ""
            tempDoc = tempDoc.replace('"', "")
            docString += f"{docTab}* @param {field['name']} {tempDoc}\n"
            if field["type"] == BF and not bfOpen:
                prevBFname = field[PW]
                bfOpen = True
                line += self._open_bitField()
            elif field["type"] != BF and bfOpen:
                bfOpen = False
                bfSize = 0
                line += self._close_bitfield(bfSize, prevBFname)
                prevBFname = None
            elif PW in field.keys() and field[PW] != prevBFname and bfOpen:
                line += self._close_bitfield(bfSize, prevBFname)
                line += self._open_bitField()
                bfSize = 0
                prevBFname = field[PW]

            if bfOpen:
                bfSize += int(field["count"])

            # print variable
            line += self.tab() + self._print_variable(field) + "\n"
        docString += f"{docTab}*/\n"

        if bfOpen:
            line += self._close_bitfield(bfSize, prevBFname)
            prevBFname = field[PW]

        # print serialization stuff
        line += (
            self.tab()
            + "/******************************************** SERIALIZATION ********************************************/\n\n"
        )
        # message size parameter
        line += self.tab() + "static constexpr uint16_t SIZE = "
        prevBFname = None
        for field in message["fields"]:
            if field["type"] == BF:
                if prevBFname != field[PW]:
                    line += f"sizeof({field[PW]}) + "
                prevBFname = field[PW]
            elif field["type"] in BUILTINS.keys():
                line += f"sizeof({field['name']}) + "
            else:
                scope = self.tree.find_member(field["type"])
                line += f"{scope[0][0]}::{field['type']}::SIZE "
                if field["count"] != 1:
                    line += f"* {field['count']} "
                line += "+ "
        line += "0;\n"
        line += (
            self.tab()
            + f"static constexpr wordIDs WORDID = wordIDs::"
            + self.messageNameToWordID(f"{module['name']}::{message['name']};\n")
        )

        # serialization
        line += f"{self.tab()}int serialize(uint8_t *buffer) override;\n"
        line += f"{self.tab()}int deserialize(uint8_t *buffer) override;\n"

        self.dedent()
        line += self.tab() + "};"
        return docString + line

    def _generate_enum(self, enum):
        line = self.tab() + f"enum {enum['name']} " "{\n"
        self.indent()
        for field in enum["fields"]:
            line += self.tab() + f"{field['name']}"
            if field["default_value"] is not None:
                line += f" = {field['default_value']}"
            line += ","
            if DOC in field.keys():
                line += f"\t\t// {field[DOC][1:-1]}"
            line += "\n"
        self.dedent()
        line += self.tab() + "};" + f" // enum {enum['name']}\n\n"
        return line

    def _generate_constants(self, constant):
        resolvedType = (
            BUILTIN_TO_CPP[constant["type"]]
            if constant["type"] in BUILTIN_TO_CPP.keys()
            else constant["type"]
        )
        line = (
            self.tab()
            + f"constexpr {resolvedType} {constant['name']} = {constant['default_value']};"
        )
        if DOC in constant.keys():
            line += f"\t// {constant[DOC][1:-1]}"
        return line + "\n"

    def _generate_module(self, module):
        line = self.tab() + f"namespace {module['name']} " "{\n"
        self.indent()
        for constant in module["constants"]:
            line += self._generate_constants(constant) + "\n"
        for enum in module["states"]:
            line += self._generate_enum(enum) + "\n"
        for message in module["messages"]:
            line += self._generate_message(message, module) + "\n"
            self.messageList.append(f"{module['name']}::{message['name']}")

        self.dedent()
        line += self.tab() + "};" + f" // namespace {module['name']}"
        return line + "\n\n"

    def _generate_message_deserialization(self, message):
        return self._generate_message_serialization_helper(message, serialize=False)

    def _generate_message_serialization(self, message):
        return self._generate_message_serialization_helper(message, serialize=True)

    """
    ===============================================================================
                                    HELPERS
    ===============================================================================
    """

    def _generate_wordIDList(self, messageList):
        wordIDs = self.tab() + "enum class wordIDs " "{\n"
        self.indent()
        for message in messageList:
            wordIDs += self.tab() + f"{self.messageNameToWordID(message)},\n"
        wordIDs += "\n"
        wordIDs += self.tab() + "WORDID_COUNT,\n"
        wordIDs += self.tab() + "INVALID_WORDID = 0xFFFF\n"
        self.dedent()
        wordIDs += self.tab() + "};\n"
        return wordIDs

    def messageNameToWordID(self, messageName):
        return messageName.replace(":", "_").upper()

    def _generate_message_serialization_helper(self, message, serialize=True):
        if serialize:
            line = f"{message['name']}::serialize(uint8_t *buffer) " + "\n{\n"
        else:
            line = f"{message['name']}::deserialize(uint8_t *buffer) " + "\n{\n"

        self.indent()
        line += self.tab() + f"uint8_t* itr = buffer;\n"

        line += self._message_field_worker(
            message=message,
            on_udf=lambda field: self._serialize_parameter(field, serialize),
            on_df=lambda field: self._serialize_parameter(field, serialize),
        )

        line += self.tab() + "return itr - buffer;\n"
        self.dedent()
        line += self.tab() + "}\n\n"
        return line

    def _serialize_parameter(self, field, serialize=True):
        hton_call = "HTON"
        function_hton_call = "serialize"
        if not serialize:
            hton_call = "NTOH"
            function_hton_call = "deserialize"

        line = ""
        if field["count"] != 1:
            line += self.tab() + f"for(int i = 0; i < {field['count']}; i++) " "{\n"
            self.indent()

        if field["type"] in BUILTIN_TO_CPP.keys():
            if field["count"] == 1:
                line += f"{self.tab()}{hton_call}(&{field['name']}, itr, sizeof({field['name']}));\n"
            else:
                line += f"{self.tab()}{hton_call}({field['name']}, itr, sizeof({field['name']}[0]));\n"

        else:
            line += self.tab() + f"itr += {field['name']}"
            if field["count"] != 1:
                line += "[i]"
            line += f".{function_hton_call}(itr);\n"

        if field["count"] != 1:
            self.dedent()
            line += self.tab() + "}\n"

        return line

    def _print_variable(self, field):

        if field["type"] == BF:
            resolvedType = U8CPP
            for key in CPP_TO_BUILTINS.keys():
                if CPP_TO_BUILTINS[key]["bitLength"] < int(field["count"]):
                    continue
                resolvedType = key
                break
            if CPP_TO_BUILTINS[resolvedType]["bitLength"] < int(field["count"]):
                raise Exception(
                    f"Field {field['name']} is too large for type {resolvedType}"
                )
        elif field["type"] in BUILTIN_TO_CPP.keys():
            resolvedType = BUILTIN_TO_CPP[field["type"]]
        else:
            logger.debug("Resolving type for " + field["type"])
            member = self.tree.find_member(field["type"])
            resolvedType = member[0][0] + "::"
            if member[2] is not None:
                resolvedType += (
                    +self.tree.tree[member[0][1]][member[1][1]]["name"] + "::"
                )
            resolvedType += field["type"]

        string = f"{resolvedType} {field['name']}"
        if field["type"] == BF:
            string += f" : {field['count']}"
        elif not is_number(field["count"]) or int(field["count"]) > 1:
            string += f"[{field['count']}]"

        # add default value & docstring if available
        if "default_value" in field.keys() and field["default_value"] is not None:
            if is_number(field["default_value"]):
                string += f" = {field['default_value']}"
            else:
                # get default value scope
                logger.debug(f"Searching for default value of {field['default_value']}")
                member = self.tree.find_member(field["default_value"])
                if member is None:
                    string += f" = {field['default_value']}"
                else:
                    hierarchy = (
                        self.tree.tree[member[0][1]]["name"]
                        + "::"
                        + self.tree.tree[member[0][1]][member[1][0]][member[1][1]][
                            "name"
                        ]
                    )
                    if len(member) == 3 and member[2] is not None:
                        hierarchy += "::" + field["default_value"]
                    string += f" = {hierarchy}"

        string += ";"

        if DOC in field.keys():
            string += f"\t// {field[DOC][1:-1]}"
        return string

    def _close_bitfield(self, bfSize, bfName):
        # first determine the type needed for the parameter to union the bitfield with

        resolvedType = CPP_TO_BUILTINS[U8CPP]
        for key in BUILTIN_TO_CPP.keys():
            if CPP_TO_BUILTINS[BUILTIN_TO_CPP[key]]["bitLength"] < bfSize:
                continue
            resolvedType = key
            break

        param = {
            "type": resolvedType,
            "name": bfName,
            "count": 1,
        }
        # use byte array in this case
        if CPP_TO_BUILTINS[BUILTIN_TO_CPP[key]]["bitLength"] < bfSize:
            param["type"] = U8
            param["count"] = bfSize // 8

        self.dedent()
        line = self.tab() + "};\n"
        line += self.tab() + self._print_variable(param) + "\n"
        self.dedent()
        line += self.tab() + "};\n"
        return line

    def _open_bitField(self):
        line = self.tab() + "union {\n"
        self.indent()
        line += self.tab() + "struct {\n"
        self.indent()

        return line

    def _get_max_message_size(self):
        max_size_constant = (
            f"{self.tab()}constexpr uint16_t __max_message_size()\n"
            + self.tab()
            + "{\n"
        )
        self.indent()
        max_size_constant += f"{self.tab()}uint16_t max = 0;\n"
        for message in self.messageList:
            max_size_constant += (
                self.tab() + f"max = ({message}::SIZE > max) ? {message}::SIZE : max;\n"
            )
        max_size_constant += f"{self.tab()}return max;\n"
        self.dedent()
        max_size_constant += f"{self.tab()}" + "}\n\n"
        max_size_constant += f"{self.tab()}constexpr uint16_t MAX_MESSAGE_SIZE = __max_message_size();\n\n"
        return max_size_constant
