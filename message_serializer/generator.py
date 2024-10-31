import datetime
import os
import logging

from abc import ABC, abstractmethod
from message_serializer.ast import ast


logger = logging.getLogger("message_serializer")


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

    def _copy_template_file(self, output_dir, template_dir, file_name):
        # create output directory if it does not exist
        if not os.path.exists(output_dir):
            logger.debug(
                f"{output_dir} does not exist, creating directory {output_dir}"
            )
            os.makedirs(output_dir)
        with open(template_dir + "/" + file_name, "r") as f:
            with open(output_dir + "/" + file_name, "w") as out:
                out.write(self.get_license())
                out.write(f.read())

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
    def generate_source_files(self, output_dir, source_name=None):
        pass
