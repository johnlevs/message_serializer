# Message Serializer

## Usage

To use this tool, run message_serizlizer.py in the commandline. Arguments are needed to direct the script towards the configuration files, where the messages are defined.

```bash
python.exe message_serializer.py -I <input_dir> -O <output_dir> [-L <output language> (optional)]
```

Currently the only output language supported is C++.

### Building the .ICD file:

The tool supports three type:

- Constants
- Enums/States
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
MSG <message name> -Doc [message documenation (optional)] {
    <paramName> <paramType> [= <default_value> (optional)]  [-Doc "paramComment / documenation" (optional)]
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
- U16
- U32
- U64
- f32
- F64

#### Arrays/Bitfields

arrays may be defined as such, and can only be defined as members of messages in the paramType field:

```ini
<paramType>[<arraySize>]
```

bitfields are defined in a simliar manner to arrays, and can only be memebers of messages:

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
- Any bitfield parameters that exceed 64 bits are thrown out with a warning

#### References

references to other messages may be made by using the message name as the paramType and long as they are defined in the scope of the files passed to the ICDBuilder
