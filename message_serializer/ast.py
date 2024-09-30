import json
import copy

import logging

logger = logging.getLogger("message_serializer")


class ast:
    def __init__(self, jsonTree):
        self.tree = jsonTree
        self.sortedTree = self.__sort_tree()

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
        tree = self.sortedTree[module_ndx][element_name]
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

    def find_member(self, name):
        hierarchy = [None, None, None]
        for module_ndx, module in enumerate(self.sortedTree):

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

            ndx = self.__search_module_field(name, "messages", module_ndx)
            if ndx is not None:
                hierarchy[1] = ["messages", ndx]
                logging.debug(f"Found {name} in messages")
                return hierarchy
        
        logging.debug(f"Could not find {name}")

        return None
