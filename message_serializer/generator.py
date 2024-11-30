import datetime
import os
import logging

from abc import ABC, abstractmethod
from message_serializer.ast import ast
from message_serializer.lexerConfig import *


logger = logging.getLogger("message_serializer")


class Generator(ABC):
    tabCount = 0
    inlineCommentChar = "#"
    scope_combine_function = lambda self, higher, lower: f"{higher}.{lower}"
    msg_id_function = lambda self, higher, lower: f"{higher}__{lower}"

    def __init__(self, tree: "ast"):
        self.ast_tree = tree

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

        this_dir = os.path.dirname(os.path.realpath(__file__))
        license_file = os.path.join(this_dir, "..", "LICENSE")
        with open(license_file, "r") as f:
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

    def _message_field_worker(
        self,
        message,
        on_bf_open=lambda field, *args: "",
        on_bf_close=lambda field, *args: "",
        on_bf=lambda field, *args: "",
        on_udf=lambda field, *args: "",
        on_df=lambda field, *args: "",
        *args,
    ):
        line = ""
        bf_name = None
        bf_open = False
        bf_size = 0
        for field in message["fields"]:
            if field["type"] in BUILTINS.keys():
                if field["type"] == BF:
                    if not bf_open:
                        line += on_bf_open(field, bf_name, bf_size, *args)
                        bf_open = True
                    elif bf_name != field[PW]:
                        line += on_bf_close(field, bf_name, bf_size, *args)
                        line += on_bf_open(field, bf_name, bf_size, *args)
                    bf_name = field[PW]
                    line += on_bf(field, bf_name, bf_size, *args)
                    bf_size += int(field["count"])
                else:
                    if bf_open:
                        line += on_bf_close(field, bf_name, bf_size, *args)
                        bf_open = False
                        bf_size = 0
                    line += on_df(field, bf_name, bf_size, *args)
            else:
                if bf_open:
                    line += on_bf_close(field, bf_name, bf_size, *args)
                    bf_open = False
                    bf_size = 0
                line += on_udf(field, bf_name, bf_size, *args)
        if bf_open:
            line += on_bf_close(field, bf_name, bf_size, *args)
        return line

    def msg_2_wordID(self, message):
        return self.msg_id_function(message["parent"]["name"], message["name"])

    def msg_name_w_scope(self, message):
        temp = self.scope_combine_function(message["parent"]["name"], message["name"])
        if "parent" in message["parent"]:
            return self.scope_combine_function(message["parent"]["parent"]["name"], temp)
        return temp
    
    def msg_name_w_scope_from_name(self, name):
        return self.msg_name_w_scope(self.ast_tree.find_member_reference(name))
        
