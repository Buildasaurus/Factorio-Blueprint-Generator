# Standard imports
import math
import random
from typing import List

# First party imports
from vector import Vector

from layout import ConstructionSite

from node import Node



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
        print("Nodes initialized")
        for position in start_positions:
            self.nodes[position[1]][position[0]].set_as_start_node()
            self.queue.append(self.nodes[position[1]][position[0]])
        print("Start nodes initialized")

        for position in end_positions:
            self.nodes[position[1]][position[0]].set_as_end_node()
        print("End nodes initialized")

    def find_path(self, underground_belts=False) -> List['Node']:
        """
        Runs the A* algorithm
        """
        print("finding path")
        self.underground_belts = underground_belts

        # Initialize the open and closed lists
        open_list = self.queue.copy()
        closed_list = []

        while open_list:
            # Get the node in the open list with the lowest f score (f = g + h)
            current_node = min(open_list, key=lambda node: node.cost_to_node + node.heuristic_function(self.end_positions))
            if current_node.is_underground_exit:
                print("Underground used")
            # Move the current node from the open list to the closed list
            open_list.remove(current_node)
            closed_list.append(current_node)

            # If the current node is an end node, we've found a path
            if current_node.is_end_node:
                return self.backtrace(current_node)

            neighbors = self.get_neighbors(current_node)
            for neighbor in neighbors:
                if neighbor in closed_list:
                    continue  # Ignore this neighbor since it's already been evaluated

                # Calculate the tentative g score for the neighbor
                cost_to_neighbor = current_node.cost_to_node + current_node.weight_between_nodes(current_node, neighbor)

                if neighbor not in open_list:
                    # This neighbor hasn't been evaluated yet, so add it to the open list
                    open_list.append(neighbor)
                elif cost_to_neighbor >= neighbor.cost_to_node:
                    # This is not a better path, so ignore this neighbor
                    continue

                # This path is the best so far, so record it. Also record if the
                # Node was a underground node, then tell it to store it.
                neighbor.set_parent(current_node, neighbor.is_observed_as_underground_exit)
                neighbor.cost_to_node = cost_to_neighbor


        return None  # No path was found



    def get_neighbors(self, node: 'Node') -> List['Node']:
        """
        Asks the Constructionside whether non-visited tiles directly around it has been visited.

        Also uses self.undergroundbelts to possibly check neighbors further away. A possible underground
        neighbor, is a neighbor at a distance [(2)3; 6] blocks away from current node in a straight line. The node
        directly next to the current node, must be empty in that direction, as must the exit node.
        Note - while a underground to a node two nodes away is possible, it is a waste of underground, as the result
        would be the same as just two normal belts
        An underground belt will start one node away from the current node, and terminate up to 6 nodes away.

        example of underground belt:

        c i x x x x o

        where c is the current node, i is undergruondbelt in, x is any block, o is underground belt out.
        """

        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Up, Right, Down, Left
        for dx, dy in directions:
            x, y = node.position[0] + dx, node.position[1] + dy
            if not self.site.is_reserved(x,y):
                # Normal neighbors
                neighbors.append(self.nodes[y][x])
                # Some nodes might previously have been set to underground neighbors
                # But if we can see them normally now, then they shouldn't be.
                self.nodes[y][x].is_observed_as_underground_exit = False

                # Underground neighbors (also require that the adjacent neighbor is empty for underground entry)
                if(self.underground_belts):
                    for under_ground_distance in [3,4,5,6]:
                        nx, ny = (node.position[0] + dx*under_ground_distance,
                                                node.position[1] + dy*under_ground_distance)
                        # each possible distance to the underground exit
                        if not self.site.is_reserved(nx,ny) and self.is_in_bounds(nx,ny,self.nodes):
                            neighbors.append(self.nodes[ny][nx])
                            self.nodes[ny][nx].is_observed_as_underground_exit = True




        return neighbors

    def is_in_bounds(self, x, y, map):
        return x >= 0 and y >= 0 and x < len(map[0]) and y < len(map)

    def backtrace(self, node):
        """
        Backtraces a path from the end position to the start position

        Note for implementation (delete later):
        Goes to the parent of each node, and saves it to a list
        """
        path = []
        while node is not None:
            path.append((node.position[0], node.position[1]))
            node = node.parent
        return path[::-1]  #Reversed reversed path = normal path
