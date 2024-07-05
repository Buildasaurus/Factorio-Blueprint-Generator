# Standard imports
from typing import List
from math import sqrt


class Node:
    def __init__(self, position: 'tuple'):
        self.position = position
        self.visited = False
        self.is_start_node = False
        self.is_end_node = False
        self.cost_to_node = 999999999
        self.stored_heuristic = -1
        self.parent = None
        self.is_underground_exit = False
        self.is_observed_as_underground_exit = False
        self.illegal_neighbors = []

    def heuristic_function(self, end_node: List["tuple"]):
        """
        function to describe how close a node is to the end node
        """
        if self.stored_heuristic != -1:
            return self.stored_heuristic
        else:
            min_distance = 99999999
            for possible_end_node in end_node:
                distance = self.distance(possible_end_node, self.position)
                if(distance < min_distance):
                    min_distance = distance
            self.stored_heuristic = min_distance
            return self.stored_heuristic

    def set_parent(self, parent_node, is_underground_exit):
        """
        For later backtracing
        """
        self.parent = parent_node
        self.is_underground_exit = is_underground_exit

    def weight_between_nodes(self, start_node: 'Node', end_node: 'Node'):
        """
        Will calculate the weight between the given nodes.
        In most cases just a constant, but more expensive with undergroundbelts, to avoid unessecary use.

        Doesn't care about length of the underground belt, to incentivize longer
        underground belts, when finally used
        """
        distance = self.distance((start_node.position[0],start_node.position[1]),
                                 (end_node.position[0],end_node.position[1]))
        if distance <= 1:
            return 1
        else:
            return 7

    def distance(self, node1: 'tuple', node2: 'tuple'):
        '''
        Calculates the distance between two coordinates
        '''
        return sqrt((node1[0]-node2[0])**2 + (node1[1] - node2[1])**2)

    def set_as_start_node(self):
        self.is_start_node = True
        self.cost_to_node = 0
        pass

    def add_illegal_neighbor(self, neighbor: 'tuple'):
        self.illegal_neighbors.append(neighbor)

    def get_illegal_neighbors(self) -> List['tuple']:
        return self.illegal_neighbors

    def set_as_end_node(self):
        self.is_end_node = True
        pass
