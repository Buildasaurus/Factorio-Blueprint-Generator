"""
Underground belts are important for complex layout of factories.
- some layout are impossible without underground belts
    - trapped machines
    - crossing a wide main-belt
- some layouts are cheaper with underground belts
    - long way around objects
"""

import logging
import unittest

import layout
import solver
from vector import Vector
from factoriocalc import CraftingMachine, Recipe

from test.astar.path_visuals import PathFindingVisuals

#
#  Logging
#

LOG_FILE = "fbg.log"


def config_logging():
    formatter = logging.Formatter(
        style="{", fmt="{asctime} {module} {levelname} {message}"
    )

    handler = logging.FileHandler(filename=LOG_FILE, mode="w", encoding="utf-8")
    handler.setFormatter(formatter)

    root_log = logging.getLogger()
    root_log.addHandler(handler)
    root_log.setLevel(logging.DEBUG)
    return root_log


log = config_logging()
log.info("unittest of route finding belts")

#
#  Game constants
#

WOOD_CHEST = "wooden-chest"
IRON_CHEST = "iron-chest"
BELT = "transport-belt"
INSERTER = "inserter"


#
#  Test
#


class TestRouteFinding(unittest.TestCase):
    """Cases with narrow paths"""

    def test_snake(self):
        """A snaky route from star to target
        The idea is as below. X means the spot is taken, b means a belt should be put there
        i is the in and output inserters

        x x x x b b b
        b b b x b x b
        b x b x b x b
        i x b x b x i
        s x b b b x t
        """
        width = 7
        height = 5
        site = layout.ConstructionSite(width, height)
        source = solver.Port()
        target = solver.Port()
        source.position = Vector(0, 0)
        target.position = Vector(6, 0)
        site.add_entity(WOOD_CHEST, source.position, 0)
        site.add_entity(IRON_CHEST, target.position, 0)

        belts = [
            [0, 1, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 1, 0],
            [1, 1, 1, 1, 0, 0, 0],
        ]
        for row in range(height):
            for column in range(width):
                if belts[row][column]:
                    site.add_entity(INSERTER, (column, row), 0)

        log.debug(f"On site that looks like this:\n{site}")
        log.debug(f"Find path from {source.position} to {target.position}")
        spring_visuals = PathFindingVisuals(width, height, site, fps=20)
        pos_list = solver.find_path(site, source, target, spring_visuals)
        log.debug(pos_list)
        self.assertEqual(len(pos_list), 19)

    def test_reroute_underground(self):
        """When you have to go back to go forwards

        x x x x x x x x
        x b e x o i t x
        x b x x x x x x
        x b b x x x x x
        x x b i s x x x
        x x x x x x x x
        """
        width = 8
        height = 6
        site = layout.ConstructionSite(width, height)
        source = solver.Port()
        target = solver.Port()
        source.position = Vector(4, 1)
        target.position = Vector(6, 4)
        site.add_entity(WOOD_CHEST, source.position, 0)
        site.add_entity(IRON_CHEST, target.position, 0)

        # Drawing flipped on it's head
        belts = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 1, 1, 1, 1, 1],
            [1, 0, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]
        for row in range(height):
            for column in range(width):
                if belts[row][column]:
                    site.add_entity(INSERTER, (column, row), 0)

        log.debug(f"On site that looks like this:\n{site}")
        log.debug(f"Find path from {source.position} to {target.position}")
        spring_visuals = PathFindingVisuals(width, height, site, fps=20)
        pos_list = solver.find_path(site, source, target, spring_visuals)
        log.debug(pos_list)
        self.assertEqual(len(pos_list), 9)

    def test_automated_2(self):
        ''' This demonstrates the problem when two assemblymachines are placed as follows:
        a a a x x a a a
        a a a x x a a a
        a a a x x a a a

        Where a is an assembly machine. The problem is that the start squares for the left assembly
        is right next to the end squares for the other machine. So the path just goes from 4th row (0 indexed) to the 3rd.
        But that is the spot for the inserter, so that movement is not allowed.
        '''
        print("AssemblingMachine2(copper_cable) and AssemblingMachine2(electronic_circuit)")
        width = 96
        height = 96
        site = layout.ConstructionSite(width, height)
        source = solver.FakeMachine(Vector(31, 46), (3,3))
        target = solver.FakeMachine(Vector(36, 46), (3,3))

        # Drawing flipped on its head
        coordinates = [(37, 39), (38, 39), (39, 39), (37, 40), (38, 40), (39, 40), (31, 41), (37, 41), (38, 41), (39, 41), (25, 46), (26, 46), (27, 46), (31, 46), (32, 46), (33, 46), (36, 46), (37, 46), (38, 46), (25, 47), (26, 47), (27, 47), (31, 47), (32, 47), (33, 47), (36, 47), (37, 47), (38, 47), (25, 48), (26, 48), (27, 48), (29, 48), (31, 48), (32, 48), (33, 48), (34, 48), (35, 48), (36, 48), (37, 48), (38, 48), (27, 49), (29, 49), (31, 49), (27, 50), (28, 50), (29, 50), (31, 50), (28, 51), (29, 51), (31, 51), (28, 52), (29, 52), (30, 52), (31, 52), (28, 53), (30, 53), (31, 53), (28, 54), (29, 54), (30, 54), (31, 54), (32, 54), (38, 54), (30, 55), (31, 55), (32, 55), (30, 56), (31, 56), (32, 56)]
        for coordinat in coordinates:
            site.add_entity(INSERTER, (coordinat[0], coordinat[1]), 0)

        log.debug(f"On site that looks like this:\n {site} ")
        log.debug(f"Find path from (31, 46) to (36, 46)")
        spring_visuals = PathFindingVisuals(width, height, site, fps=60 )
        pos_list = solver.connect_machines(site, source, target, spring_visuals)
        log.debug(pos_list)







# Test for later, this is hard, because now it has to explore the same node from different angels to find the right way.
def test_reroute_underground(self):
    """When you have to go back to go forwards, and have to come from the right direction

    x x x x x x x x
    x b e x o i t x
    x b b x x x x x
    x x b i s x x x
    x x x x x x x x
    """
    width = 8
    height = 5
    site = layout.ConstructionSite(width, height)
    source = solver.Port()
    target = solver.Port()
    source.position = Vector(4, 1)
    target.position = Vector(6, 3)
    site.add_entity(WOOD_CHEST, source.position, 0)
    site.add_entity(IRON_CHEST, target.position, 0)

    # Drawing flipped on it's head
    belts = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ]
    for row in range(height):
        for column in range(width):
            if belts[row][column]:
                site.add_entity(INSERTER, (column, row), 0)

    log.debug(f"On site that looks like this:\n{site}")
    log.debug(f"Find path from {source.position} to {target.position}")
    spring_visuals = PathFindingVisuals(width, height, site, fps=2)
    pos_list = solver.find_path(site, source, target, spring_visuals)
    log.debug(pos_list)
    self.assertEqual(len(pos_list), 7)
