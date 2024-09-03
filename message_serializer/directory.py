import os

from message_serializer.module import Module


class Directory:
    _debug = False

    def __init__(self, path):
        Module._module_debug = self._debug
        self.path = path
        self.modules = []
        self._load_modules()

    def _load_modules(self):
        for file in os.listdir(self.path):
            if file.endswith(".icd"):
                m = Module(os.path.join(self.path, file))
                self.modules.append(m)

    def __str__(self):
        return "\n".join([str(module) for module in self.modules])

    def validate(self):
        moduleNames = []
        constants = []
        for module in self.modules:
            moduleNames += module.get_names()
            constants += module.get_constants()

        for module in self.modules:
            module.validate_type_names(moduleNames)
            module.validate_module_names()
            module.validate_message_names()
            module.validate_default_values(constants)
