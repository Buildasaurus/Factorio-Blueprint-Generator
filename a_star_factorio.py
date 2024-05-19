# Standard imports
import logging
import math
import random
from typing import List

# First party imports
from vector import Vector

from layout import ConstructionSite

from node import Node



#
#  Logging
#
log = logging.getLogger(__name__)



# for implementation:
# https://academy.finxter.com/python-a-search-algorithm/
class A_star:
    def __init__(
        self,
        site: ConstructionSite,
        start_positions: List["tuple"],
        end_positions: List["tuple"],
    ):
        if not isinstance(site, ConstructionSite):
            raise TypeError("site must be an instance of ConstructionSite")
        if not isinstance(start_positions, list) or not all(isinstance(i, tuple) for i in start_positions):
            raise TypeError("start_positions must be a list of tuples")
        if not isinstance(end_positions, list) or not all(isinstance(i, tuple) for i in end_positions):
            raise TypeError("end_positions must be a list of tuples")

        self.site = site
        self.start_positions = start_positions
        self.end_positions = end_positions
        self.underground_belts = False
        self.queue = []
        # creates a grid of all nodes.
        height = site.size()[1]
        width = site.size()[0]
        self.nodes = [
            [Node((x, y)) for x in range(width)] for y in range(height)]
        log.debug("Nodes initialized")
        for position in start_positions:
            self.nodes[position[1]][position[0]].set_as_start_node()
            self.queue.append(self.nodes[position[1]][position[0]])
        log.debug("Start nodes initialized")

        for position in end_positions:
            self.nodes[position[1]][position[0]].set_as_end_node()
        log.debug("End nodes initialized")

    def find_entrance_node(self, current_node: 'Node', exit_node: 'Node') -> 'Node':
        normalized_direction = self.find_normalized_direction(current_node,exit_node)
        return self.nodes[current_node.position[1] + normalized_direction[1]][current_node.position[0] + normalized_direction[0]]

    def find_normalized_direction(self, current_node: 'Node', exit_node: 'Node') -> 'tuple':
        distance = (exit_node.position[0]- current_node.position[0], exit_node.position[1]-current_node.position[1])
        return (distance[0]//abs(distance[0]) if distance[0] != 0 else 0, distance[1]//abs(distance[1]) if distance[1] != 0 else 0)


    def find_path(self, underground_belts=False, visualizer = None) -> List['Node']:
        """
        Runs the A* algorithm
        """
        log.debug("finding path")
        self.underground_belts = underground_belts

        # Initialize the open and closed lists
        open_list: List['Node'] = self.queue.copy()
        closed_list: List['Node'] = []
        if visualizer != None:
            visualizer.set_closed_list(closed_list)
            visualizer.set_open_list(open_list)
            visualizer.set_start_squares(self.start_positions)
            visualizer.set_end_squares(self.end_positions)
        while open_list:
            # Get the node in the open list with the lowest f score (f = g + h)
            current_node = min(open_list, key=lambda node: node.cost_to_node + node.heuristic_function(self.end_positions))
            if current_node.is_underground_exit:
                log.debug("Underground used")
            # Move the current node from the open list to the closed list
            open_list.remove(current_node)
            closed_list.append(current_node)

            # If the current node is an end node, we've found a path
            if current_node.is_end_node:
                return self.backtrace(current_node, path_visualizer=visualizer)

            neighbors = self.get_neighbors(current_node, closed_list)
            for neighbor in neighbors:
                if neighbor in closed_list:
                    continue  # Ignore this neighbor since it's already been evaluated

                # Calculate the tentative g score for the neighbor
                if neighbor.is_observed_as_underground_exit:
                    # start node have weird underground neigbors - look at the neighbor function
                    if current_node.is_start_node and neighbor.distance(neighbor.position, current_node.position) < 6:
                        # if the distance is 6, it is too far for direct underground, thus this must be the edge case described
                        # by the neighbor function
                        cost_to_neighbor = current_node.cost_to_node + current_node.weight_between_nodes(current_node, neighbor)
                        if cost_to_neighbor <= neighbor.cost_to_node:
                            # This path is the best so far, so record it. Also record if the
                            # Node was an underground node, then tell it to store it.
                            neighbor.set_parent(current_node, True)
                            neighbor.cost_to_node = cost_to_neighbor
                    else:
                        underground_entry_node = self.find_entrance_node(current_node,neighbor)
                        cost_to_neighbor = underground_entry_node.cost_to_node + underground_entry_node.weight_between_nodes(underground_entry_node, neighbor)
                        if cost_to_neighbor <= neighbor.cost_to_node:
                            # This path is the best so far, so record it. Also record if the
                            # Node was an underground node, then tell it to store it.
                            neighbor.set_parent(underground_entry_node, True)
                            underground_entry_node.set_parent(current_node, False)
                            neighbor.cost_to_node = cost_to_neighbor

                else:
                    cost_to_neighbor = current_node.cost_to_node + current_node.weight_between_nodes(current_node, neighbor)
                    if cost_to_neighbor <= neighbor.cost_to_node:
                        # This path is the best so far, so record it. Also record if the
                        # Node was an underground node, then tell it to store it.

                        neighbor.set_parent(current_node, False)
                        neighbor.cost_to_node = cost_to_neighbor


                if neighbor not in open_list:
                    # This neighbor hasn't been evaluated yet, so add it to the open list
                    open_list.append(neighbor)
            if visualizer:
                visualizer.show_frame()

        return None  # No path was found

    def get_neighbors(self, node: 'Node', illegal_nodes: List['Node']) -> List['Node']:
        """
        Asks the Constructionside whether non-visited tiles directly around it has been visited.

        Also uses self.undergroundbelts to possibly check neighbors further away. A possible underground
        neighbor, is a neighbor at a distance [(2)3-6] blocks away from current node in a straight line. The node
        directly next to the current node, must be empty in that direction, as must the exit node.
        Note - while an underground to a node two nodes away is possible, it is a waste of underground, as the result
        would be the same as just two normal belts
        An underground belt will start one node away from the current node, and terminate up to 6 nodes away.

        example of underground belt:

        c i x x x x o

        where c is the current node, i is underground belt in, x is any block, o is underground belt out.


        If a node is a startnode, so where the path starts, a direct underground is allowed in the following fashion:
        i x x x x o

        As we then don't need to worry about the parent of the belt being in the right spot, as there is no parent.
        It is however still possible for a startnode to reach nodes 1 further away than the underground belts distance
        by using the same technique above. So start nodes have all the following underground neighbors.
        i x n n n n n
        Desipite the last neigbour being too far away, since it then could reach it by placing a normal belt fist.
        """

        neighbors = []
        if node.is_underground_exit:
            direction = self.find_normalized_direction(node.parent, node)
            x, y = node.position[0] + direction[0], node.position[1] + direction[1]
            self.nodes[y][x].is_observed_as_underground_exit = False
            neighbors.append(self.nodes[y][x])
        else:
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Up, Right, Down, Left
            for dx, dy in directions:
                x, y = node.position[0] + dx, node.position[1] + dy

                if not self.site.is_reserved(x,y) and self.is_in_bounds(x,y,self.nodes):
                    # Normal neighbors
                    neighbors.append(self.nodes[y][x])
                    # Some nodes might previously have been set to underground neighbors
                    # But if we can see them normally now, then they shouldn't be.
                    self.nodes[y][x].is_observed_as_underground_exit = False

                    # Underground neighbors
                    # Requires that the adjacent neighbor is empty for underground entry
                    # Also required taht the neighbor isn't the parent of the current node. Otherwise infinite loops
                    # will be created as that node again now will be the child of this node, which will eat all your ram.
                    if self.underground_belts and not node.is_start_node: # start nodes handled below
                        for underground_distance in [3,4,5,6]:
                            nx, ny = (node.position[0] + dx*underground_distance,
                                                    node.position[1] + dy*underground_distance)
                            # each possible distance to the underground exit
                            # The entry and exit should be empty. The entry and exit must not be illegal (in closed list)
                            if not self.site.is_reserved(nx,ny) and self.is_in_bounds(nx,ny,self.nodes) and not illegal_nodes.__contains__(self.nodes[y][x]) and not self.site.is_reserved(x,y):
                                neighbors.append(self.nodes[ny][nx])
                                self.nodes[ny][nx].is_observed_as_underground_exit = True

                # Start node underground nodes
                if self.underground_belts and node.is_start_node: # if we are at a start node, it is allowed and preferred to do a direct underground
                    # This must therefore also be checked when using neighbors
                    for underground_distance in [2,3,4,5]:
                        nx, ny = (node.position[0] + dx*underground_distance,
                                                node.position[1] + dy*underground_distance)
                        # each possible distance to the underground exit
                        # The entry and exit should be empty. The entry and exit must not be illegal (in closed list)
                        if not self.site.is_reserved(nx,ny) and self.is_in_bounds(nx,ny,self.nodes):
                            neighbors.append(self.nodes[ny][nx])
                            self.nodes[ny][nx].is_observed_as_underground_exit = True

                    nx, ny = (node.position[0] + dx*6, node.position[1] + dy*6)
                    # Add 6th distance as usual
                    if not self.site.is_reserved(nx,ny) and self.is_in_bounds(nx,ny,self.nodes) and not illegal_nodes.__contains__(self.nodes[y][x]) and not self.site.is_reserved(x,y):
                            neighbors.append(self.nodes[ny][nx])
                            self.nodes[ny][nx].is_observed_as_underground_exit = True





        return neighbors

    def is_in_bounds(self, x, y, map):
        return x >= 0 and y >= 0 and x < len(map[0]) and y < len(map)

    def backtrace(self, node, path_visualizer = None):
        """
        Backtrace a path from the end position to the start position

        Note for implementation (delete later):
        Goes to the parent of each node, and saves it to a list
        """
        path = []
        while node is not None:
            if path_visualizer != None:
                path_visualizer.show_frame(path)
            path.append((node.position[0], node.position[1]))
            node = node.parent
        return path[::-1]  #Reversed reversed path = normal path
