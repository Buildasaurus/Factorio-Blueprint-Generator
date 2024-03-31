
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

from pathfinding.finder.finder import BY_END, Finder, MAX_RUNS, TIME_LIMIT
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.heuristic import manhattan, octile
from pathfinding.core.util import backtrace, bi_backtrace

def my_find_path(self, start: List[GridNode], end: List[GridNode], grid):

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
        open_list.push_node(start[node_index])
        start[node_index].opened = True

    while len(open_list) > 0:
        self.runs += 1
        self.keep_running()

        path = self.check_neighbors(start, end, grid, open_list)
        if path:
            return path, self.runs

    # failed to find path
    return [], self.runs


def a_star_find_path(self, start: List[GridNode], end: List[GridNode], graph):
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

def my_check_neighbors(self, start, end: List[GridNode], graph, open_list,
                        open_value=True, backtrace_by=None):
    """
    find next path segment based on given node
    (or return path if we found the end)

    :param start: start node
    :param end: end node
    :param grid: grid that stores all possible steps/tiles as 2D-list
    :param open_list: stores nodes that will be processed next
    """
    # pop node with minimum 'f' value
    node = open_list.pop_node()
    node.closed = True

    # if reached the end position, construct the path and return it
    # (ignored for bi-directional a*, there we look for a neighbor that is
    #  part of the oncoming path)
    if not backtrace_by and node in end:
        return backtrace(node)

    # get neighbors of the current node
    neighbors = self.find_neighbors(graph, node)
    for neighbor in neighbors:
        if neighbor.closed:
            # already visited last minimum f value
            continue
        if backtrace_by and neighbor.opened == backtrace_by:
            # found the oncoming path
            if backtrace_by == BY_END:
                return bi_backtrace(node, neighbor)
            else:
                return bi_backtrace(neighbor, node)

        # check if the neighbor has not been inspected yet, or
        # can be reached with smaller cost from the current node
        self.process_node(
            graph, neighbor, node, end, open_list, open_value)

    # the end has not been reached (yet) keep the find_path loop running
    return None

def my_process_node(
        self, graph, node, parent, end, open_list, open_value=True):
    '''
    we check if the given node is part of the path by calculating its
    cost and add or remove it from our path
    :param node: the node we like to test
        (the neighbor in A* or jump-node in JumpPointSearch)
    :param parent: the parent node (of the current node we like to test)
    :param end: the end point to calculate the cost of the path
    :param open_list: the list that keeps track of our current path
    :param open_value: needed if we like to set the open list to something
        else than True (used for bi-directional algorithms)

    '''
    # calculate cost from current node (parent) to the next node (neighbor)
    ng = parent.g + graph.calc_cost(parent, node, self.weighted)

    if not node.opened or ng < node.g:
        old_f = node.f
        node.g = ng
        node.h = node.h or self.apply_heuristic(node, GridNode(sum([node.x for node in end])/len(end), sum([node.y for node in end])/len(end)))
        # f is the estimated total cost from start to goal
        node.f = node.g + node.h
        node.parent = parent
        if not node.opened:
            open_list.push_node(node)
            node.opened = open_value
        else:
            # the node can be reached with smaller cost.
            # Since its f value has been updated, we have to
            # update its position in the open list
            open_list.remove_node(node, old_f)
            open_list.push_node(node)

Finder.process_node = my_process_node
AStarFinder.check_neighbors = my_check_neighbors
Finder.find_path = my_find_path
AStarFinder.find_path = a_star_find_path
