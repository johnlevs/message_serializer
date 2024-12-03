import datetime
import os
import logging

from abc import ABC, abstractmethod
from message_serializer.ast import ast, is_number
from message_serializer.lexerConfig import *


logger = logging.getLogger("message_serializer")


class Generator(ABC):
    tabCount = 0
    msg_id_function = lambda self, higher, lower: f"{higher}__{lower}"

    def __init__(
        self,
        tree: "ast",
        inlineCommentChar,
        scope_combine_function,
        type_lookup: dict,
    ):
        self.scope_combine_function = scope_combine_function
        self.type_lookup = type_lookup
        self.inlineCommentChar = inlineCommentChar
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
        for field in message["fields"]:
            e_type = self.ast_tree.get_type(field)
            if e_type == BF:
                line += on_bf_open(field) + on_bf(field) + on_bf_close(field)
            elif e_type in BUILTINS.keys():
                line += on_df(field)
            else:
                line += on_udf(field)

        return line

    def msg_2_wordID(self, message):
        return self.msg_id_function(message["parent"]["name"], message["name"])

    def msg_name_w_scope(self, message):
        temp = self.scope_combine_function(message["parent"]["name"], message["name"])
        if (
            "parent" in message["parent"]
            and message["parent"]["parent"]["type"] != "directory"
        ):
            return self.scope_combine_function(
                message["parent"]["parent"]["name"], temp
            )
        return temp

    def get_module_name(self, element):
        if element["type"] == "module":
            return element["name"]
        return self.get_module_name(element["parent"])

    def get_language_type(self, element):
        e_type = self.ast_tree.get_type(element)
        if e_type not in BUILTINS.keys():
            return self.msg_name_w_scope(element["type"])
        return self.type_lookup[e_type]

    def get_default_value(self, element):
        if "default_value" in element and element["default_value"] is not None:
            dv = element["default_value"]
            if is_number(dv):
                return dv
            return self.msg_name_w_scope(dv)

        return None

    def get_count(self, element):
        if "count" not in element:
            return "1"
        if is_number(element["count"]):
            return element["count"]
        return self.msg_name_w_scope(element["count"])
