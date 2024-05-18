"""
    Testing if methods are correctly implemented
"""

import logging
import unittest

import layout
from a_star_factorio import A_star

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

WOOD_CHEST = "wooden-chest"
IRON_CHEST = "iron-chest"
BELT = "transport-belt"


#
#  Test
#


class Test_find_underground_entry(unittest.TestCase):
    """Cases where it would be impossible without an underground belt"""

    def test_underground_method(self):
        """
        A main belt may be so wide that you need to surface to cross it
        in this configuration:
        0 1 2 3 4 5 6
        e x x x x x o
        the output should be the node at index 1
        """
        log.debug(f"test")

        site = layout.ConstructionSite(50, 50)
        finder = A_star(site, [(0, 0)], [(1, 1)])
        start_position = (5, 5)
        end_positions = [(3, 5), (7, 5), (5, 3), (5, 7)]
        correct_directions = [(4, 5), (6, 5), (5,4), (5,6)]
        counter = 0
        for end in end_positions:
            node = finder.find_entrance_node(
                finder.nodes[start_position[1]][start_position[0]],
                finder.nodes[end[1]][end[0]],
            )
            self.assertEqual(node.position, correct_directions[counter])
            counter += 1
