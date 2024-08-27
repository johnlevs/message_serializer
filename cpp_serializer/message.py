from typing import List
import argparse
import shlex


from cpp_serializer.message_defs import *
from cpp_serializer.message_printer import MessagePrinter
from cpp_serializer.message_bit_field import (
    MessageBitField,
    MessageParameter,
    MessageElement,
)
from cpp_serializer.module_element import ModuleElement


class Message(ModuleElement):
    unamedStructCount: int = 0
    lastParamWasBit: bool = False
    params: List["MessageElement"]
    # arg parser
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        config[MSGFLGS][MSGDOC], type=str, help="Documentation for the message"
    )
    args: argparse.Namespace
    nextOpenName: str = "reserved"

    def __init__(self, line, parent=None):
        args = shlex.split(line)
        if len(args) < 2:
            return

        self.args = self.parser.parse_args(args[2:])
        self.params = []

        super().__init__(args[1], args[1], parent)

    def add_param(self, param: MessageParameter) -> None:
        """
        Adds a parameter to the message.

        Args:
            param (messageParameter): The parameter to add.

        Returns:
            None

        """

        param.name = self.make_unique_param_name(param.name)

        if param.is_bit_field():

            bfExists, bf = self._bitfield_should_take_param(param)

            if bfExists:
                bf.add_param(param)
            else:
                name = self.make_unique_param_name(self.nextOpenName)
                if param.args.PW is not None:
                    name = self.make_unique_param_name(param.args.PW)

                bf = MessageBitField(name, self)
                bf.add_param(param)
                self.params.append(bf)
            self.lastParamWasBit = True
            return

        if self.lastParamWasBit:
            self.lastParamWasBit = False
            self.unamedStructCount += 1

        self.params.append(param)

    def make_unique_param_name(self, name):
        if self.containsParam(name):
            nameCounter = 0
            newname = name
            while self.containsParam(newname):
                nameCounter += 1
                newname = name + "_" + str(nameCounter)
            print(
                f"Warning: Parameter {name} already exists in message {self.name}. Incrementing name to {newname}."
            )
            return newname
        return name

    def _bitfield_should_take_param(self, param: MessageParameter) -> bool:
        for p in reversed(self.params):
            if isinstance(p, MessageBitField) and (
                p.name == param.args.PW
                or (param.args.PW == None and self.lastParamWasBit)
            ):
                return True, p
        return False, None

    def removeInvalidParameters(self, messageNames) -> None:
        """
        Removes invalid parameters from the list of parameters.

        Parameters:
        - messageNames: A list of valid message names.

        Returns:
        None
        """
        self.params = [
            param
            for param in self.params
            if type_is_valid(param.type)
            or param.type in [message.name for message in messageNames]
        ]
        for param in self.params:
            if isinstance(param, MessageBitField):
                continue
            if param.type in [message.name for message in messageNames]:
                module = [
                    module for module in messageNames if module.name == param.type
                ]
                param.add_module_reference(module[0])

    def to_enum_string(self) -> str:
        """Generate the C++ enum string representation of the message."""
        return MessagePrinter.printEnumMessageList(self.name.upper())

    def to_cpp_max_size(self) -> str:
        """Generate the C++ max size string representation of the message."""
        return MessagePrinter.maxSizeFunctionParam(self.name, self.get_module_name())

    """ abstract methods """

    def to_cpp_string(self) -> str:
        """Generate the C++ struct string representation of the message."""
        string = self.get_docs()
        string += MessagePrinter.startMessage(self.name)
        string += MessagePrinter.inlineComment(
            "==================== START USER DEFINED STRUCT ==================="
        )
        # print params
        for param in self.params:
            string += param.to_cpp_string()

        string += MessagePrinter.inlineComment(
            "====================== END USER DEFINED STRUCT ==================="
        )

        # print messageSize variable
        string += "\n\n"
        string += MessagePrinter.startMessageSize()
        for param in self.params:
            cppType = cpp_type(param.type)

            if not cppType is None or cppType == "_":
                string += MessagePrinter.paramSize(param.name) + " + "
            else:
                string += (
                    MessagePrinter.messageSize(
                        param.type, param.moduleReference.get_module_hierarchy()
                    )
                    + " + "
                )
        string += "0;\n"
        string += MessagePrinter.endMessage(self.name.upper())

        return string

    def to_cpp_serialize_implimentation_string(self) -> str:
        """
        Returns a string representing the implementation of the C++ serialization function for the message.

        This function iterates over the parameters of the message and calls their respective
        `to_cpp_serialize_implimentation_string` methods to generate the serialization code.

        Returns:
            A string representing the implementation of the C++ serialization function.
        """

        string = MessagePrinter.startSerializeFunction(
            self.name, self.get_module_name()
        )
        for param in self.params:
            string += param.to_cpp_serialize_implimentation_string()

        string += MessagePrinter.endSerializeFunction()

        return string

    def to_cpp_deserialize_implimentation_string(self) -> str:

        string = MessagePrinter.startDeserializeFunction(
            self.name, self.get_module_name()
        )
        for param in self.params:
            string += param.to_cpp_deserialize_implimentation_string()

        string += MessagePrinter.endDeserializeFunction()
        return string

    def get_docs(self):
        """Get the documentation string for the message."""
        docString = self.args.Doc if self.args.Doc != None else ""
        docs = MessagePrinter.startMessageDoc(docString, self.name)
        for param in self.params:
            if isinstance(param, MessageBitField):
                docs += param.get_docs()
            else:
                doc = param.get_docs()
                docs += MessagePrinter.printParameterDoc(doc, param.name)

        docs += MessagePrinter.endMessageDoc()

        return docs

    def containsParam(self, paramName: str) -> bool:
        return any([p.containsParam(paramName) for p in self.params])

    def get_module_hierarchy(self) -> List[str]:
        return self.parent.get_module_hierarchy()

    def get_module_name(self) -> str:
        return self.parent.get_module_name()
