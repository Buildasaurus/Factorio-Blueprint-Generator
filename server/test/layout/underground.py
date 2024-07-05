'''
Underground belts are important for complex layout of factories.
- some layout are impossible without underground belts
    - trapped machines
    - crossing a wide main-belt
- some layouts are cheaper with underground belts
    - long way around objects
'''

import logging
import unittest

import layout
import solver
from vector import Vector
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
log.info("unittest of underground belts")

#
#  Game constants
#

WOOD_CHEST = 'wooden-chest'
IRON_CHEST = 'iron-chest'
BELT = 'transport-belt'


#
#  Test
#

class Test_must_have_underground(unittest.TestCase):
    '''Cases where it would be impossible without an underground belt'''
    def test_main_belt(self):
        '''A main belt may be so wide that you need to surface to cross it'''
        # zero dip
        #     S  b  T (1)
        #     S  bbbb  T (4)
        # one dip
        #     S  bbbbb  T (4+1=5)
        #     S  bbbbbbbbbb  T (4+2+4=10)
        # two dip
        #     S  bbbbbbbbbb  T (10+1=11)
        #     S  bbbbbbbbbbbbbbbb  T (10+6=16)
        #
        for main_belt_width in [1, 4, 5, 10, 11, 16]:
            expected_dips = (main_belt_width + 1) // 6
            dim = (2+1+2+main_belt_width+2+1+2, 5)
            log.debug(f'Test main belt with {main_belt_width} - expect {expected_dips+1} underground sections')
            site = layout.ConstructionSite(*dim)
            row = dim[1] // 2
            source = solver.Port()
            target = solver.Port()
            source.position = Vector(2, row)
            target.position = Vector(dim[0]-2-1, row)
            site.add_entity(WOOD_CHEST, source.position, 0)
            site.add_entity(IRON_CHEST, target.position, 0)
            for b in range(main_belt_width):
                for row in range(dim[1]):
                    site.add_entity(BELT, (2+1+2+b, row), 0)
            log.debug(f'On site that looks like this:\n{site}')
            log.debug(f'Find path from {source.position} to {target.position}')
            spring_visuals = PathFindingVisuals(dim[0], dim[1], site, fps=10)
            pos_list = solver.find_path(site, source, target,spring_visuals)
            log.debug(pos_list)
            self.assertEqual(len(pos_list), 2+(expected_dips+1)*2)
