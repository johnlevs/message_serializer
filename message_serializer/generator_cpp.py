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
        self.scope_combine_function = lambda higher, lower: f"{higher}::{lower}"
        self.inlineCommentChar = "//"
        super().__init__(
            ast,
            inlineCommentChar="//",
            scope_combine_function=lambda higher, lower: f"{higher}::{lower}",
            type_lookup=BUILTIN_TO_CPP,
        )

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
        # for module in self.ast_tree.tree:
        #     modules += self._generate_module(module)
        # needs to be called after all messages are generated
        modules += self._generate_module_members(self.ast_tree.print_order_iterator())

        wordIDs = self._generate_wordIDList() + "\n"
        max_size_constant = self._get_max_message_size()
        message_generator = f"{self.tab()}serializableMessage *newMessage(wordIDs id);\n";
        self.dedent()

        headerFile = (
            lic
            + includeGuard
            + includes
            + f"namespace {source_name.upper()} {{\n"
            + wordIDs
            + modules
            + max_size_constant
            + message_generator
            + f"}} // namespace {source_name.upper()}\n\n"
            + f"#endif\t//_{source_name.upper()}_H_\n\n"
        )

        serializers = ""
        for message in self.ast_tree.message_iterator():
            module = message["parent"]
            serializers += (
                f"{self.tab()}int {source_name.upper()}::{module['name']}::"
                + self._generate_message_serialization(message)
                + "\n"
            )
            serializers += (
                f"{self.tab()}int {source_name.upper()}::{module['name']}::"
                + self._generate_message_deserialization(message)
                + "\n"
            )

        impl_includes = f'#include "{source_name}.h"\n\n'
        implementationFile = lic + impl_includes + self._generate_message_generator_func(source_name.upper()) + serializers

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

    def _generate_message(self, message):
        module = message["parent"]

            
        # declaration
        line = (
            self.tab() + f"struct {message['name']} : public serializableMessage" " {\n"
        )
        docTab = self.tab()
        self.indent()
        
        #constructor
        word_id = f"wordIDs::{self.msg_2_wordID(message)}"
        line += f"{self.tab()}{message['name']}() : serializableMessage((int){word_id}) {{}}\n"
        
        line += (
            self.tab()
            + "/******************************************** USER DATA ********************************************/\n\n"
        )

        printVar = lambda field, *args: f"{self.tab()}{self._print_variable_declaration(field)}\n"
        line += self._message_field_worker(
            message=message,
            on_bf_open=lambda field, *args: self._open_bitField(),
            on_bf_close=lambda field, bf_name, bf_size: self._close_bitfield(
                bf_size, bf_name
            ),
            on_bf=printVar,
            on_udf=printVar,
            on_df=printVar,
        )

        tempDoc = message[DOC] if DOC in message.keys() else ""
        tempDoc = tempDoc.replace('"', "")
        docString = f"{docTab}/**\n{docTab}* @brief {tempDoc}\n"

        for field in message["fields"]:
            tempDoc = field[DOC] if DOC in field.keys() else ""
            tempDoc = tempDoc.replace('"', "")
            docString += f"{docTab}* @param {field['name']} {tempDoc}\n"
        docString += f"{docTab}*/\n"

        # print serialization stuff
        line += (
            self.tab()
            + "/******************************************** SERIALIZATION ********************************************/\n\n"
        )
        # message size parameter
        line += self.tab() + f"static constexpr uint16_t SIZE = "
        on_udf_lambda = lambda field, *args: (
            f"{self.msg_name_w_scope(field['type'])}::SIZE "
            + (
                f" * {self.msg_name_w_scope(field['count'])}"
                if field["count"] != 1
                else ""
            )
            + " + "
        )
        line += self._message_field_worker(
            message=message,
            on_bf_open=lambda field, *args: f"sizeof({field[PW]}) + ",
            on_df=lambda field, *args: f"sizeof({field['name']}) + ",
            on_udf=on_udf_lambda,
        )
        line += "0;\n"

        # serialization
        line += f"{self.tab()}int serialize(uint8_t *buffer) override;\n"
        line += f"{self.tab()}int deserialize(uint8_t *buffer) override;\n"

        self.dedent()
        line += self.tab() + "};\n"
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
        line = f"{self.tab()}constexpr {self._print_variable_declaration(constant)}"  # semi-colon is added in print_variable
        if DOC in constant.keys():
            line += f"\t// {constant[DOC][1:-1]}"
        return line + "\n"

    def _generate_module_members(self, print_list):
        generators = {
            "MSG": self._generate_message,
            STATE: self._generate_enum,
            CONST: self._generate_constants,
        }
        line = ""
        moduleName = None
        newName = None
        for element in print_list:
            e_type = self.ast_tree.get_type(element)
            generator = (
                generators[CONST] if e_type in BUILTINS.keys() else generators[e_type]
            )
            newName = self.get_module_name(element)
            if moduleName != newName:
                if moduleName is not None:
                    self.dedent()
                    line += f"{self.tab()}}}; // namespace {moduleName}\n\n"

                line += f"{self.tab()}namespace {newName} {{\n"
                self.indent()
                moduleName = newName
            line += f"{generator(element)}\n"
        if moduleName is not None:
            self.dedent()
            line += f"{self.tab()}}}; // namespace {moduleName}\n\n"
        return line

    def _generate_message_deserialization(self, message):
        return self._generate_message_serialization_helper(message, serialize=False)

    def _generate_message_serialization(self, message):
        return self._generate_message_serialization_helper(message, serialize=True)

    """
    ===============================================================================
                                    HELPERS
    ===============================================================================
    """

    def _generate_wordIDList(self):
        wordIDs = self.tab() + "enum class wordIDs " "{\n"
        self.indent()
        for message in self.ast_tree.message_iterator():
            wordIDs += self.tab() + f"{self.msg_2_wordID(message)},\n"
        wordIDs += "\n"
        wordIDs += self.tab() + "WORDID_COUNT,\n"
        wordIDs += self.tab() + "INVALID_WORDID = 0xFFFF\n"
        self.dedent()
        wordIDs += self.tab() + "};\n"
        return wordIDs

    def _generate_message_serialization_helper(self, message, serialize=True):
        if serialize:
            line = f"{message['name']}::serialize(uint8_t *buffer) " + "\n{\n"
        else:
            line = f"{message['name']}::deserialize(uint8_t *buffer) " + "\n{\n"

        self.indent()
        line += self.tab() + f"uint8_t* itr = buffer;\n"

        line += self._message_field_worker(
            message=message,
            on_udf=lambda field, *args: self._serialize_parameter(field, serialize),
            on_df=lambda field, *args: self._serialize_parameter(field, serialize),
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
        count = self.get_count(field)
        if count != 1:
            line += self.tab() + f"for(int i = 0; i < {count}; i++) " "{\n"
            self.indent()

        if self.get_language_type(field) in CPP_TO_BUILTINS.keys():
            if count == 1:
                line += f"{self.tab()}{hton_call}(&{field['name']}, itr, sizeof({field['name']}));\n"
            else:
                line += f"{self.tab()}{hton_call}({field['name']}, itr, sizeof({field['name']}[0]));\n"
        else:
            line += self.tab() + f"itr += {field['name']}"
            if count != 1:
                line += "[i]"
            line += f".{function_hton_call}(itr);\n"

        if count != 1:
            self.dedent()
            line += self.tab() + "}\n"

        return line

    def _print_variable_declaration(self, field):
        string = f"{self.get_language_type(field)} {field['name']}"

        # add count / array size / bitfield size if necessary
        count = self.get_count(field)
        if self.ast_tree.get_type(field) == BF:
            string += f" : {count}"
        elif not is_number(count) or int(count) > 1:
            string += f"[{count}]"

        # add default value & docstring if available
        if "default_value" in field and field["default_value"] is not None:
            string += f" = {self.get_default_value(field)}"

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
            "count": "1",
        }
        # use byte array in this case
        if CPP_TO_BUILTINS[BUILTIN_TO_CPP[key]]["bitLength"] < bfSize:
            param["type"] = U8
            param["count"] = f"{bfSize // 8}"

        self.dedent()
        line = self.tab() + "};\n"
        line += self.tab() + self._print_variable_declaration(param) + "\n"
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
        for message in self.ast_tree.message_iterator():
            name = self.msg_name_w_scope(message)
            max_size_constant += (
                self.tab() + f"max = ({name}::SIZE > max) ? {name}::SIZE : max;\n"
            )
        max_size_constant += f"{self.tab()}return max;\n"
        self.dedent()
        max_size_constant += f"{self.tab()}" + "}\n\n"
        max_size_constant += f"{self.tab()}constexpr uint16_t MAX_MESSAGE_SIZE = __max_message_size();\n\n"
        return max_size_constant

    def _generate_message_generator_func(self, source_name):
        line = f"{self.tab()}serializableMessage *{source_name}::newMessage(wordIDs id)\n{self.tab()}{{\n"
        self.indent();
        line += f"{self.tab()}switch (id) {{\n"
        for message in self.ast_tree.message_iterator():
            line += f"{self.tab()}case wordIDs::{self.msg_2_wordID(message)}:\n"
            self.indent();
            line += f"{self.tab()}return new {self.get_module_name(message)}::{message['name']}();\n"
            self.dedent();
        line += f"{self.tab()}}}\n"
        line += f"{self.tab()}return nullptr;\n"
        self.dedent();
        line += f"{self.tab()}}}\n\n";
        return line