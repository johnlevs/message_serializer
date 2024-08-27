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
                if len(stripLine) > 0 and stripLine[0] == "#":
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
