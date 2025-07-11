import ply.yacc as yacc
import logging
import sys

from message_serializer.lexer import *
import message_serializer.lexer as lexerRef


logger = logging.getLogger("message_serialize")

"""
====================================================================================================
                                        GRAMMAR FUNCTIONS
====================================================================================================
"""


def p_start(p):
    """start : entries"""
    if p[1] is None:
        return
    p[0] = {"elements": p[1]}
    for element in p[1]:
        element["parent"] = p[0]


def p_entries(p):
    """entries  : entries entry
    | entry"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_entry(p):
    """entry    : message_def
    | constant_def
    | state_def"""
    p[0] = p[1]


def p_constant_def(p):
    """constant_def : CONST IDENTIFIER TYPE "=" IDENTIFIER newline
    | CONST IDENTIFIER TYPE "=" IDENTIFIER DOC STRING newline
    | CONST IDENTIFIER TYPE "=" NUMBER newline
    | CONST IDENTIFIER TYPE "=" NUMBER DOC STRING newline"""
    p[0] = {
        "name": p[2],
        "type": p[3],
        "line": p.lineno(1),
        "count": 1,
        "default_value": p[5],
    }
    if len(p) == 8:
        p[0][DOC] = p[7]


def p_constant_def_error2(p):
    """constant_def : CONST IDENTIFIER TYPE "=" newline
    | CONST IDENTIFIER TYPE "=" error DOC STRING newline
    | CONST IDENTIFIER TYPE "=" error NUMBER newline"""
    print(
        f"Syntax error in file {lexerRef.current_file}, line {p.lineno(1)} at '{p[4]}': Missing or invalid default value"
    )
    print("\t" + get_line_text(p.slice[5]))
    print("\t" + " " * (find_column(p.slice[5]) - 1) + "^")
    lexerRef.errorCount += 1
    __parser.errok()


def p_message_def(p):
    """message_def : MESSAGEDEF IDENTIFIER optional_fields "{" field_defs "}" """
    p[0] = {
        "name": p[2],
        "type": p[1],
        "line": p.lineno(1),
        "fields": p[5],
    }
    # assign parent references to fields

    p[0]["fields"] = merge_adjacent_bitfields(p[0]["fields"])

    for field in p[0]["fields"]:
        field["parent"] = p[0]

    if p[3] is None:
        return
    for optional_field in p[3]:
        p[0][list(optional_field.keys())[0]] = optional_field[
            list(optional_field.keys())[0]
        ]


def p_message_def_error(p):
    """message_def : MESSAGEDEF error optional_fields "{" field_defs "}" """
    print(
        f"Syntax error in file {lexerRef.current_file}, line {p.lineno(1)} at '{p[2]}'"
    )
    print("\t" + get_line_text(p))
    print("\t" + " " * (find_column(p) - 1) + "^")
    lexerRef.errorCount += 1
    __parser.errok()


def p_state_def(p):
    """state_def : STATE IDENTIFIER optional_fields "{" state_fields "}" """
    p[0] = {
        "name": p[2],
        "type": p[1],
        "line": p.lineno(1),
        "fields": p[5],
    }
    # assign parent references to fields
    for field in p[0]["fields"]:
        field["parent"] = p[0]
    if p[3] is None:
        return
    for optional_field in p[3]:
        p[0][list(optional_field.keys())[0]] = optional_field[
            list(optional_field.keys())[0]
        ]


def p_state_def_error(p):
    """state_def : STATE error optional_fields "{" state_fields "}" """
    print(
        f"Syntax error in file {lexerRef.current_file}, line {p.lineno(1)} at '{p[2]}': state name is required to define states"
    )
    print("\t" + get_line_text(p))
    print("\t" + " " * (find_column(p) - 1) + "^")
    lexerRef.errorCount += 1
    __parser.errok()


def p_state_fields(p):
    """state_fields : state_fields state_field
    | state_field"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_state_field(p):
    """state_field  : IDENTIFIER default_value newline
    | IDENTIFIER default_value DOC STRING newline"""
    if len(p) == 4:
        p[0] = {
            "name": p[1],
            "default_value": p[2],
            "line": p.lineno(1),
            "type": STATEFIELD,
        }
    else:
        p[0] = {
            "name": p[1],
            "default_value": p[2],
            "doc": p[4],
            "line": p.lineno(1),
            "type": STATEFIELD,
        }


def p_state_field_error(p):
    """state_field  : IDENTIFIER error newline
    | IDENTIFIER error DOC STRING newline"""
    print(
        f"Syntax error in file {lexerRef.current_file}, line {p.lineno(1)} at '{p[2]}'"
    )
    print("\t" + get_line_text(p))
    print("\t" + " " * (find_column(p) - 1) + "^")
    lexerRef.errorCount += 1
    __parser.errok()


def p_field_defs(p):
    """field_defs : field_defs field_def
    | field_def"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


precedence = (
    ("left", "IDENTIFIER"),
    ("left", "TYPE"),
    ("left", "NUMBER"),
    ("left", "STRING"),
    ("left", "DOC"),
    ("left", PW),
)


def p_field_def(p):
    """field_def :  IDENTIFIER resolved_type count_field default_value optional_fields newline"""
    p[0] = {
        "name": p[1],
        "type": p[2],
        "line": p.lineno(1),
        "count": p[3],
        "default_value": p[4],
    }
    if p[5] is not None:
        for optional_field in p[5]:
            p[0][list(optional_field.keys())[0]] = optional_field[
                list(optional_field.keys())[0]
            ]
    if not numeric_bounds_check(p[0]):
        print(
            f"Error in file {lexerRef.current_file}, line {p.lineno(1)}: "
            f"Default value '{p[0]['default_value']}' out of bounds for type '{p[0]['type']}'"
        )
        print("\t" + get_line_text(p.slice[1]))
        print("\t" + " " * (find_column(p.slice[1]) - 1) + "^")
        lexerRef.errorCount += 1


def p_field_def_error(p):
    """field_def :  IDENTIFIER error count_field default_value optional_fields newline
    | IDENTIFIER resolved_type count_field error optional_fields newline"""
    print(
        f"Syntax error in file {lexerRef.current_file}, line {p.lineno(1)} at '{p[2]}'"
    )
    print("\t" + get_line_text(p))
    print("\t" + " " * (find_column(p) - 1) + "^")
    lexerRef.errorCount += 1
    __parser.errok()


def p_count_field(p):
    """count_field  : "[" NUMBER "]"
    | "[" IDENTIFIER "]"
    | empty"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = 1


def p_default_value(p):
    """default_value    : "=" NUMBER
    | "=" IDENTIFIER
    | empty"""
    if len(p) == 3:
        p[0] = p[2]


def p_resolved_type(p):
    """resolved_type    : TYPE
    | IDENTIFIER"""
    p[0] = p[1]


def p_optional_fields(p):
    """optional_fields  : optional_field_list
    | empty"""
    p[0] = p[1]


def p_optional_field_list(p):
    """optional_field_list  : optional_field_list optional_field
    | optional_field"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_optional_field(p):
    """optional_field   : DOC STRING
    | PW IDENTIFIER"""
    if len(p) == 3:
        if p[1] == DOCREG:
            p[0] = {DOC: p[2][1:-1]}
        elif p[1] == PWREG:
            p[0] = {PW: p[2]}
    else:
        p[0] = {}


def p_empty(p):
    "empty :"
    pass


def p_error(p):
    if p is None:
        return
    if p.type == "newline":
        __parser.errok()
        return
    column = find_column(p)
    line = get_line_text(p)

    print(
        f"\nSyntax error in file {lexerRef.current_file}, line {p.lineno} at '{p.value}':"
    )
    print("\t" + line)
    print("\t" + " " * (column - 1) + "^")
    while True:
        tok = __parser.token()
        if not tok or tok.type == "newline":
            break

    lexerRef.errorCount += 1
    __parser.errok()


if getattr(sys, "frozen", False):
    __parser = yacc.yacc(optimize=True, debug=False, write_tables=False)
else:
    __parser = yacc.yacc(optimize=False)
    
"""
====================================================================================================
                                        HELPER FUNCTIONS
====================================================================================================
"""


def parse_string(file_text, fileName, debug=False):

    lexerRef.current_file = fileName

    if debug:
        lexer.input(file_text)
        token = lexer.token()
        while token is not None:
            logger.debug(f"Token: {token}")
            token = lexer.token()
    logger.debug("Parsing file: " + fileName)
    tree = __parser.parse(file_text)
    __parser.lineno = 1
    lexer.lineno = 1
    return tree


def error_count():
    return lexerRef.errorCount


def is_number(s):
    if s is None:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def numeric_bounds_check(node):
    value = node["default_value"]
    resolvedType = node["type"]
    if resolvedType not in BUILTINS.keys():

        return True
    if not is_number(value):
        return True

    bi_type = BUILTINS[resolvedType]

    if resolvedType in INT_TYPES:
        value = int(value)
    elif resolvedType in FLOAT_TYPES:
        value = float(value)

    minVal = bi_type["min"]
    maxVal = bi_type["max"]

    if resolvedType == BF:
        minVal = 0
        maxVal = 2 ** int(node["count"]) - 1
        resolvedType = "bitFeild_size_" + node["count"]

    return value >= minVal and value <= maxVal


def merge_adjacent_bitfields(entries):
    merged_entries = []
    i = 0
    bitfield_counter = 0
    current_bf_name = None
    existing_bf_names = set()

    while i < len(entries):
        entry = entries[i]
        if entry["type"] == BF:
            if PW in entry:
                pw = entry[PW]
                if pw in existing_bf_names:
                    raise ValueError(
                        f"Duplicate bitfield name '{pw}' found in message."
                    )
                existing_bf_names.add(pw)
                current_bf_name = pw
            else:
                if current_bf_name is None:
                    current_bf_name = f"bitfield_{bitfield_counter}"
                    bitfield_counter += 1
                pw = current_bf_name

            bitfield_group = [entry]
            total_count = int(entry["count"])
            i += 1
            while i < len(entries) and entries[i]["type"] == BF:
                next_entry = entries[i]
                if PW in next_entry:
                    next_pw = next_entry[PW]
                    if next_pw in existing_bf_names:
                        raise ValueError(
                            f"Duplicate bitfield name '{next_pw}' found in message."
                        )
                    existing_bf_names.add(next_pw)
                    current_bf_name = next_pw
                    break
                bitfield_group.append(next_entry)
                total_count += next_entry["count"]
                i += 1

            if total_count % 8 != 0:
                padding_bits = 8 - (total_count % 8)
                padding_name = f"padding_{bitfield_counter}"
                bitfield_counter += 1
                bitfield_group.append(
                    {
                        "name": padding_name,
                        "type": BF,
                        "count": padding_bits,
                        "default_value": 0,
                        "line": entry["line"],
                    }
                )

            merged_entries.append(
                {
                    "name": pw,
                    "fields": bitfield_group,
                    "type": BF,
                    "count": total_count,
                    "line": entry["line"],
                }
            )
        else:
            merged_entries.append(entry)
            i += 1

    return merged_entries
