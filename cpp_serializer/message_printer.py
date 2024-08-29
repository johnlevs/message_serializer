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


from cpp_serializer.message_defs import *


class MessagePrinter:
    _SMALLEST_FIELD_SIZE: int = 8
    _layer = 0
    _enumType = "words"
    inheritedType = "serializableMessage"

    @staticmethod
    def tab():
        return "\t" * MessagePrinter._layer

    def incrementLayer(amount: int = 1):
        MessagePrinter._layer += amount

    def decrementLayer(amount: int = 1):
        MessagePrinter._layer -= amount
        MessagePrinter._layer = max(0, MessagePrinter._layer)

    """ Header file printing """

    @staticmethod
    def startHeaderGuard(name: str) -> str:
        name = name.replace(" ", "_").upper()
        if not name_is_valid(name):
            print(f"Warning: {name} is not a valid name for a header guard")
            return MessagePrinter.inlineComment(
                f"#ifndef __{name}__\n#define __{name}__\n"
            )
        return f"#ifndef __{name}__\n#define __{name}__\n"

    @staticmethod
    def endHeaderGuard(name: str) -> str:
        name = name.replace(" ", "_").upper()
        if not name_is_valid(name):
            return MessagePrinter.inlineComment(f"#endif // __{name}__")
        return f"#endif // __{name}__\n"

    @staticmethod
    def startModule(namespace: str) -> str:
        line = MessagePrinter.tab() + "namespace " + namespace + " {\n"
        MessagePrinter.incrementLayer()
        return line

    @staticmethod
    def endModule() -> str:
        MessagePrinter.decrementLayer()
        return MessagePrinter.tab() + "};\n"

    def startMessageSize() -> str:
        return MessagePrinter.tab() + "static constexpr int SIZE = "

    def paramSize(paramText) -> str:
        return f"sizeof({paramText})"

    def messageSize(messageType, moduleName=None) -> str:
        if moduleName != None:
            string = ""
            for module in moduleName:
                string += f"{module}::"

            return f"{string}{messageType}::SIZE"

        return f"{messageType}::SIZE"

    @staticmethod
    def startMessage(messageName) -> str:
        # start message header
        line = (
            MessagePrinter.tab()
            + "typedef struct "
            + messageName
            + f" : public {MessagePrinter.inheritedType}"
            + " {\n"
            + MessagePrinter.tab()
            + "\n"
        )
        MessagePrinter.incrementLayer()

        return line

    @staticmethod
    def endMessage(enumName) -> str:
        line = ""
        line += f"{MessagePrinter.tab()}static constexpr {MessagePrinter._enumType} m_wordId = {enumName};\n\n"
        # add in required serialize and deserialize functions
        line += f"{MessagePrinter.tab()}int serialize(uint8_t *buffer) override;\n"
        line += f"{MessagePrinter.tab()}int deserialize(uint8_t *buffer) override;\n"
        line += (
            f"{MessagePrinter.tab()}constexpr wordIds wordId() override "
            + "{ return m_wordId; };\n\n"
        )
        MessagePrinter.decrementLayer()
        return line + MessagePrinter.tab() + "};\n"

    @staticmethod
    def startBitField() -> str:
        line = (
            MessagePrinter.tab() + "union {\n" + MessagePrinter.tab() + "\tstruct {\n"
        )
        MessagePrinter.incrementLayer(2)
        return line

    @staticmethod
    def endBitField(bitfieldName: str) -> str:
        MessagePrinter.decrementLayer()
        line = MessagePrinter.tab() + "};\n"
        line += MessagePrinter.tab() + bitfieldName + "\n"
        MessagePrinter.decrementLayer()
        line += MessagePrinter.tab() + "};\n"

        return line

    @staticmethod
    def printParam(paramText, docs="", hierarchy=None) -> str:
        line = MessagePrinter.tab() + paramText
        line = line + "\t /** " + docs + " */\n" if docs != "" else line + "\n"
        return line

    @staticmethod
    def printBitFieldParam(paramText, bitSize, docs="") -> str:
        if paramText[-1] == ";":
            paramText = paramText[:-1]
        line = MessagePrinter.tab() + paramText + " : " + str(bitSize) + ";"
        line = line + "\t /** " + docs + " */\n" if docs != "" else line + "\n"
        return line

    @staticmethod
    def startEnumMessageList(listName: str) -> str:
        MessagePrinter._enumType = listName
        string = MessagePrinter.tab() + f"enum {MessagePrinter._enumType}" + " {\n"
        MessagePrinter.incrementLayer()
        return string

    @staticmethod
    def printEnumMessageList(enumName: str) -> str:
        return MessagePrinter.tab() + f"{enumName},\n"

    @staticmethod
    def endEnumMessageList() -> str:
        string = "\n"
        string += MessagePrinter.printEnumMessageList("_MESSAGE_COUNT")
        string += MessagePrinter.printEnumMessageList("_INVALID_MESSAGE")
        MessagePrinter.decrementLayer()
        string += MessagePrinter.tab() + "};\n"

        return string

    @staticmethod
    def startMaxSizeFunction() -> str:
        line = MessagePrinter.tab() + "constexpr int GET_MAX_SIZE()\n"
        line += MessagePrinter.tab() + "{\n"
        MessagePrinter.incrementLayer()
        line += MessagePrinter.tab() + "int SIZE = 0;\n"

        return line

    @staticmethod
    def maxSizeFunctionParam(messageName, nameSpace) -> str:
        if nameSpace != "":
            messageName = f"{nameSpace}::{messageName}"

        return (
            MessagePrinter.tab()
            + f"SIZE = {messageName}::SIZE > SIZE ? {messageName}::SIZE : SIZE;\n"
        )

    @staticmethod
    def endMaxSizeFunction() -> str:
        line = MessagePrinter.tab() + "return SIZE;\n"
        MessagePrinter.decrementLayer()
        line += MessagePrinter.tab() + "}\n"
        line += MessagePrinter.tab() + "constexpr int MAX_SIZE = GET_MAX_SIZE();\n\n"

        return line

    """ Implimentation serialize and deserialize functions """

    @staticmethod
    def startSerializeFunction(name, namespace="") -> str:
        if namespace == "":
            line = MessagePrinter.tab() + f"int {name}::serialize(uint8_t *buffer)\n"
        else:
            line = (
                MessagePrinter.tab()
                + f"int {namespace}::{name}::serialize(uint8_t *buffer)\n"
            )
        line += MessagePrinter.tab() + "{\n"
        MessagePrinter.incrementLayer()
        line += MessagePrinter.tab() + "uint8_t *itr = buffer;\n"
        return line

    @staticmethod
    def serializeParameter(paramName, paramCount) -> str:
        if paramCount == 1:
            line = (
                MessagePrinter.tab()
                + f"HTON(&{paramName}, itr, sizeof({paramName}));\n"
            )
        else:
            line = (
                MessagePrinter.tab()
                + f"for (int i = 0; i < {paramCount}; i++) "
                + "{\n"
            )
            MessagePrinter.incrementLayer()
            line += (
                MessagePrinter.tab()
                + f"HTON(&{paramName}[i], itr, sizeof({paramName}[i]));\n"
            )
            MessagePrinter.decrementLayer()
            line += MessagePrinter.tab() + "}\n"
        return line

    @staticmethod
    def serializeMessageCall(name) -> str:
        return MessagePrinter.tab() + "itr += " + f"{name}.serialize(itr);\n"

    @staticmethod
    def endSerializeFunction() -> str:
        line = MessagePrinter.tab() + "return itr - buffer;\n"
        MessagePrinter.decrementLayer()
        line += MessagePrinter.tab() + "}\n"
        return line

    @staticmethod
    def startDeserializeFunction(name, namespace="") -> str:
        if namespace == "":
            line = MessagePrinter.tab() + f"int {name}::deserialize(uint8_t *buffer)\n"
        else:
            line = (
                MessagePrinter.tab()
                + f"int {namespace}::{name}::deserialize(uint8_t *buffer)\n"
            )
        line += MessagePrinter.tab() + "{\n"
        MessagePrinter.incrementLayer()
        line += MessagePrinter.tab() + "uint8_t *itr = buffer;\n"
        return line

    @staticmethod
    def deserializeParameter(paramName, paramCount) -> str:
        if paramCount == 1:
            line = (
                MessagePrinter.tab()
                + f"NTOH(&{paramName}, itr, sizeof({paramName}));\n"
            )
        else:
            line = (
                MessagePrinter.tab()
                + f"for (int i = 0; i < {paramCount}; i++) "
                + "{\n"
            )
            MessagePrinter.incrementLayer()
            line += (
                MessagePrinter.tab()
                + f"NTOH(&{paramName}[i], itr, sizeof({paramName}[i]));\n"
            )
            MessagePrinter.decrementLayer()
            line += MessagePrinter.tab() + "}\n"

        return line

    @staticmethod
    def deserializeMessageCall(name) -> str:
        return MessagePrinter.tab() + f"{name}.deserialize(itr);\n"

    @staticmethod
    def endDeserializeFunction() -> str:
        line = MessagePrinter.tab() + "return itr - buffer;\n"
        MessagePrinter.decrementLayer()
        line += MessagePrinter.tab() + "}\n"
        return line

    """ comment printing"""

    @staticmethod
    def startMessageDoc(messageName: str, messageBrief: str) -> str:
        return f"{MessagePrinter.tab()}/**\n{MessagePrinter.tab()} * @brief {messageName}: {messageBrief}\n"

    @staticmethod
    def endMessageDoc() -> str:
        return f"{MessagePrinter.tab()} */\n"

    @staticmethod
    def printParameterDoc(documentStr: str, paramName: str) -> str:
        return MessagePrinter.tab() + f" * @param {paramName} {documentStr}\n"

    @staticmethod
    def inlineComment(commentStr: str) -> str:
        return MessagePrinter.tab() + f"// {commentStr}\n"

    @staticmethod
    def newlines(amount: int = 1) -> str:
        return "\n" * amount

    @staticmethod
    def printCodeGenWarning() -> str:
        return (
            "// =========================================================================\n"
            "// THIS CODE HAS BEEN AUTOMATICALLY GENERATED USING 'cpp_serializer' TOOL\n"
            "//      https://github.com/johnlevs/cpp_serializer\n"
            "// ========================================================================="
        )
