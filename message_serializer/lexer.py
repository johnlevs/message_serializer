import sys
import ply.lex as lex
from message_serializer.lexerConfig import *
import tempfile

reserved = {"MSG": MSGDEF, "CONSTANT": CONST, "STATE": STATE}

tokens = [ID, TYPE, STRING, NUMBER, DOC, PW, "newline"] + list(reserved.values())

literals = "[]={}"

t_ignore = " \t"
t_STRING = STRINGREG
t_DOC = DOCREG
t_PW = PWREG
t_NUMBER = NUMBERREG
t_ignore_COMMENT = r"\#.*"


type_regex = "".join([f"{builtInType}|" for builtInType in list(BUILTINS.keys())])


@lex.TOKEN(type_regex[:-1])
def t_TYPE(t):
    ...
    return t


def t_newline(t):
    r"\n+|(\r\n)+"
    t.lexer.lineno += len(t.value)
    return t


@lex.TOKEN(IDREG)
def t_IDENTIFIER(t):
    ...
    t.type = reserved.get(t.value, ID)  # Check for reserved words
    return t


current_file = ""
errorCount = 0


def t_error(t):
    global errorCount
    global current_file
    errorCount += 1
    column = find_column(t)
    line = get_line_text(t)
    print(
        f"Error in file {current_file}, line {t.lineno}: Illegal character '{t.value[0]}'"
    )
    print("\t" + line)
    print("\t" + " " * (column - 1) + "^")
    t.lexer.skip(1)


if getattr(sys, "frozen", False):
    outputdir = tempfile.gettempdir()
    lexer = lex.lex(debug=False, optimize=True, outputdir=outputdir)
else:
    lexer = lex.lex(optimize=False)
    

"""
====================================================================================================
                                        HELPER FUNCTIONS
====================================================================================================
"""


def find_column(token):
    text = token.lexer.lexdata
    line_start = text.rfind("\n", 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


def get_line_text(token):
    text = token.lexer.lexdata
    line_start = text.rfind("\n", 0, token.lexpos) + 1
    return text[line_start : text.find("\n", token.lexpos)]
