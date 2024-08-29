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


from cpp_serializer.printable_element import PrintableElement
from cpp_serializer.module_list_element import Module_List_Element
from abc import abstractmethod


class ModuleElement(PrintableElement):
    """
    Represents a base class for module elements.
    """

    name: str = ""
    type: str = ""
    parent: "Module_List_Element"

    def __init__(self, name: str, type: str, parent: "Module_List_Element" = None):
        self.name = name
        self.parent = parent
        self.type = type

    @abstractmethod
    def get_docs(self) -> str:
        """
        Retrieves the documentation for the module element.

        Returns:
            str: The documentation for the module element.
        """
        pass

    @abstractmethod
    def containsParam(self, param: str) -> bool:
        """
        Check if the module element contains a parameter.

        Args:
            param (str): The parameter to check for.

        Returns:
            bool: True if the module element contains the parameter, False otherwise.
        """
        pass
