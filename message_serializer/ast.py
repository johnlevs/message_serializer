import json
import copy

import logging

from message_serializer.lexerConfig import BUILTINS

logger = logging.getLogger("message_serializer")


class ast:
    def __init__(self, jsonTree):
        self.tree = jsonTree
        self.tree = self.__sort_tree()
        self.messages_sorted = self.topological_message_sort()
        self.constants_sorted = self.topological_const_sort()

    def __str__(self):
        return json.dumps(self.tree, indent=4)

    def __sort_tree(self):
        sortedTree = []
        for module in copy.deepcopy(self.tree):
            sortedModule = {}
            sortedModule["name"] = module["name"]
            sortedModule["constants"] = sorted(
                module["constants"], key=lambda x: x["name"]
            )
            sortedModule["states"] = sorted(module["states"], key=lambda x: x["name"])
            sortedModule["messages"] = sorted(
                module["messages"], key=lambda x: x["name"]
            )
            for message in sortedModule["messages"]:
                message["fields"] = sorted(message["fields"], key=lambda x: x["name"])
            for states in sortedModule["states"]:
                states["fields"] = sorted(states["fields"], key=lambda x: x["name"])
            sortedTree.append(sortedModule)
        return sortedTree

    def __search_module_field(self, search_string, element_name, module_ndx):
        """
        performs a binary search on the sorted tree to find the element
        """
        if (
            element_name != "constants"
            and element_name != "states"
            and element_name != "messages"
        ):
            return None
        tree = self.tree[module_ndx][element_name]
        low = 0
        high = len(tree) - 1
        while low <= high:
            mid = (low + high) // 2
            if tree[mid]["name"] < search_string:
                low = mid + 1
            elif tree[mid]["name"] > search_string:
                high = mid - 1
            else:
                return mid
        return None

    def module_iterator(self):
        for module in self.tree:
            yield module

    def state_iterator(self):
        for module in self.module_iterator():
            for state in module["states"]:
                yield state

    def __message_iterator(self):
        for module in self.module_iterator():
            for message in module["messages"]:
                yield message

    def message_iterator(self):
        for message in self.messages_sorted:
            yield message

    def __constant_iterator(self):
        for module in self.module_iterator():
            for constant in module["constants"]:
                yield constant

    def constant_iterator(self):
        for constant in self.constants_sorted:
            yield constant

    def field_iterator(self):
        for message in self.__message_iterator():
            for field in message["fields"]:
                yield field

    def find_field(self, structure, name):
        ndx = 0
        for field in structure:
            if field["name"] == name:
                return ndx
            ndx += 1
        return None

    def find_member(self, name):
        hierarchy = [None, None, None]
        for module_ndx, module in enumerate(self.tree):

            logging.debug(f"Searching for {name} in module {module['name']}")

            hierarchy[0] = [module["name"], module_ndx]

            ndx = self.__search_module_field(name, "constants", module_ndx)
            if ndx is not None:
                hierarchy[1] = ["constants", ndx]
                logging.debug(f"Found {name} in constants")
                return hierarchy

            ndx = self.__search_module_field(name, "states", module_ndx)
            if ndx is not None:
                hierarchy[1] = ["states", ndx]
                logging.debug(f"Found {name} in states")
                return hierarchy
            for state in module["states"]:
                ndx = self.find_field(state["fields"], name)
                if ndx is not None:
                    hierarchy[1] = ["states", module["states"].index(state)]
                    hierarchy[2] = ["fields", ndx]
                    return hierarchy

            ndx = self.__search_module_field(name, "messages", module_ndx)
            if ndx is not None:
                hierarchy[1] = ["messages", ndx]
                logging.debug(f"Found {name} in messages")
                return hierarchy

        logging.debug(f"Could not find {name}")

        return None

    def find_member_reference(self, name):
        hierarchy = self.find_member(name)
        if hierarchy is None:
            return None

        if hierarchy[1] is None:
            return self.tree[hierarchy[0][1]]

        if hierarchy[2] is None:
            return self.tree[hierarchy[0][1]][hierarchy[1][0]][hierarchy[1][1]]

        if hierarchy[2] is not None:
            return self.tree[hierarchy[0][1]][hierarchy[1][0]][hierarchy[1][1]][
                hierarchy[2][0]
            ][hierarchy[2][1]]
            

    def topological_message_sort(self):
        return self.__topological_sort(
            self.field_iterator,
            self.__message_iterator,
            lambda field: field["parent"],
        )

    def topological_const_sort(self):
        return self.__topological_sort(
            self.__constant_iterator,
            self.__constant_iterator,
            lambda field: field,
        )


    def __topological_sort(
        self, dependency_cmp_iterator, element_iterator, storage_element_accessor
    ):
        # assign all dependencies
        for element in dependency_cmp_iterator():
            if element["type"] in BUILTINS:
                continue
            dependency = self.find_member_reference(element["type"])
            if dependency is None:
                raise ValueError(f"Could not find {element['type']}")
            if "dependencies" not in storage_element_accessor(element):
                storage_element_accessor(element)["dependencies"] = []

            storage_element_accessor(element)["dependencies"].append(dependency)

            if "dependents" not in dependency:
                dependency["dependents"] = []
            dependency["dependents"].append(storage_element_accessor(element))

        # create list of elements with no incoming dependencies (edges)
        no_depends = [
            element for element in element_iterator() if "dependents" not in element
        ]

        sorted_list = []
        for element in no_depends:
            sorted_list.append(element)
            if "dependencies" not in element:
                continue
            for dependency in element["dependencies"]:
                dependency["dependents"].remove(element)
                if "dependents" not in dependency or len(dependency["dependents"]) == 0:
                    no_depends.append(dependency)
                    if "dependents" in dependency:
                        del dependency["dependents"]
            del element["dependencies"]

        for element in element_iterator():
            if "dependents" in element:
                raise ValueError(f"Circular dependency detected in {element['name']}")


        sorted_list.reverse()
        return sorted_list
