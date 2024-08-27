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
