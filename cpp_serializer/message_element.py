from cpp_serializer.printable_element import PrintableElement
from cpp_serializer.module_element import ModuleElement
from abc import abstractmethod


class MessageElement(PrintableElement):
    """
    Represents a base class for message elements.
    """

    name: str = ""
    type: str = ""
    parent = ["ModuleElement"]  # this is a reference to a strcutre that contains this element
    moduleReference = None      # this is a reference to a module which defines said element

    def __init__(self, name: str, type: str, parent: "ModuleElement" = None):
        self.name = name
        self.parent = parent
        self.type = type

    @abstractmethod
    def get_docs(self) -> str:
        """
        Retrieves the documentation for the message element.

        Returns:
            str: The documentation for the message element.
        """
        pass

    @abstractmethod
    def containsParam(self, param: str) -> bool:
        """
        Check if the message element contains a parameter.

        Args:
            param (str): The parameter to check for.

        Returns:
            bool: True if the message element contains the parameter, False otherwise.
        """
        pass


    @abstractmethod
    def add_module_reference(self, module: "ModuleElement") -> None:
        """
        Adds a module reference to the message element.

        Args:
            module (ModuleElement): The module to add.

        Returns:
            None
        """
        pass

    