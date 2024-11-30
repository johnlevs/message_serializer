from abc import ABC, abstractmethod
from bitstring import BitStream

class serializableMessage(ABC):
    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @abstractmethod
    def deserialize(self, data) -> None:
        pass
    
    def reverse_bits(self, bits: BitStream) -> BitStream:
        """Reverses the bits of every byte in the bitstream."""
        reversed_bits = BitStream()
        for byte in bits.cut(8):
            reversed_bits.append(byte[::-1])
        return reversed_bits