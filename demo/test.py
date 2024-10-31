# =========================================================================
# THIS CODE HAS BEEN AUTOMATICALLY GENERATED USING 'message_serializer' TOOL
#       https://github.com/johnlevs/message_serializer
#       Generated on: #2024-10-31 02:05:40# 
# =========================================================================
# MIT License
# 
# Copyright (c) 2024 johnlevs
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import numpy as np
import bitstring
from serializer.serializer import serializableMessage


class LED:
	LED_COUNT: np.uint8 = 2

	class states:
		ON = 0
		OFF = 1

	class ledStatusWord(serializableMessage):
		"""############################################ USER DATA ############################################"""

		lightStatuses: list['LIGHTBULB.lightBulbStatusWord']
		connectedToInternet: np.int8
		__ledStatusWord_pad_0: np.int8
		test: np.uint8
		"""########################################## SERIALIZATION ##########################################"""

		def __init__(self):
			self.lightStatuses = [LIGHTBULB.lightBulbStatusWord() for _ in range(LED.LED_COUNT)]
			self.test = LED.states.OFF

		def serialize(self) -> bytes:
			bitstream = bitstring.BitStream()
			for i in range(LED.LED_COUNT):
				bitstream.append(bitstring.BitArray(bytes=self.lightStatuses[i].serialize()))
			bitstream.append(bitstring.BitStream(uint=self.connectedToInternet, length=1))
			bitstream.append(bitstring.BitStream(uint=self.__ledStatusWord_pad_0, length=7))
			bitstream.append(bitstring.BitStream(uint=self.test, length=8))
			return bitstream.bytes

		def deserialize(self, bitstream: bitstring.BitStream):
			for i in range(LED.LED_COUNT):
				self.lightStatuses[i].deserialize(bitstream)
			self.connectedToInternet = bitstream.read('uint:1')
			self.__ledStatusWord_pad_0 = bitstream.read('uint:7')
			self.test = bitstream.read('uint:8')


class LIGHTBULB:
	class lightBulbStatusWord(serializableMessage):
		"""############################################ USER DATA ############################################"""

		brightness: np.uint8
		colorR: np.uint8
		colorG: np.uint8
		colorB: np.uint8
		powerOn: np.int8
		powerOff: np.int8
		broken: np.int8
		__lightBulbStatusWord_pad_0: np.int8
		"""########################################## SERIALIZATION ##########################################"""

		def __init__(self):
			self.brightness = 5

		def serialize(self) -> bytes:
			bitstream = bitstring.BitStream()
			bitstream.append(bitstring.BitStream(uint=self.brightness, length=8))
			bitstream.append(bitstring.BitStream(uint=self.colorR, length=8))
			bitstream.append(bitstring.BitStream(uint=self.colorG, length=8))
			bitstream.append(bitstring.BitStream(uint=self.colorB, length=8))
			bitstream.append(bitstring.BitStream(uint=self.powerOn, length=1))
			bitstream.append(bitstring.BitStream(uint=self.powerOff, length=3))
			bitstream.append(bitstring.BitStream(uint=self.broken, length=1))
			bitstream.append(bitstring.BitStream(uint=self.__lightBulbStatusWord_pad_0, length=3))
			return bitstream.bytes

		def deserialize(self, bitstream: bitstring.BitStream):
			self.brightness = bitstream.read('uint:8')
			self.colorR = bitstream.read('uint:8')
			self.colorG = bitstream.read('uint:8')
			self.colorB = bitstream.read('uint:8')
			self.powerOn = bitstream.read('uint:1')
			self.powerOff = bitstream.read('uint:3')
			self.broken = bitstream.read('uint:1')
			self.__lightBulbStatusWord_pad_0 = bitstream.read('uint:3')


