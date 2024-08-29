# MIT License

# Copyright (c) 2024 johnlevs

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


MSGDEFSTRT: str = "messageDef"
MSGNAME: str = "messageName"
MSGDEFEND: str = "endMessageDef"
MSGFLGS: str = "messageFlags"
MSGDOC: str = "messageDoc"

PARAMFLAGS: str = "parameterFlags"
PARAMNAME: str = "paramName"
PARAMDOC: str = "paramDoc"
PARAMSIZEBITS: str = "paramSizeBits"
PARAMBITWORD: str = "paramBitWord"
ALOWTYPESSTR: str = "allowableTypes"
TYPE: str = "type"
BITLENGTH: str = "bitLength"
CPPTYPE: str = "cppType"
CPPKEYWORDS: str = "cppKeywords"

config: dict = {
    ALOWTYPESSTR: {
        "uint8": {BITLENGTH: 8, CPPTYPE: "uint8_t"},
        "uint16": {BITLENGTH: 16, CPPTYPE: "uint16_t"},
        "uint32": {BITLENGTH: 32, CPPTYPE: "uint32_t"},
        "uint64": {BITLENGTH: 64, CPPTYPE: "uint64_t"},
        "int8": {BITLENGTH: 8, CPPTYPE: "int8_t"},
        "int16": {BITLENGTH: 16, CPPTYPE: "int16_t"},
        "int32": {BITLENGTH: 32, CPPTYPE: "int32_t"},
        "int64": {BITLENGTH: 64, CPPTYPE: "int64_t"},
        "float32": {BITLENGTH: 32, CPPTYPE: "float"},
        "float64": {BITLENGTH: 64, CPPTYPE: "double"},
        "bitfield": {BITLENGTH: 0, CPPTYPE: "_"},
    },
    CPPKEYWORDS: {
        "alignas",
        "alignof",
        "and",
        "and_eq",
        "asm",
        "atomic_cancel",
        "atomic_commit",
        "atomic_noexcept",
        "auto",
        "bitand",
        "bitor",
        "bool",
        "break",
        "case",
        "catch",
        "char",
        "char8_t",
        "char16_t",
        "char32_t",
        "class",
        "compl",
        "concept",
        "const",
        "consteval",
        "constexpr",
        "constinit",
        "const_cast",
        "continue",
        "co_await",
        "co_return",
        "co_yield",
        "decltype",
        "default",
        "delete",
        "do",
        "double",
        "dynamic_cast",
        "else",
        "enum",
        "explicit",
        "export",
        "extern",
        "false",
        "float",
        "for",
        "friend",
        "goto",
        "if",
        "inline",
        "int",
        "long",
        "mutable",
        "namespace",
        "new",
        "noexcept",
        "not",
        "not_eq",
        "nullptr",
        "operator",
        "or",
        "or_eq",
        "private",
        "protected",
        "public",
        "register",
        "reinterpret_cast",
        "requires",
        "return",
        "short",
        "signed",
        "sizeof",
        "static",
        "static_assert",
        "static_cast",
        "struct",
        "switch",
        "synchronized",
        "template",
        "this",
        "thread_local",
        "throw",
        "true",
        "try",
        "typedef",
        "typeid",
        "typename",
        "union",
        "unsigned",
        "using",
        "virtual",
        "void",
        "volatile",
        "wchar_t",
        "while",
        "xor",
        "xor_eq",
    },
    MSGDEFSTRT: "MESSAGEDEF",
    MSGDEFEND: "ENDMESSAGEDEF",
    MSGFLGS: {MSGDOC: "-Doc"},
    PARAMFLAGS: {PARAMBITWORD: "-PW", PARAMDOC: "-Doc"},
}


def get_smallest_bitfield_type(size) -> tuple:
    """
    Returns the smallest bitfield type that can accommodate the given size.

    Args:
        size (int): The size of the bitfield.

    Returns:
        tuple: A tuple containing the bit length and C++ type of the smallest bitfield type.
               If no suitable type is found, returns (None, None).
    """
    for key in config[ALOWTYPESSTR]:
        if config[ALOWTYPESSTR][key][BITLENGTH] >= size:
            return (
                config[ALOWTYPESSTR][key][BITLENGTH],
                config[ALOWTYPESSTR][key][CPPTYPE],
            )
    return None, None


def cpp_type(string: str) -> str:
    """
    Returns the C++ type of the given string.

    Args:
        string (str): The string to be checked.

    Returns:
        str: The C++ type of the given string.
    """
    if type_is_valid(string):
        return config[ALOWTYPESSTR][string][CPPTYPE]
    return None


def type_is_valid(type: str) -> bool:
    """
    Check if the given type is valid.

    Args:
        type (str): The type to be checked.

    Returns:
        bool: True if the type is valid, False otherwise.
    """
    return type in config[ALOWTYPESSTR]


def name_is_valid(name: str) -> bool:
    """
    Check if the given name is valid.

    Args:
        name (str): The name to be checked.

    Returns:
        bool: True if the name is valid, False otherwise.
    """
    return name not in config[CPPKEYWORDS] and name not in [T[CPPTYPE] for T in config[ALOWTYPESSTR].values()]


def get_input_type(cppType):
    """
    Returns the input type of the given C++ type.
    """
    for key in config[ALOWTYPESSTR]:
        if config[ALOWTYPESSTR][key][CPPTYPE] == cppType:
            return key
    return None
