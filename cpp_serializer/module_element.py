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
