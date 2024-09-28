from abc import ABC, abstractmethod
import datetime
from message_serializer.ast import ast


class Generator(ABC):
    tabCount = 0
    inlineCommentChar = "#"

    def __init__(self, tree: "ast"):
        self.tree = tree

    def tab(self):
        return "\t" * self.tabCount

    def indent(self):
        self.tabCount += 1

    def dedent(self):
        self.tabCount -= 1

    def get_license(self):
        lic = (
            self.inlineCommentChar
            + " =========================================================================\n"
            + self.inlineCommentChar
            + " THIS CODE HAS BEEN AUTOMATICALLY GENERATED USING 'message_serializer' TOOL\n"
            + self.inlineCommentChar
            + "       https://github.com/johnlevs/message_serializer\n"
            + self.inlineCommentChar
            + "       Generated on: "
            + self.inlineCommentChar
            + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + self.inlineCommentChar
            + " \n"
            + self.inlineCommentChar
            + " =========================================================================\n"
        )
        with open("LICENSE", "r") as f:
            for line in f:
                lic += f"{self.inlineCommentChar} {line}"

        return lic

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def _generate_message(self, message):
        pass

    @abstractmethod
    def _generate_enum(self, enum):
        pass

    @abstractmethod
    def _generate_constants(self, constant):
        pass

    @abstractmethod
    def _generate_module(self, module):
        pass

    @abstractmethod
    def _generate_message_serialization_helper(self, message):
        pass

    @abstractmethod
    def _generate_message_deserialization(self, message):
        pass

    @abstractmethod
    def generate_source_files(self, output_dir):
        pass