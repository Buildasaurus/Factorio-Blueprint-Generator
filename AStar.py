# Standard imports
import math
import random
from typing import List

# First party imports
from vector import Vector

from layout import ConstructionSite

# for implementation:
# https://academy.finxter.com/python-a-search-algorithm/

def __init__(self, site: ConstructionSite, start_positions: List['tuple'], end_positions: List['tuple']):
    self.site = site
    self.start_positions = start_positions
    self.end_positions = end_positions
    self.underground_belts = False


def find_path(self, underground_belts = False):
    '''
    Runs a modified version of A*
    '''
    self.underground_belts = underground_belts

def heuristic_function(self, node):
    '''
    function to calculate how expensive it is to travel to a node.
    Should put extra expense on using undergroundbelts, to avoid unessecary use.
    '''

def get_neighbors(self):
    '''
    Asks the Constructionside whether non-visited tiles directly around it has been visited.

    Also uses self.undergroundbelts to possibly check neighbors further away. A possible underground
    neighbor, is a neighbor at a distance (2)3-6 blocks away from current node in a straight line. The node
    directly next to the current node, must be empty in that direction, as must the exit node.
    Note - while a underground to a node two nodes away is possible, it is a waste of underground, as the result
    would be the same as just two normal belts
    An underground belt will start one node away from the current node, and terminate up to 6 nodes away.

    example of underground belt:

    c i x x x x o

    where c is the current node, i is undergruondbelt in, x is any block, o is underground belt out.
    '''
    pass

def backtrace(self):
    '''
    Backtraces a path from the end position to the start position

    Note for implementation (delete later):
    Goes to the parent of each node, and saves it to a list
    '''
    pass
