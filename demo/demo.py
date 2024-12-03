# =========================================================================
# THIS CODE HAS BEEN AUTOMATICALLY GENERATED USING 'message_serializer' TOOL
#       https://github.com/johnlevs/message_serializer
#       Generated on: #2024-12-02 20:58:39# 
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
from typing import List
from bitstring import BitArray, BitStream
from serializer.serializer import serializableMessage


class wordIds:
	LIGHTBULB__lightBulbStatusWord = 0
	LED__ledStatusWord = 1

class LIGHTBULB:
	class lightBulbStatusWord(serializableMessage):
		"""
		 contain the status of a light bul
			:param brightness: The brightness of the light bulb
			:type brightness: np.uint8
			:param colorR: The color of the light bulb
			:type colorR: np.uint8
			:param colorG: The color of the light bulb
			:type colorG: np.uint8
			:param colorB: The color of the light bulb
			:type colorB: np.uint8
			:param powerOn: The power state of the light bulb
			:type powerOn: np.uint8
			:param powerOff: The power state of the light bulb
			:type powerOff: np.uint8
			:param broken: True (1) if the light bulb is broken
			:type broken: np.uint8

 		"""
		"""############################################ USER DATA ############################################"""

		brightness: np.uint8
		"""		The brightness of the light bulb		"""
		colorR: np.uint8
		"""		The color of the light bulb		"""
		colorG: np.uint8
		"""		The color of the light bulb		"""
		colorB: np.uint8
		"""		The color of the light bulb		"""
		powerOn: np.uint8
		"""		The power state of the light bulb		"""
		powerOff: np.uint8
		"""		The power state of the light bulb		"""
		broken: np.uint8
		"""		True (1) if the light bulb is broken		"""
		"""########################################## SERIALIZATION ##########################################"""

		def __init__(self):
			self.brightness = 5
			self.colorR = np.uint8()
			self.colorG = np.uint8()
			self.colorB = np.uint8()
			self.powerOn = np.uint8()
			self.powerOff = np.uint8()
			self.broken = np.uint8()


		def serialize(self) -> bytes:
			bStr = BitStream()
			bStr.append(BitStream(uint=self.brightness, length=8))
			bStr.append(BitStream(uint=self.colorR, length=8))
			bStr.append(BitStream(uint=self.colorG, length=8))
			bStr.append(BitStream(uint=self.colorB, length=8))
			bStr.append(BitStream(uint=self.powerOn, length=8))
			bStr.append(BitStream(uint=self.powerOff, length=8))
			bStr.append(BitStream(uint=self.broken, length=8))
			return bStr.bytes

		def deserialize(self, byteArr):
			bStr = BitStream(bytes=byteArr)
			self.brightness = bStr.read('uintbe:8')
			self.colorR = bStr.read('uintbe:8')
			self.colorG = bStr.read('uintbe:8')
			self.colorB = bStr.read('uintbe:8')
			self.powerOn = bStr.read('uintbe:8')
			self.powerOff = bStr.read('uintbe:8')
			self.broken = bStr.read('uintbe:8')


	LIGHTBULB_COUNT: np.uint8 = 2


class LED:
	LED_COUNT: np.uint8 = LIGHTBULB.LIGHTBULB_COUNT


	class states:
		ON = 0
		OFF = 1


	class ledStatusWord(serializableMessage):
		"""
		 contain the status of a 20 led light stri
			:param lightStatuses: The status of each light bulb in the strip
			:type lightStatuses: LIGHTBULB.lightBulbStatusWord
			:param connectedToInternet: True (1) if the light bulb is connected to the internet
			:type connectedToInternet: np.uint8
			:param test:
			:type test: np.uint8

 		"""
		"""############################################ USER DATA ############################################"""

		lightStatuses: List['LIGHTBULB.lightBulbStatusWord']
		"""		The status of each light bulb in the strip		"""
		connectedToInternet: np.uint8
		"""		True (1) if the light bulb is connected to the internet		"""
		test: np.uint8
		"""########################################## SERIALIZATION ##########################################"""

		def __init__(self):
			self.lightStatuses = [LIGHTBULB.lightBulbStatusWord] * LED.LED_COUNT
			self.connectedToInternet = np.uint8()
			self.test = LED.states.OFF


		def serialize(self) -> bytes:
			bStr = BitStream()
			[bStr.append(BitArray(bytes=lightStatuses.serialize())) for lightStatuses in self.lightStatuses]
			bStr.append(BitStream(uint=self.connectedToInternet, length=8))
			bStr.append(BitStream(uint=self.test, length=8))
			return bStr.bytes

		def deserialize(self, byteArr):
			bStr = BitStream(bytes=byteArr)
			[lightStatuses.deserialize(bStr) for lightStatuses in self.lightStatuses]
			self.connectedToInternet = bStr.read('uintbe:8')
			self.test = bStr.read('uintbe:8')


