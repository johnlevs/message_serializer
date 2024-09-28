from message_serializer.lexerConfig import *

# U8CPP = "uint8_t"
# U16CPP = "uint16_t"
# U32CPP = "uint32_t"
# U64CPP = "uint64_t"
# I8CPP = "int8_t"
# I16CPP = "int16_t"
# I32CPP = "int32_t"
# I64CPP = "int64_t"
# F32CPP = "float"
# F64CPP = "double"
U8CPP = "u8"
U16CPP = "u16"
U32CPP = "u32"
U64CPP = "u64"
I8CPP = "i8"
I16CPP = "i16"
I32CPP = "i32"
I64CPP = "i64"
F32CPP = "f32"
F64CPP = "f64"


CPP_TO_BUILTINS = {
    U8CPP: BUILTINS[U8],
    U16CPP: BUILTINS[U16],
    U32CPP: BUILTINS[U32],
    U64CPP: BUILTINS[U64],
    I8CPP: BUILTINS[I8],
    I16CPP: BUILTINS[I16],
    I32CPP: BUILTINS[I32],
    I64CPP: BUILTINS[I64],
    F32CPP: BUILTINS[F32],
    F64CPP: BUILTINS[F64],
}

BUILTIN_TO_CPP = {
    U8: U8CPP,
    U16: U16CPP,
    U32: U32CPP,
    U64: U64CPP,
    I8: I8CPP,
    I16: I16CPP,
    I32: I32CPP,
    I64: I64CPP,
    F32: F32CPP,
    F64: F64CPP,
}


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
