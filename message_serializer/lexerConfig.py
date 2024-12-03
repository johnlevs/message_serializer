import numpy as np


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


""" Define builtin types """
BITLENGTH = "bitLength"
U8 = "u8"
U16 = "u16"
U32 = "u32"
U64 = "u64"
I8 = "i8"
I16 = "i16"
I32 = "i32"
I64 = "i64"
F32 = "f32"
F64 = "f64"
BF = "bitfield"
STATEFIELD = "stateField"

INT_TYPES = [U8, U16, U32, U64, I8, I16, I32, I64]
FLOAT_TYPES = [F32, F64]
DEFAULT_VALUE = "defaultValue"

BUILTINS = {
    U8: {
        "name": U8,
        BITLENGTH: 8,
        "max": np.iinfo(np.uint8).max,
        "min": np.iinfo(np.uint8).min,
        DEFAULT_VALUE: 0,
    },
    U16: {
        "name": U16,
        BITLENGTH: 16,
        "max": np.iinfo(np.uint16).max,
        "min": np.iinfo(np.uint16).min,
        DEFAULT_VALUE: 0,
    },
    U32: {
        "name": U32,
        BITLENGTH: 32,
        "max": np.iinfo(np.uint32).max,
        "min": np.iinfo(np.uint32).min,
        DEFAULT_VALUE: 0,
    },
    U64: {
        "name": U64,
        BITLENGTH: 64,
        "max": np.iinfo(np.uint64).max,
        "min": np.iinfo(np.uint64).min,
        DEFAULT_VALUE: 0,
    },
    I8: {
        "name": I8,
        BITLENGTH: 8,
        "max": np.iinfo(np.int8).max,
        "min": np.iinfo(np.int8).min,
        DEFAULT_VALUE: 0,
    },
    I16: {
        "name": I16,
        BITLENGTH: 16,
        "max": np.iinfo(np.int16).max,
        "min": np.iinfo(np.int16).min,
        DEFAULT_VALUE: 0,
    },
    I32: {
        "name": I32,
        BITLENGTH: 32,
        "max": np.iinfo(np.int32).max,
        "min": np.iinfo(np.int32).min,
        DEFAULT_VALUE: 0,
    },
    I64: {
        "name": I64,
        BITLENGTH: 64,
        "max": np.iinfo(np.int64).max,
        "min": np.iinfo(np.int64).min,
        DEFAULT_VALUE: 0,
    },
    F32: {
        "name": F32,
        BITLENGTH: 32,
        "max": np.finfo(np.float32).max,
        "min": np.finfo(np.float32).min,
        DEFAULT_VALUE: 0,
    },
    F64: {
        "name": F64,
        BITLENGTH: 64,
        "max": np.finfo(np.float64).max,
        "min": np.finfo(np.float64).min,
        DEFAULT_VALUE: 0,
    },
    # BF: {
    #     "name": BF,
    #     BITLENGTH: 0,
    #     "max": 0,
    #     "min": 0,
    #     DEFAULT_VALUE: 0,
    # },
    STATEFIELD: {
        "name": STATEFIELD,
        BITLENGTH: 32,
        "max": np.iinfo(np.int32).max,
        "min": np.iinfo(np.int32).min,
        DEFAULT_VALUE: 0,
    },
}
