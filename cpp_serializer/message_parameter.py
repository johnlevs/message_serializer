import argparse
import shlex
import re

from cpp_serializer.message_defs import *
from cpp_serializer.message_printer import MessagePrinter
from cpp_serializer.message_element import MessageElement
from cpp_serializer.module_element import ModuleElement


class MessageParameter(MessageElement):
    """
    Represents a message parameter.

    Attributes:
        parser (argparse.ArgumentParser): The argument parser.
        args (argparse.Namespace): The parsed arguments.
        init (bool): Flag indicating if the object is initialized.
        count (int): The size of the parameter, if greater than 1, it indicates an array.
        name (str): The name of the parameter.
        type (str): The type of the parameter.
    """

    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        config[PARAMFLAGS][PARAMBITWORD],
        type=str,
        help="Larger Word for the parameter if it is a bitfield. If not a bitfield, this will be ignored.",
    )
    parser.add_argument(
        config[PARAMFLAGS][PARAMDOC],
        type=str,
        help="Documentation for the parameter",
    )
    args: argparse.Namespace
    init: bool = False
    count: int = 1

    def __init__(self, argString, allTypesValid=False, parent=None):
        """
        Initialize the MessageParam object.

        :param argString: The argument string to parse.
        :param allTypesValid: Flag to allow all types as valid.
        """

        # check if the argString is valid
        if argString is None:
            return

        args = shlex.split(argString)
        if len(args) < 2:
            print(
                "Warning: Invalid parameter string: "
                + argString
                + "Parameter will be ignored"
            )
            return

        if not type_is_valid(args[1]) and not allTypesValid:
            print(
                "Warning: Param '"
                + args[0]
                + "' has an invalid type '"
                + args[1]
                + "'. It will be ignored."
            )
            return

        # assign the name and type

        self.name = args[0]
        self.type = args[1]

        # check for name validity
        if not self.name.isidentifier():
            print(
                "Warning: Param '"
                + self.name
                + "' is not a valid identifier. It will be ignored."
            )
            self.init = False
            return
        elif not name_is_valid(self.name):
            print(
                "Warning: Param '"
                + self.name
                + "' is a reserved keyword. It will be ignored."
            )
            self.init = False
            return
        # check for array/bitfield types
        match = re.search(r"\[(\d+)\]$", self.type)
        if match:
            if int(match.group(1)) < 1:
                print(
                    "Warning: Param '"
                    + self.name
                    + "' has an invalid array size. It will be excluded."
                )
                return
            else:
                self.count = int(match.group(1))
                self.type = self.type[: match.start()]
        elif "[" in self.type or "]" in self.type:
            print(
                "Warning: Param '"
                + self.name
                + f"' has an invalid array size/syntax ({self.type}). It will be excluded."
            )
            return
        if self.is_bit_field() and self.count > 64:
            print(
                "Warning: Param '"
                + self.name
                + f"' has an invalid bit size ({self.count} > 64). It will be excluded."
            )
            return

        self.init = True
        # parse optional arguments
        try:
            self.args = self.parser.parse_args(args[2:])
        except SystemExit:
            print(
                "Warning: Param '"
                + self.name
                + "' has invalid optional arguments. It will be excluded."
            )
            self.init = False

        super().__init__(self.name, self.type, parent)

    def to_cpp_string_no_tabs(self, nameSpace=None) -> str:
        """
        Convert the parameter to a C++ string representation without tabs.

        Returns:
            str: The C++ string representation of the parameter without tabs.
        """
        if type_is_valid(self.type):
            finalType = config[ALOWTYPESSTR][self.type][CPPTYPE]
            if self.is_bit_field():
                _, finalType = get_smallest_bitfield_type(self.bit_size())

        else:
            finalType = self.type

        if nameSpace is not None:
            prefix = ""
            for ns in nameSpace:
                prefix += ns + "::"
            finalType = prefix + finalType

        if self.count == 1 or self.is_bit_field():
            return finalType + " " + self.name + ";"

        return finalType + " " + self.name + "[" + str(self.count) + "];"

    def is_bit_field(self) -> bool:
        """
        Check if the parameter is a bit field.

        Returns:
            bool: True if the parameter is a bit field, False otherwise.
        """
        return type_is_valid(self.type) and self.type == "bitfield"

    def bit_size(self) -> int:
        """
        Get the bit size of the parameter.

        Returns:
            int: The bit size of the parameter.
        """
        if self.is_bit_field():
            return self.count

        return config[ALOWTYPESSTR][self.type][BITLENGTH]

    """ override methods """

    def get_docs(self) -> str:
        """
        Get the documentation for the parameter.

        Returns:
            str: The documentation for the parameter.
        """
        if self.args.Doc is None:
            return ""

        return self.args.Doc

    def to_cpp_string(self) -> str:
        """
        Convert the parameter to a C++ string representation.

        Returns:
            str: The C++ string representation of the parameter.
        """

        moduleList = None
        if self.moduleReference != None:
            moduleList = self.moduleReference.get_module_hierarchy()
        
        string = self.to_cpp_string_no_tabs(moduleList)

        if self.is_bit_field():
            return MessagePrinter.printBitFieldParam(
                string, self.bit_size(), self.get_docs()
            )

        return MessagePrinter.printParam(string, self.get_docs())

    def to_cpp_serialize_implimentation_string(self):
        """
        Convert the parameter to a C++ string representation for serialization.

        Returns:
            str: The C++ string representation of the parameter for serialization.
        """
        if not type_is_valid(self.type):
            return MessagePrinter.serializeMessageCall(self.name)
        return MessagePrinter.serializeParameter(self.name, self.count)

    def to_cpp_deserialize_implimentation_string(self):
        """
        Convert the parameter to a C++ string representation for deserialization.

        Returns:
            str: The C++ string representation of the parameter for deserialization.
        """
        return MessagePrinter.deserializeParameter(self.name, self.count)

    def containsParam(self, param: str) -> bool:
        return self.name == param

    def get_module_name(self) -> str:
        return self.parent.get_module_name()

    def add_module_reference(self, module: ModuleElement) -> None:
        self.moduleReference = module
