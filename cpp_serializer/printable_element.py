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


from abc import ABC, abstractmethod


class PrintableElement(ABC):
    @abstractmethod
    def to_cpp_string(self) -> str:
        """
        Converts the message element to a C++ string representation. Meant to print information for a header file.

        Returns:
            str: The C++ string representation of the message element.
        """
        pass

    @abstractmethod
    def to_cpp_serialize_implimentation_string(self) -> str:
        """
        Generates the C++ implementation string for serializing the message element. Meant to print implimentation code.

        Returns:
            str: The C++ implementation string for serialization.
        """
        pass

    @abstractmethod
    def to_cpp_deserialize_implimentation_string(self) -> str:
        """
        Generates the C++ implementation string for deserializing the message element. Meant to print implimentation code.

        Returns:
            str: The C++ implementation string for deserialization.
        """
        pass
