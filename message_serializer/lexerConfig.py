import numpy as np

CPPKEYWORDS = [
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
]

# define reserved tokens
MSGDEF = "MESSAGEDEF"
CONST = "CONST"
STATE = "STATE"

# define remaining tokens, and their respective token regexes
ID = "IDENTIFIER"
TYPE = "TYPE"
STRING = "STRING"
NUMBER = "NUMBER"
DOC = "DOC"
PW = "PW"

IDREG = r"[a-zA-Z_][a-zA-Z_0-9]*"
STRINGREG = r'"[^"]*"'
NUMBERREG = r"-?\d+(\.\d+)?"
DOCREG = r"-Doc"
PWREG = r"-PW"
SYNC = r"\n+|(\r\n)+"

BITLENGTH = "bitLength"
LEXERTYPE = "lexerType"
CPPTYPE = "cppType"
BUILTINS = {
    "uint8": {
        BITLENGTH: 8,
        CPPTYPE: "uint8_t",
        "max": np.iinfo(np.uint8).max,
        "min": np.iinfo(np.uint8).min,
    },
    "uint16": {
        BITLENGTH: 16,
        CPPTYPE: "uint16_t",
        "max": np.iinfo(np.uint16).max,
        "min": np.iinfo(np.uint16).min,
    },
    "uint32": {
        BITLENGTH: 32,
        CPPTYPE: "uint32_t",
        "max": np.iinfo(np.uint32).max,
        "min": np.iinfo(np.uint32).min,
    },
    "uint64": {
        BITLENGTH: 64,
        CPPTYPE: "uint64_t",
        "max": np.iinfo(np.uint64).max,
        "min": np.iinfo(np.uint64).min,
    },
    "int8": {
        BITLENGTH: 8,
        CPPTYPE: "int8_t",
        "max": np.iinfo(np.int8).max,
        "min": np.iinfo(np.int8).min,
    },
    "int16": {
        BITLENGTH: 16,
        CPPTYPE: "int16_t",
        "max": np.iinfo(np.int16).max,
        "min": np.iinfo(np.int16).min,
    },
    "int32": {
        BITLENGTH: 32,
        CPPTYPE: "int32_t",
        "max": np.iinfo(np.int32).max,
        "min": np.iinfo(np.int32).min,
    },
    "int64": {
        BITLENGTH: 64,
        CPPTYPE: "int64_t",
        "max": np.iinfo(np.int64).max,
        "min": np.iinfo(np.int64).min,
    },
    "float32": {
        BITLENGTH: 32,
        CPPTYPE: "float",
        "max": np.finfo(np.float32).max,
        "min": np.finfo(np.float32).min,
    },
    "float64": {
        BITLENGTH: 64,
        CPPTYPE: "double",
        "max": np.finfo(np.float64).max,
        "min": np.finfo(np.float64).min,
    },
    "bitfield": {
        BITLENGTH: 0,
        CPPTYPE: "_",
        "max": 0,
        "min": 0,
    },
}
