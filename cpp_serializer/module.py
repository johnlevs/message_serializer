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


from typing import List
import logging

from cpp_serializer.message_defs import *
from cpp_serializer.message_printer import MessagePrinter
from cpp_serializer.message import Message, ModuleElement
from cpp_serializer.message_parameter import MessageParameter
from cpp_serializer.module_list_element import Module_List_Element


logger = logging.Logger("cpp_serializer")


class Module(Module_List_Element):

    msgs: List["ModuleElement"]

    def __init__(self, moduleName="", parent=None):
        super().__init__(parent, moduleName)
        self.moduleName = moduleName.upper()
        self.msgs = []

    def loadConfig(self, path):
        msg = None
        with open(path) as file:
            for line in file:
                stripLine = line.strip()
                if len(stripLine) > 0 and stripLine[0] == "#" or line == "\n":
                    continue

                if line.startswith(config[MSGDEFSTRT]) and msg == None:
                    msg = Message(line, self)

                elif line.startswith(config[MSGDEFEND]) and msg != None:
                    self.msgs.append(msg)
                    msg = None

                elif msg != None:
                    param = MessageParameter(line, True, msg)
                    if param.init:
                        msg.add_param(param)

    def validatemsgs(self, messageList):
        [msg.removeInvalidParameters(messageList) for msg in self.msgs]

    def to_cpp_string(self):
        string = ""
        if self.moduleName != "":
            string += MessagePrinter.startModule(self.moduleName)

        for msg in self.msgs:
            string += msg.to_cpp_string() + "\n"

        if self.moduleName != "":
            string += MessagePrinter.endModule()

        return string

    def to_cpp_serialize_implimentation_string(self):
        string = "\n\n"

        for msg in self.msgs:
            string += msg.to_cpp_serialize_implimentation_string() + "\n"
        return string

    def to_cpp_deserialize_implimentation_string(self):
        string = "\n\n"
        for msg in self.msgs:
            string += msg.to_cpp_deserialize_implimentation_string() + "\n"
        return string

    def to_enum_message_list(self):
        string = "\n\n"
        string += MessagePrinter.startEnumMessageList("WordIds")
        for msg in self.msgs:
            string += msg.to_enum_string()
        string += MessagePrinter.endEnumMessageList()
        return string

    def get_module_name(self) -> str:
        return self.moduleName

    def get_messages(self) -> List["ModuleElement"]:
        return self.msgs

    def get_module_hierarchy(self) -> str:
        return self.parent.get_module_hierarchy() + [self.moduleName]
