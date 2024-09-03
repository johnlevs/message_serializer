import ply.yacc as yacc

from message_serializer.lexer import *
import message_serializer.lexer as lexerRef


"""
====================================================================================================
                                        GRAMMAR FUNCTIONS
====================================================================================================
"""


def p_start(p):
    """start : entries"""
    messages = [entry for entry in p[1] if entry["entryType"] == MSGDEF]
    constants = [entry for entry in p[1] if entry["entryType"] == CONST]
    states = [entry for entry in p[1] if entry["entryType"] == STATE]
    p[0] = {"messages": messages, "constants": constants, "states": states}


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
    if len(p) == 8:
        p[0] = {
            "entryType": CONST,
            "type": p[3],
            "name": p[2],
            "default_value": p[5],
            DOC: p[7],
            "line": p.lineno(1),
        }
    else:
        p[0] = {
            "entryType": CONST,
            "type": p[3],
            "name": p[2],
            "default_value": p[5],
            "line": p.lineno(1),
        }


def p_message_def(p):
    """message_def : MESSAGEDEF IDENTIFIER optional_fields "{" field_defs "}" """
    p[0] = {
        "entryType": MSGDEF,
        "type": p[1],
        "name": p[2],
        "line": p.lineno(1),
        "fields": p[5],
    }
    for optional_field in p[3]:
        p[0][list(optional_field.keys())[0]] = optional_field[
            list(optional_field.keys())[0]
        ]


def p_state_def(p):
    """state_def : STATE IDENTIFIER optional_fields "{" state_fields "}" """
    p[0] = {
        "entryType": STATE,
        "type": p[1],
        "name": p[2],
        "line": p.lineno(1),
        "fields": p[5],
    }
    for optional_field in p[3]:
        p[0][list(optional_field.keys())[0]] = optional_field[
            list(optional_field.keys())[0]
        ]


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
        p[0] = {"name": p[1], "default_value": p[2], "line": p.lineno(1)}
    else:
        p[0] = {"name": p[1], "default_value": p[2], "doc": p[4], "line": p.lineno(1)}


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
    ("left", "PW"),
)


def p_field_def(p):
    """field_def :  IDENTIFIER resolved_type count_field default_value optional_fields newline"""
    p[0] = {
        "name": p[1],
        "type": p[2],
        "count": p[3],
        "default_value": p[4],
        "line": p.lineno(1),
    }
    if p[5] is not None:
        for optional_field in p[5]:
            p[0][list(optional_field.keys())[0]] = optional_field[
                list(optional_field.keys())[0]
            ]



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
            p[0] = {DOC: p[2]}
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

    print(f"\nSyntax error in file {current_file}, line {p.lineno} at '{p.value}':")
    print("\t" + line)
    print("\t" + " " * (column - 1) + "^")

    lexerRef.errorCount += 1
    __parser.errok()


__parser = yacc.yacc()

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
            print(token)
            token = lexer.token()
        print("\n")

    tree = __parser.parse(file_text)
    __parser.lineno = 1
    lexer.lineno = 1
    return tree


def error_count():
    return lexerRef.errorCount


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
