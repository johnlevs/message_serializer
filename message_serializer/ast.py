import json
import copy

import logging

from message_serializer.lexerConfig import BUILTINS, CONST, STATE, STATEFIELD

logger = logging.getLogger("message_serializer")


class ast:
    CHILDREN = {
        "MSG": "fields",
        STATE: "fields",
        "module": "elements",
        "directory": "modules",
    }

    def __init__(self, jsonTree):
        self.tree = jsonTree
        self.__print_order = self.validate()

    """===================================================================================================
                                                    VALIDATION
        =================================================================================================="""

    def link_references(self):

        def add_dependency(element, dependency):
            if "dependencies" not in element:
                element["dependencies"] = []
            element["dependencies"].append(dependency)

        def check_and_add_dependency(attribute, element, dependant):
            if (
                attribute in element
                and not is_number(element[attribute])
                and element[attribute] is not None
            ):
                ref = self.find_member_reference(element[attribute], element)
                if ref is None:
                    raise ValueError(
                        f"in file {self.element_file_name(element)}, line {element['line']}:\n"
                        + f"\tCould not find {attribute} {element[attribute]}"
                    )
                element[attribute] = ref
                if self.get_type(ref) == STATEFIELD or self.get_type(ref) == "MSG":
                    ref = ref["parent"]

                add_dependency(dependant, ref)

        for element in self.__leaf_node_iterator():

            dependant = (
                element["parent"]
                if element["parent"]["type"] == "MSG"
                or element["parent"]["type"] == STATE
                else element
            )

            # check types
            if element["type"] not in BUILTINS.keys():
                e_type = self.find_member_reference(element["type"], element)
                if e_type is None:
                    raise ValueError(
                        f"in file {self.element_file_name(element)}, line {element['line']}:\n"
                        + f"\tUnknown type reference: {element['type']}"
                    )
                add_dependency(dependant, e_type)
                element["type"] = e_type
            else:
                element["type"] = BUILTINS[element["type"]]

            for attribute in ["default_value", "count"]:
                check_and_add_dependency(attribute, element, dependant)

    def validate(self):

        # validate variable naming
        self.validate_names()
        # link references
        self.link_references()

        # topological sort. Circular dependencies checked here
        print_order = []

        def visit(element, visited, stack):
            if id(element) in visited:
                if id(element) in stack:
                    raise ValueError(
                        f"in file {self.element_file_name(element)}, line {element['line']}:\n"
                        f"\tCircular dependency detected in element {element['name']}"
                    )
                return

            visited.add(id(element))
            stack.add(id(element))
            if "dependencies" in element:
                for dependency in element["dependencies"]:
                    visit(dependency, visited, stack)
            stack.remove(id(element))
            print_order.append(element)

        visited = set()
        stack = set()
        for element in self.__printable_type_iterator():
            visit(element, visited, stack)

        print_order
        # cleanup
        for element in print_order:
            element.pop("dependencies", None)
            element.pop("p", None)
            element.pop("t", None)

        return print_order

    def validate_names(self):
        nodeList = [node for node in self.tree["modules"]]
        names = []
        for node in nodeList:
            if node["name"] in names:
                raise ValueError(
                    f"In File {self.element_file_name(node)}, line {node['line']}:\n"
                    f"Duplicate element names: {node['name']}"
                )
            else:
                names.append(node["name"])
        for node in nodeList:
            self.__validate_names_recursive(node)

    def __validate_names_recursive(self, element):
        childAccess = self.get_child_accessor(element)
        if childAccess is None or childAccess not in element:
            return
        nodeList = element[childAccess]
        names = []
        for node in nodeList:
            if node["name"] in names:
                raise ValueError(
                    f"In File {self.element_file_name(node)}, line {node['line']}:\n"
                    + f"Duplicate element names: {node['name']}"
                )
            else:
                names.append(node["name"])
        for node in nodeList:
            self.__validate_names_recursive(node)

    """===================================================================================================
                                                    GETTERS
        =================================================================================================="""

    def get_child_accessor(self, element):
        e_type = element["type"]
        if isinstance(element["type"], dict) or e_type not in self.CHILDREN.keys():
            return None
        return self.CHILDREN[element["type"]]

    def get_child(self, element):
        child = self.get_child_accessor(element)
        if child is None:
            return None
        return element[child]

    def get_type(self, element):
        e_type = element["type"]
        if isinstance(e_type, dict):
            return e_type["name"]
        return e_type

    def dfs(self, element, searchName):
        logging.debug(f"Searching for {searchName} in {element['name']}")
        child = self.get_child_accessor(element)
        if child is None or child not in element:
            return
        for childElement in element[child]:
            if childElement["name"] == searchName:
                return childElement
            dfs = self.dfs(childElement, searchName)
            if dfs is not None:
                return dfs

    def find_member_reference(self, searchName, startingElement):
        if "parent" not in startingElement:
            logger.warning(f"Could not find {searchName} in {startingElement['name']}")
            return None
        parent = startingElement["parent"]
        logging.debug(f"Searching for {searchName} in {parent['name']}")
        parentChild = self.get_child_accessor(parent)
        for element in parent[parentChild]:
            logging.debug(f"Checking in {element['name']}")
            if id(element) == id(startingElement):
                continue
            if element["name"] == searchName:
                return element
            childSearch = self.dfs(element, searchName)
            if childSearch is not None:
                return childSearch
        return self.find_member_reference(searchName, parent)

    def element_file_name(self, element):
        if "filename" in element:
            return element["filename"]
        return self.element_file_name(element["parent"])

    """===================================================================================================
                                                    ITERATORS
        =================================================================================================="""

    def __str__(self):
        return json.dumps(self.__print_order, indent=4)

    def jsonPrint(self, outFile):
        for element in self.__depth_first_iterator():
            if "parent" in element.keys():
                del element["parent"]
        return json.dump(self.__print_order, outFile)

    def __depth_first_iterator(self):
        nodeList = [node for node in self.tree["modules"]]
        while len(nodeList) > 0:
            node = nodeList.pop(0)
            childAccess = self.get_child_accessor(node)
            if childAccess is not None and childAccess in node:
                nodeList = node[childAccess] + nodeList
            yield node

    def __leaf_node_iterator(self):
        for node in self.__depth_first_iterator():
            if self.get_child_accessor(node) is None:
                yield node

    def __printable_type_iterator(self):
        for node in self.__depth_first_iterator():
            if node["type"] in [CONST, "MSG", STATE]:
                yield node

    def print_order_iterator(self):
        for node in self.__print_order:
            yield node

    def message_iterator(self):
        for node in self.__print_order:
            if node["type"] == "MSG":
                yield node

    """===================================================================================================
                                                    HELPERS
    =================================================================================================="""


def is_number(s):
    try:
        float(s)
        return True
    except Exception:
        return False
