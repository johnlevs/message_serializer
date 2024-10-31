from message_serializer.lexerConfig import *


U8PY = "np.uint8"
U16PY = "np.uint16"
U32PY = "np.uint32"
U64PY = "np.uint64"
I8PY = "np.int8"
I16PY = "np.int16"
I32PY = "np.int32"
I64PY = "np.int64"
F32PY = "np.float32"
F64PY = "np.float64"
BFPY = "np.int8"


PYTHON_TO_BUILTINS = {
    U8PY: BUILTINS[U8],
    U16PY: BUILTINS[U16],
    U32PY: BUILTINS[U32],
    U64PY: BUILTINS[U64],
    I8PY: BUILTINS[I8],
    I16PY: BUILTINS[I16],
    I32PY: BUILTINS[I32],
    I64PY: BUILTINS[I64],
    F32PY: BUILTINS[F32],
    F64PY: BUILTINS[F64],
}

BUILTIN_TO_BIT_STRINGS = {
    U8: "uint:8",
    U16: "uint:16",
    U32: "uint:32",
    U64: "uint:64",
    I8: "int:8",
    I16: "int:16",
    I32: "int:32",
    I64: "int:64",
    F32: "float:32",
    F64: "float:64",
}

BUILTIN_TO_PYTHON = {
    U8: U8PY,
    U16: U16PY,
    U32: U32PY,
    U64: U64PY,
    I8: I8PY,
    I16: I16PY,
    I32: I32PY,
    I64: I64PY,
    F32: F32PY,
    F64: F64PY,
    BF: BFPY,
}

PYTHON_KEYWORDS = [
    "False",
    "None",
    "True",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
]