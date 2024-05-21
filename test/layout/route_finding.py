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

    def test_automated_3(self):
        '''
        This test provokes too far underground belts.
        '''
        print("AssemblingMachine1(electronic_circuit) and AssemblingMachine1(assembling_machine_1)")
        width = 64
        height = 64
        site = layout.ConstructionSite(width, height)
        source = solver.FakeMachine(Vector(18, 37), (3,3))
        target = solver.FakeMachine(Vector(30, 41), (3,3))

        # Drawing flipped on its head
        coordinates = [(9, 2), (21, 2), (14, 4), (15, 4), (16, 4), (14, 5), (15, 5), (16, 5), (14, 6), (15, 6), (16, 6), (20, 9), (21, 9), (22, 9), (20, 10), (21, 10), (22, 10), (20, 11), (21, 11), (22, 11), (29, 13), (36, 13), (37, 13), (38, 13), (36, 14), (37, 14), (38, 14), (36, 15), (37, 15), (38, 15), (31, 18), (32, 18), (33, 18), (28, 19), (29, 19), (30, 19), (31, 19), (32, 19), (33, 19), (28, 20), (29, 20), (30, 20), (31, 20), (32, 20), (33, 20), (28, 21), (29, 21), (30, 21), (36, 22), (37, 22), (38, 22), (36, 23), (37, 23), (38, 23), (36, 24), (37, 24), (38, 24), (38, 25), (38, 26), (39, 26), (29, 27), (30, 27), (31, 27), (39, 27), (29, 28), (30, 28), (31, 28), (39, 28), (29, 29), (30, 29), (31, 29), (39, 29), (40, 29), (41, 29), (30, 30), (39, 30), (40, 30), (41, 30), (60, 30), (13, 31), (30, 31), (36, 31), (39, 31), (40, 31), (41, 31), (42, 31), (43, 31), (30, 32), (32, 32), (41, 32), (43, 32), (46, 32), (47, 32), (48, 32), (30, 33), (41, 33), (43, 33), (46, 33), (47, 33), (48, 33), (30, 34), (41, 34), (42, 34), (43, 34), (46, 34), (47, 34), (48, 34), (52, 34), (53, 34), (54, 34), (27, 35), (30, 35), (42, 35), (43, 35), (52, 35), (53, 35), (54, 35), (30, 36), (37, 36), (38, 36), (39, 36), (40, 36), (41, 36), (42, 36), (43, 36), (52, 36), (53, 36), (54, 36), (18, 37), (19, 37), (20, 37), (30, 37), (36, 37), (37, 37), (43, 37), (12, 38), (13, 38), (14, 38), (18, 38), (19, 38), (20, 38), (30, 38), (35, 38), (36, 38), (43, 38), (12, 39), (13, 39), (14, 39), (18, 39), (19, 39), (20, 39), (22, 39), (23, 39), (24, 39), (30, 39), (32, 39), (33, 39), (34, 39), (35, 39), (43, 39), (44, 39), (45, 39), (48, 39), (49, 39), (50, 39), (12, 40), (13, 40), (14, 40), (22, 40), (23, 40), (24, 40), (30, 40), (32, 40), (43, 40), (44, 40), (45, 40), (48, 40), (49, 40), (50, 40), (53, 40), (54, 40), (55, 40), (22, 41), (23, 41), (24, 41), (25, 41), (26, 41), (27, 41), (28, 41), (29, 41), (30, 41), (31, 41), (32, 41), (43, 41), (44, 41), (45, 41), (48, 41), (49, 41), (50, 41), (53, 41), (54, 41), (55, 41), (12, 42), (13, 42), (14, 42), (28, 42), (29, 42), (30, 42), (31, 42), (32, 42), (53, 42), (54, 42), (55, 42), (12, 43), (13, 43), (14, 43), (27, 43), (28, 43), (29, 43), (30, 43), (31, 43), (32, 43), (12, 44), (13, 44), (14, 44), (27, 44), (30, 44), (31, 44), (32, 44), (41, 44), (42, 44), (43, 44), (25, 45), (26, 45), (27, 45), (30, 45), (31, 45), (32, 45), (33, 45), (34, 45), (35, 45), (36, 45), (37, 45), (38, 45), (39, 45), (41, 45), (42, 45), (43, 45), (61, 45), (9, 46), (16, 46), (17, 46), (18, 46), (25, 46), (26, 46), (27, 46), (30, 46), (31, 46), (37, 46), (38, 46), (39, 46), (41, 46), (42, 46), (43, 46), (16, 47), (17, 47), (18, 47), (25, 47), (26, 47), (27, 47), (28, 47), (30, 47), (31, 47), (37, 47), (38, 47), (39, 47), (46, 47), (16, 48), (17, 48), (18, 48), (28, 48), (30, 48), (31, 48), (32, 48), (33, 48), (26, 49), (27, 49), (28, 49), (30, 49), (32, 49), (26, 50), (27, 50), (28, 50), (30, 50), (32, 50), (33, 50), (34, 50), (35, 50), (36, 50), (37, 50), (38, 50), (39, 50), (40, 50), (26, 51), (27, 51), (28, 51), (30, 51), (38, 51), (39, 51), (40, 51), (30, 52), (31, 52), (32, 52), (38, 52), (39, 52), (40, 52), (30, 53), (31, 53), (32, 53), (30, 54), (31, 54), (32, 54)]
        for coordinat in coordinates:
            site.add_entity(INSERTER, (coordinat[0], coordinat[1]), 0)

        log.debug(f"On site that looks like this:\n {site} ")
        log.debug(f"Find path from (18, 37) to (30, 41)")
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
