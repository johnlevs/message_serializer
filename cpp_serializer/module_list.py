from cpp_serializer.module_list_element import Module_List_Element
from cpp_serializer.module import Module
from cpp_serializer.message_printer import MessagePrinter

from typing import List
import os


class module_list:
    directory: str
    name: str
    modules = List["Module_List_Element"]
    modulePaths = None

    def __init__(self, directory, name):
        self.directory = directory
        self.name = name
        self.modules = []

    def get_name(self) -> str:
        return self.name

    def scan_directory(self, directory="") -> List[str]:
        """
        Recursively scans the ICD directory for module files.
        Returns:
            List[str]: A list of module file paths.

        """
        if directory == "":
            directory = self.directory

        module_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".icd"):
                    module_files.append((os.path.join(root, file), file[:-4]))
        self.modulePaths = module_files

    def get_messages(self) -> List["Module_List_Element"]:
        """
        Returns a list of all the messages in the ICD.
        """
        return [message for module in self.modules for message in module.get_messages()]

    def load_modules(self):
        """
        Loads the modules from the module files.
        """

        for path, moduleName in self.modulePaths:
            module = Module(str(moduleName), self)
            module.loadConfig(path)
            self.modules.append(module)

        for module in self.modules:
            module.validatemsgs(self.get_messages())

    def generate_cpp(self, target_directory):

        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        self._generate_header_files(target_directory)
        self._generate_source_files(target_directory)

        pass

    def get_module_hierarchy(self) -> List[str]:
        """
        Returns a list of the module hierarchy.

        Returns:
            List[str]: A list of module names.
        """
        return [self.name]

    def _generate_source_files(self, target_directory):
        """
        Generates the source files for the ICD.
        """
        if not os.path.exists(target_directory + "/serializer"):
            os.makedirs(target_directory + "/serializer")
        self._copy_serializer_files(target_directory + "/serializer")

        with open(os.path.join(target_directory, "message.cpp"), "w") as f:
            self._copy_license(target_directory, f)
            f.write(MessagePrinter.newlines(1))

            f.write("#include \"message.h\"\n")
            f.write(MessagePrinter.newlines(1))
            f.write('#include "serializer/serializer.h"\n')
            f.write(MessagePrinter.newlines(1))
            f.write("using namespace " + self.name + ";\n")

            for module in self.modules:
                f.write(MessagePrinter.newlines(1))
                string = module.to_cpp_serialize_implimentation_string()
                f.write(string)

            f.write(MessagePrinter.newlines(1))
            f.write(self.max_size())

    def _copy_serializer_files(self, target_directory):
        """
        Copies the tempalted files to the target directory.
        """
        for root, _, files in os.walk("cpp_templates/serializer"):
            for file in files:
                with open(os.path.join(root, file), "r") as f:
                    with open(os.path.join(target_directory, file), "w") as f2:
                        f2.write(f.read())

    def _copy_license(self, target_directory, file):
        """
        Copies the liscense file to the target directory.
        """
        with open("LICENSE", "r") as f:
            line = f.readline()
            while line:
                file.write(MessagePrinter.inlineComment(line.replace("\n", "")))
                line = f.readline()
        file.write(MessagePrinter.newlines(2))

    def _generate_header_files(self, target_directory):
        """
        Generates the message file.
        """
        with open(os.path.join(target_directory, "message.h"), "w") as f:
            self._copy_license(target_directory, f)
            f.write(MessagePrinter.startHeaderGuard(self.name))

            f.write(MessagePrinter.newlines(2))
            f.write("#include <stdint.h>\n")

            f.write(MessagePrinter.newlines(2))
            if self.name != "":
                f.write(MessagePrinter.startModule(self.name))

            self.print_wordIds_to_file(f)

            self.print_abstract_message_class(f)

            f.write(MessagePrinter.newlines(1))
            for module in self.modules:
                string = module.to_cpp_string();
                f.write(MessagePrinter.newlines(1))
                f.write(string)

            f.write(MessagePrinter.newlines(1))
            if self.name != "":
                f.write(MessagePrinter.endModule())

            f.write(MessagePrinter.newlines(1))
            f.write(MessagePrinter.endHeaderGuard(self.name))

    def print_abstract_message_class(self, f):
        f.write(MessagePrinter.newlines(1))
        with open("cpp_templates/genericMessage", "r") as f2:
            line = f2.readline()
            while line:
                f.write(MessagePrinter.tab() + line)
                line = f2.readline()

    def print_wordIds_to_file(self, f):
        messages = self.get_messages()

        f.write(MessagePrinter.startEnumMessageList("wordIds"))

        for msg in messages:
            f.write(MessagePrinter.printEnumMessageList(msg.name.upper()))

        f.write(MessagePrinter.endEnumMessageList())

        f.write(MessagePrinter.newlines(1))

    def max_size(self):
        string = "\n\n"
        string += MessagePrinter.startMaxSizeFunction()
        for msg in self.get_messages():
            string += msg.to_cpp_max_size()
        string += MessagePrinter.endMaxSizeFunction()
        return string
