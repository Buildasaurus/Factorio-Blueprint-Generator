
from pathfinding.core.node import GridNode
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.finder import Finder
from typing import List

import heapq  # used for the so colled "open list" that stores known nodes
import time  # for time limitation
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.heap import SimpleHeap

def my_find_path(self, start: List[GridNode], end, grid):

    """
    find a path from start to end node on grid by iterating over
    all neighbors of a node (see check_neighbors)
    :param start: start node
    :param end: end node
    :param grid: grid that stores all possible steps/tiles as 2D-list
    (can be a list of grids)
    :return:
    """
    self.start_time = time.time()  # execution time limitation
    self.runs = 0  # count number of iterations

    first_node = start[0]
    first_node.opened = True
    open_list = SimpleHeap(first_node, grid)
    for node_index in range (1,len(start)):
        open_list.push_node(start.get(node_index))
        start[node_index].opened = True

    while len(open_list) > 0:
        self.runs += 1
        self.keep_running()

        path = self.check_neighbors(start, end, grid, open_list)
        if path:
            return path, self.runs

    # failed to find path
    return [], self.runs


def a_star_find_path(self, start, end, graph):
        """
        find a path from start to end node on grid using the A* algorithm
        :param start: start node
        :param end: end node
        :param graph: graph or grid that stores all possible nodes
        :return:
        """
        for node in start:
            node.g = 0
            node.f = 0

        return super(AStarFinder, self).find_path(start, end, graph)

Finder.find_path = my_find_path
AStarFinder.find_path = a_star_find_path
