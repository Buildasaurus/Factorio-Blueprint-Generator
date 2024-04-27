# Standard imports
from typing import List



class Node:
    def __init__(self, position: List["tuple"]):
        self.position = position
        self.visited = False
        self.is_start_node = False
        self.is_end_node = False

    def heuristic_function(self, node):
        """
        function to describe how close a node is to the end node
        """
        pass

    def set_parent(self, parent_node):
        """
        For later backtracing
        """
        self.parent = parent_node

    def weight_between_nodes(self, start_node, end_node):
        """
        Will calculate the weight between the given nodes.
        In most cases just a constant, but more expensive with undergroundbelts, to avoid unessecary use.
        """
        pass
