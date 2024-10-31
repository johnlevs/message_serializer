from abc import ABC, abstractmethod

class serializableMessage(ABC):
    @abstractmethod
    def serialize(self) -> bytes:
        pass

    def deserialize(self, data) -> None:
        pass