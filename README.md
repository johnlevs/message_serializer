# Message Serializer

## Usage

To use this tool, run message_serializer.py in the commandline. Arguments are needed to direct the script towards the configuration files, where the messages are defined.

```bash
python.exe message_serializer.py <input_dir> <output_dir> <output_file_name(s)> [-L <output language> (optional)]
```

Currently the only output languages supported are C++ and python.

### Building the .ICD file:

The tool supports three type:

- Constants
- Enumerated values (referred to as states)
- Messages

Constants & States are constant values that would typically be defined at compile time in a program. Messages are structures in the program that a user would want to translate to byte arrays. The tool automatically generates the code to serialize each field in a message to network byte ordering, and then de-serialize it back. The generated code would be useful when sending data packets over a network.

#### Constants

Constants may be generated as such:

```ini
CONSTANT <constant name> <constant type> = <constant value>
```

Constants may be used as default values and array size initializers

#### States

States (enums) may be defined as such:

```ini
STATE <state name> {
    <state value>
    .
    .
}
```

States may be used as default values and array size initializers
A message may be defined as such:

```ini
MSG <message name> -Doc [message documentation (optional)] {
    <paramName> <paramType> [= <default_value> (optional)]  [-Doc "paramComment / documentation" (optional)]
    .
    .
}
```

#### Types

Valid default types are as follows:

- i8
- i16
- i32
- i64
- u8
- u16
- u32
- u64
- f32
- f64

#### Arrays

arrays may be defined as such, and can only be defined as members of messages in the paramType field:

```ini
<paramType>[<arraySize>]
```

<!--
bitfields are defined in a similar manner to arrays, and can only be members of messages:

```ini
bitfield[<size>] [-PW <bitfield Name> -Doc "docstring" (optional)]
```

were size represents the number of bits in the bitfield parameter.

##### Some notes on bitfields:

Bitfields follow these rules when being generated:

- The name of the first bitfield in a message will be generated or defined by the user
- Adjacent bitfield parameters with no name will share the previous name until a
  new unique bitfield name is defined, thus creating a new separate bitfield
  (adjacent parameters with the same DEFINED name will be considered part of the same bitfield)
- If a bitfield name is defined, it must be unique in the message and will throw an error if it is not
- If a bitfield name is not defined, it will be generated and be unique in the message

Some other notes:

- If the size is not specified, the parameter will be assumed to be a single bit
- BitFields are defined as a union of a struct containing the bitfield and a single integer (or array of bytes), containing the bitfield as a whole.
- Any bitfields that exceed 64 are union'd with the smallest possible byte array that can contain the bitfield.
- Any bitfield parameters that exceed 64 bits are thrown out with a warning -->

#### References

references to other messages may be made by using the message name as the paramType and long as they are defined in the scope of the files passed to the ICDBuilder

## Example:

### File Setup

An two example .icd files can be found in the `demo` folder. The example is a little rough around the edges but it supposed to show how you might define different elements.

- led.icd
- lightbulb.icd

#### lightbulb.icd

This file defines a `lightBulbStatusWord` struct. You can see the member definitions below:

```ini
MSG lightBulbStatusWord                         -Doc "I contain the status of a light bulb" 
{
    brightness u8          = 5                  -Doc "The brightness of the light bulb"
    colorR u8                                -Doc "The color of the light bulb"
    colorG u8                                -Doc "The color of the light bulb"
    colorB u8                                -Doc "The color of the light bulb"
    powerOn u8                              -Doc  "The power state of the light bulb" 
    powerOff u8                             -Doc "The power state of the light bulb" 
    broken u8                               -Doc "True (1) if the light bulb is broken" 
}
```

#### led.icd

led.icd defines a few things:

- A constant `LED_COUNT` set to a value of 2, with a byte size of 1 byte
- A List of states, `ON` and `OFF`
- A Message containing an array of the previously defined `lightbulbStatusWord`

```ini
CONSTANT LED_COUNT u8 = 2

MSG ledStatusWord                                       -Doc "I contain the status of a 20 led light strip"
{
    lightStatuses lightBulbStatusWord[LED_COUNT]        -Doc "The status of each light bulb in the strip"
    connectedToInternet u8                               -Doc "True (1) if the light bulb is connected to the internet"
    test u8 = OFF
}

STATE states{
    ON
    OFF
}
```

### Code Generation

Running:

```bash
python.exe message_serialize.py demo demo message -L cpp
```

Will scan the `demo` directory for `.icd` files and produce the following files (again in the `demo` directory):

- message.h
- message.cpp

`States` get converted to `enums`, and constants are converted to `constexpr`. The Message is converted to a struct. Each file exists in it's own namespace to avoid naming conflicts. Here is what led.icd generates:

```cpp
namespace TEST {
	enum class wordIDs {
		LED__LEDSTATUSWORD,
		LIGHTBULB__LIGHTBULBSTATUSWORD,

		WORDID_COUNT,
		INVALID_WORDID = 0xFFFF
	};

	namespace LED {
		constexpr uint8_t LED_COUNT = 2;

		enum states {
			ON,
			OFF,
		}; // enum states


		/**
		* @brief I contain the status of a 20 led light strip
		* @param lightStatuses The status of each light bulb in the strip
		* @param connectedToInternet True (1) if the light bulb is connected to the internet
		* @param test
		*/
		struct ledStatusWord : public serializableMessage {
			/******************************************** USER DATA ********************************************/

			LIGHTBULB::lightBulbStatusWord lightStatuses[LED_COUNT];	// The status of each light bulb in the strip
			uint8_t connectedToInternet;	// True (1) if the light bulb is connected to the internet
			uint8_t test = LED::states::OFF;
			/******************************************** SERIALIZATION ********************************************/

			static constexpr uint16_t SIZE = LIGHTBULB::lightBulbStatusWord::SIZE * LED_COUNT + sizeof(connectedToInternet) + sizeof(test) + 0;
			static constexpr wordIDs WORDID = wordIDs::LED__LEDSTATUSWORD;
			int serialize(uint8_t *buffer) override;
			int deserialize(uint8_t *buffer) override;
		};
	}; // namespace LED
    .
    .
    .

	constexpr uint16_t __max_message_size()
	{
		uint16_t max = 0;
		max = (LED::ledStatusWord::SIZE > max) ? LED::ledStatusWord::SIZE : max;
		max = (LIGHTBULB::lightBulbStatusWord::SIZE > max) ? LIGHTBULB::lightBulbStatusWord::SIZE : max;
		return max;
	}

	constexpr uint16_t MAX_MESSAGE_SIZE = __max_message_size();

}; // namespace TEST
```

A few extra field are added:

- `SIZE` is a constant value which contains the actual size of an equivalent byte array containing all the field data. (sum of the size of all the fields, excludes any padding, ect...)
- `wordID` returns an enumerated value of the word ID. Those are defined at the top of the header file (see below). WordIds are prefixed with the namespace to avoid conflicts due to the global scope.
- `MAX_MESSAGE_SIZE` is a constant defined in the global message namespace which contains the max size in bytes of all the messages processed.

```cpp
    enum class wordIDs {
		LED__LEDSTATUSWORD,
		LIGHTBULB__LIGHTBULBSTATUSWORD,

		WORDID_COUNT,
		INVALID_WORDID = 0xFFFF
	};
```

The `serialize()` and `deserialize()` methods are defined in the `message.cpp` file:

```cpp
int TEST::LED::ledStatusWord::serialize(uint8_t *buffer)
{
	uint8_t* itr = buffer;
	for(int i = 0; i < LED_COUNT; i++) {
		itr += lightStatuses[i].serialize(itr);
	}
	HTON(&connectedToInternet, itr, sizeof(connectedToInternet));
	HTON(&test, itr, sizeof(test));
	return itr - buffer;
}


int TEST::LED::ledStatusWord::deserialize(uint8_t *buffer)
{
	uint8_t* itr = buffer;
	for(int i = 0; i < LED_COUNT; i++) {
		itr += lightStatuses[i].deserialize(itr);
	}
	NTOH(&connectedToInternet, itr, sizeof(connectedToInternet));
	NTOH(&test, itr, sizeof(test));
	return itr - buffer;
}

```

For reference, here is the equivalent generated python code:

```python


class wordIds:
	LED_LEDSTATUSWORD = 0
	LIGHTBULB_LIGHTBULBSTATUSWORD = 1

class LED:

	LED_COUNT: np.uint8 = 2

	class states:
		ON = 0
		OFF = 1

	class ledStatusWord(serializableMessage):
		"""
		I contain the status of a 20 led light strip
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
		"""		"""
		"""########################################## SERIALIZATION ##########################################"""

		def __init__(self):
			self.lightStatuses = [LIGHTBULB.lightBulbStatusWord() for _ in range(LED.LED_COUNT)]
			self.test = LED.states.OFF

		def serialize(self) -> bytes:
			bStr = BitStream()
			for i in range(LED.LED_COUNT):
				bStr.append(BitArray(bytes=self.lightStatuses[i].serialize()))
			bStr.append(BitStream(uint=self.connectedToInternet, length=8))
			bStr.append(BitStream(uint=self.test, length=8))
			return bStr.bytes

		def deserialize(self, byteArr):
			bStr = BitStream(bytes=byteArr)
			for i in range(LED.LED_COUNT):
				self.lightStatuses[i].deserialize(bStr)
			self.connectedToInternet = bStr.read('uintbe:8')
			self.test = bStr.read('uintbe:8')
```
