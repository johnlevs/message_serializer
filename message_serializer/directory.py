import os
import logging

from message_serializer.ast import ast
from message_serializer import parser

logger = logging.getLogger("message_serialize")


class Directory:
    _debug = False
    CONFIG_FILE_ENDING = ".icd"

    def __init__(self, path):
        self._module_debug = self._debug
        self.path = path
        self.modules = self._load_modules()

    def _load_modules(self):
        modules = []
        logger.info(
            f"Scanning directory {self.path} for *{self.CONFIG_FILE_ENDING} files"
        )
        for file in os.listdir(self.path):
            if file.endswith(self.CONFIG_FILE_ENDING):
                logger.info(f"Found {file}, parsing...")
                modules.append(self._read_module(os.path.join(self.path, file)))
        return modules

    def __str__(self):
        return "\n".join([str(module) for module in self.modules])

    def names(self):
        return [module.name for module in self.modules]

    def validate(self):
        logger.info("Validating modules")
        tree = {"modules": self.modules, "type": "directory", "name": "root"}
        for module in self.modules:
            module["parent"] = tree
        return ast(tree)  # , error_count

    def _read_module(self, fullFileName):
        name = fullFileName.replace("\\", "/").split("/")[-1].split(".")[0].upper()
        logger.debug(f"Creating module from file {fullFileName}. Name: {name}")
        with open(fullFileName, "r") as file:
            moduleTree = parser.parse_string(
                file.read(), fileName=fullFileName, debug=self._module_debug
            )
            if moduleTree is None:
                raise ValueError(f"Error parsing file {fullFileName}")
            moduleTree["filename"] = fullFileName
            moduleTree["name"] = name
            moduleTree["type"] = "module"
            moduleTree["line"] = 0
            return moduleTree
