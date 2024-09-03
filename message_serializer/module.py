import message_serializer.parser as parser
import json


class Module:
    PAD_NAME = "pad"
    BITFIELD_NAME = "reserved"
    PAD_PARAM_COUNT = "pad_count"
    BITFIELD_NAME_COUNT = "bitfield_name_count"

    _module_debug = False

    def __init__(self, fullFileName):
        self.data = {"name": fullFileName.split("\\")[-1].split(".")[0].upper()}
        self.fileName = fullFileName
        with open(fullFileName, "r") as file:
            tree = parser.parse_string(
                file.read(), fileName=fullFileName, debug=self._module_debug
            )
            if tree is None or parser.error_count() > 0:
                raise ValueError(f"Error parsing file {fullFileName}")
            self.data["messages"] = tree["messages"]
            self.data["constants"] = tree["constants"]
            self.data["states"] = tree["states"]

    """
    ====================================================================================================
                                            MISC FUNCTIONS
    ====================================================================================================
    """

    def __str__(self):
        return json.dumps(self.data, indent=4)

    def get_names(self):
        """
        Get all the names in the top scope of the module
        """
        msgs = [message["name"] for message in self.data["messages"]]
        consts = [constant["name"] for constant in self.data["constants"]]
        states = [state["name"] for state in self.data["states"]]
        return msgs + consts + states

    def get_constants(self):
        """
        Get all the constants in the module
        """
        return self.data["constants"]

    """
    ====================================================================================================
                                            VALIDATION FUNCTIONS    
    ====================================================================================================
    """

    def validate_type_names(self, directory_message_list):
        """
        Validate that all types in the module are available in the directory.
        """

        # check messages
        for message in self.data["messages"]:
            for field in message["fields"]:
                if (
                    field["type"] not in directory_message_list
                    and field["type"] not in parser.BUILTINS
                ):
                    raise TypeError(
                        f"In {self.fileName}, line {field['line']}:\n"
                        f"\tdeclared Type '{field['type']}' is not builtin or available in parser tree"
                    )

        # check constants
        for constant in self.data["constants"]:
            if (
                constant["type"] not in directory_message_list
                and constant["type"] not in parser.BUILTINS
            ):
                raise TypeError(
                    f"In {self.fileName}, line {constant['line']}:\n"
                    f"\tdeclared Type '{constant['type']}' is not a known Symbol"
                )

    def validate_module_names(self):
        """
        Validate that all module elements (messages, constants, states) in the module have unique names
        """
        names = self.get_names()

        # check messages
        for message in self.data["messages"]:
            if names.count(message["name"]) > 1:
                raise NameError(
                    f"In {self.fileName}, line {message['line']}:\n"
                    f"\t'{message['name']}' is not unique in module '{self.data['name']}'"
                    f"\n\t\t{message['name']} is defined on line {message['line']}"
                )

        # check constants
        for constant in self.data["constants"]:
            if names.count(constant["name"]) > 1:
                raise NameError(
                    f"In {self.fileName}, line {constant['line']}:\n"
                    f"\t'{constant['name']}' is not unique in module '{self.data['name']}'"
                )
        # check states
        for state in self.data["states"]:
            if names.count(state["name"]) > 1:
                raise NameError(
                    f"In {self.fileName}, line {state['line']}:\n"
                    f"\t'{state['name']}' is not unique in module '{self.data['name']}'"
                )

    def validate_message_names(self):
        """
        Validate that all fields in each message/state have unique names
        """

        for message in self.data["messages"]:
            message[self.PAD_PARAM_COUNT] = 0
            message[self.BITFIELD_NAME_COUNT] = 0
            names = [field["name"] for field in message["fields"]] + list(
                set(
                    [
                        field[parser.PW]
                        for field in message["fields"]
                        if parser.PW in field.keys()
                    ]
                )
            )

            bfOpen = False
            prevName = None
            bfBitSize = 0
            newFields = []
            for field in message["fields"]:
                # check message names
                if names.count(field["name"]) > 1:
                    raise NameError(
                        f"In {self.fileName}, line {field['line']}:\n"
                        f"\t'{field['name']}' is not unique in message '{message['name']}'"
                    )

                # rules for bitfields:
                #
                # - The name of the first bitfield in a message will be generated or defined by the user
                # - Adjacent bitfield parameters with no name will share the previous name until a
                #   new unique bitfield name is defined, thus creating a new separate bitfield
                #       (adjacent parameters with the same DEFINED name will be considered part of the same bitfield)
                # - If a bitfield name is defined, it must be unique in the message and will throw an error if it is not
                # - If a bitfield name is not defined, it will be generated and be unique in the message
                #
                # check bitfield names
                if field["type"] == "bitfield":
                    # if the BF name is defined, check if it is unique
                    if parser.PW in field.keys():
                        if names.count(field[parser.PW]) > 1:
                            raise NameError(
                                f"In {self.fileName}, line {field['line']}:\n"
                                f"\t'{field[parser.PW]}' is not unique in message '{message['name']}'"
                            )

                        # BITFIELDS CAN CLOSE HERE, add padding
                        if bfOpen and prevName != field[parser.PW]:
                            # add padding if a BF was previously open since we are may be opening a new one
                            newFields.append(
                                self.create_padding_field(message, bfBitSize, prevName)
                            )
                            bfBitSize = 0
                            prevName = None

                        prevName = field[parser.PW]

                    elif bfOpen:
                        # if the BF name is not defined but was previously open, use the previous name
                        field[parser.PW] = prevName
                    else:
                        # if the BF name is not defined, generate unique name
                        field[parser.PW] = self.get_open_bitField_name(message)
                        prevName = field[parser.PW]

                    bfOpen = True
                    bfBitSize += int(field["count"])

                elif bfOpen:
                    # BITFIELDS CAN CLOSE HERE, add padding
                    newFields.append(
                        self.create_padding_field(message, bfBitSize, prevName)
                    )

                    bfBitSize = 0
                    bfOpen = False
                    prevName = None

                newFields.append(field)

            # BITFIELDS CAN CLOSE HERE, add padding
            if bfOpen:
                newFields.append(
                    self.create_padding_field(message, bfBitSize, prevName)
                )
            # update fields
            message["fields"] = newFields

        # validate state names
        names = [state["name"] for state in self.data["states"]]
        for state in self.data["states"]:
            for field in state["fields"]:
                if names.count(field["name"]) > 1:
                    raise NameError(
                        f"In {self.fileName}, line {field['line']}:\n"
                        f"\t'{field['name']}' is not unique in state '{state['name']}'"
                    )

    def validate_default_values(self, directory_constants_list):

        # validate constants first as other types may reference them
        for constantNode in self.data["constants"]:
            visitList = {}
            self.validate_const_references_recursive(
                constantNode, visitList, directory_constants_list
            )

        for message in self.data["messages"]:
            for field in message["fields"]:
                if "default_value" not in field.keys():
                    # this shouldn't happen, the parser should fill in default vaue as "None", but just in case
                    raise ValueError(
                        f"In {self.fileName}, line {field['line']}:\n"
                        f"\tNo default value provided for field '{field['name']}'"
                    )
                # no default value provided, no need to check
                if field["default_value"] is None:
                    continue

                if not self.is_number(field["default_value"]):
                    field["actual_value"] = self.validate_constant_references(
                        field["default_value"], field["type"], directory_constants_list
                    )
                else:
                    self.resolve_default_value(field)

        # validate states
        for state in self.data["states"]:
            for field in state["fields"]:
                if "default_value" not in field.keys():
                    raise ValueError(
                        f"In {self.fileName}, line {field['line']}:\n"
                        f"\tNo default value provided for state '{field['name']}'"
                    )
                if field["default_value"] is None:
                    continue
                if not self.is_number(field["default_value"]):
                    field["actual_value"] = self.validate_constant_references(
                        field["default_value"], "int32", directory_constants_list
                    )
                else:
                    field["type"] = "int32"
                    self.resolve_default_value(field)

    """
    ====================================================================================================
                                            HELPER FUNCTIONS
    ====================================================================================================
    """

    def resolve_default_value(self, node):

        resolvedValue = node["default_value"]
        resolvedType = node["type"]
        lineReference = node["line"]
        nameReference = node["name"]

        if resolvedType in parser.BUILTINS:
            bi_type = parser.BUILTINS[resolvedType]
            if not self.is_number(resolvedValue):
                raise ValueError(
                    f"In {self.fileName}, line {lineReference}:\n"
                    f"\tDefault Value '{resolvedValue}' is not a valid built in type value or Constant identifier for a default value of field '{nameReference}'"
                )
            if "int" in resolvedType or resolvedType == "bitfield":
                resolvedValue = int(resolvedValue)
            elif "float" in resolvedType:
                resolvedValue = float(resolvedValue)

            minVal = bi_type["min"]
            maxVal = bi_type["max"]

            if resolvedType == "bitfield":
                minVal = 0
                maxVal = 2 ** int(node["count"]) - 1
                resolvedType = "bitFeild_size_" + node["count"]

            if resolvedValue < minVal or resolvedValue > maxVal:
                raise ValueError(
                    f"In {self.fileName}, line {lineReference}:\n"
                    f"{nameReference} value '{resolvedValue}' is out of range for type '{resolvedType}'"
                )
        # at this point the type should have been already validated in validate_type_names(),
        # so all we are showing here is that the default value calls out a identifier that is
        # not a constant identifier type
        else:
            raise ValueError(
                f"In {self.fileName}, line {lineReference}:\n"
                f"\tIdentifier '{resolvedType}' is not a valid Constant for a default value of field '{nameReference}'"
            )

    def validate_constant_references(
        self, referenceIdentifier, constantType, directory_constants_list
    ):
        for node in directory_constants_list:
            if node["name"] == referenceIdentifier and node["type"] == constantType:
                visitList = {}
                return self.validate_const_references_recursive(
                    node, visitList, directory_constants_list
                )
        raise ValueError(
            f"In {self.fileName}:\n"
            f"\tConstant identifier '{referenceIdentifier}' is not a known symbol"
        )

    def validate_const_references_recursive(
        self, currNode, visitList, directory_constants_list
    ):
        if id(currNode) in visitList.keys():
            raise ValueError(
                f"In {self.fileName}, line {currNode['line']}:\n"
                f"\tCircular reference detected in constant identifier '{currNode['name']}'"
            )

        visitList[id(currNode)] = True

        # if the default value is numeric type, resolve it
        if self.is_number(currNode["default_value"]):
            self.resolve_default_value(currNode)
            return currNode["default_value"]
        # get next node and perform recursive check
        for node in directory_constants_list:
            if node["name"] != currNode["default_value"]:
                continue
            currNode["actual_value"] = self.validate_const_references_recursive(
                node, visitList, directory_constants_list
            )
            return currNode["actual_value"]

        # if we reach here, the constant identifier is not a known symbol
        raise ValueError(
            f"In {self.fileName}, line {currNode['line']}:\n"
            f"\tConstant identifier '{currNode['default_value']}' is not a known symbol"
        )

    def create_padding_field(self, message, bfBitSize, prevName):
        # calculate padding size
        totalSize = bfBitSize
        while totalSize % 8 != 0:
            totalSize += 1

        padSize = totalSize - bfBitSize

        # create padding field
        return {
            "name": self.get_open_padding_name(message),
            "type": "bitfield",
            "count": padSize,
            "default_value": None,
            "line": message["line"],
            parser.PW: prevName,
        }

    def get_open_padding_name(self, message):
        """
        Get the name of the open pad in the message
        """
        name = f"__{message['name']}_{self.PAD_NAME}_{message[self.PAD_PARAM_COUNT]}"
        message[self.PAD_PARAM_COUNT] += 1
        return name

    def get_open_bitField_name(self, message, templateName=BITFIELD_NAME):
        """
        Get the name of the open pad in the message
        """
        name = f"{templateName}_{message[self.BITFIELD_NAME_COUNT]}"
        message[self.BITFIELD_NAME_COUNT] += 1
        if parser.PW not in message["fields"]:
            return name

        while name not in [field[parser.PW] for field in message["fields"]]:
            name = f"reserved_{message[self.BITFIELD_NAME_COUNT]}"
            message[self.BITFIELD_NAME_COUNT] += 1
        return name

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
