# MIT License

# Copyright (c) 2024 johnlevs

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import List

from cpp_serializer.module_element import ModuleElement
from cpp_serializer.message_defs import *
from cpp_serializer.message_printer import MessagePrinter
from cpp_serializer.message_parameter import MessageParameter, MessageElement


class MessageBitField(MessageElement):
    size: int
    params: List["MessageParameter"]

    def __init__(self, name: str, parent) -> None:
        """
        Initialize the messageBitField object.

        :param name: The name of the bitfield.
        """
        self.name = name
        self.type = "bitfield"
        self.size = 0
        self.params = []

        super().__init__(name, self.type, parent)

    def add_param(self, param: MessageParameter) -> None:
        """
        Add a parameter to the bitfield.

        :param param: The parameter to add.
        """
        self.size += param.bit_size()
        self.params.append(param)

    """ abstract methods"""

    def to_cpp_string(self) -> str:
        """
        Generate the C++ string representation of the bitfield.

        :return: The C++ string representation.
        """

        # add the reserved bit field, if necessary
        size, wordType = get_smallest_bitfield_type(self.size)

        if size == None or wordType == None:
            print("Warning: Bitfield size too large, using byte array for union type")
            size = self.size
            while size % MessagePrinter._SMALLEST_FIELD_SIZE != 0:
                size += 1
            wordType = get_smallest_bitfield_type(MessagePrinter._SMALLEST_FIELD_SIZE)[
                1
            ]

        if size > self.size:
            # add reserved bit field
            reservedParamToAdd = MessageParameter(
                self.parent.make_unique_param_name("reserved") + " bitfield"
            )
            reservedParamToAdd.count = size - self.size
            self.add_param(reservedParamToAdd)

        # print out the bitfield
        string = MessagePrinter.startBitField()
        for param in self.params:
            string += MessagePrinter.printBitFieldParam(
                param.to_cpp_string_no_tabs(), param.bit_size(), param.get_docs()
            )

        # add the variable which can be used to access the bitfield as a whole
        param = MessageParameter(self.name + " " + get_input_type(wordType), "")
        param.count = size // MessagePrinter._SMALLEST_FIELD_SIZE
        string += MessagePrinter.endBitField(param.to_cpp_string_no_tabs())
        return string

    def to_cpp_serialize_implimentation_string(self) -> str:
        """
        Generate the C++ serialization implementation string.

        :return: The C++ serialization implementation string.
        """
        _, count = self._calculate_bits_and_count()
        return MessagePrinter.serializeParameter(self.name, count)

    def to_cpp_deserialize_implimentation_string(self) -> str:
        """
        Generate the C++ deserialization implementation string.

        :return: The C++ deserialization implementation string.
        """
        _, count = self._calculate_bits_and_count()
        return MessagePrinter.deserializeParameter(self.name, count)

    def get_docs(self) -> str:
        """
        Generate the documentation string for the bitfield.

        :return: The documentation string.
        """
        docString = ""
        for param in self.params:
            docString += MessagePrinter.printParameterDoc(param.get_docs(), param.name)

        return docString

    def containsParam(self, param: str) -> bool:
        return self.name == param or any([p.containsParam(param) for p in self.params])

    """ private methods """

    def _calculate_bits_and_count(self) -> tuple:
        """
        Calculate the bits and count for serialization/deserialization.

        :return: A tuple of bits and count.
        """
        bits = get_smallest_bitfield_type(self.size)[0]
        if bits == None:
            bits = self.size
            while bits % MessagePrinter._SMALLEST_FIELD_SIZE != 0:
                bits += 1

        count = (
            bits // MessagePrinter._SMALLEST_FIELD_SIZE
            if bits // MessagePrinter._SMALLEST_FIELD_SIZE
            > MessagePrinter._SMALLEST_FIELD_SIZE
            else 1
        )
        return bits, count

    def get_module_name(self) -> str:
        return super().get_module_name()

    def add_module_reference(self, module: ModuleElement) -> None:
        pass
