from cpp_serializer.printable_element import PrintableElement, abstractmethod


class Module_List_Element(PrintableElement):
    parent = None
    moduleName: str

    def __init__(self, parent, name):
        self.parent = parent
        self.moduleName = name

    @abstractmethod
    def get_module_name(self) -> str:
        """
        Returns the name of the module that the element belongs to.

        Returns:
            str: The name of the module.
        """
        pass

    