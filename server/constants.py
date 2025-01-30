# Copied from draftsman/constants.py

"""
Enumerations of frequently used constants.
"""

from enum import IntEnum


class Direction(IntEnum):
    """
    Factorio direction enum. Encompasses all 16 cardinal directions and diagonals
    where north is 0 and increments clockwise.

    * ``NORTH`` (Default)
    * ``NORTHNORTHEAST``
    * ``NORTHEAST``
    * ``EAST``
    * ``SOUTHEAST``
    * ``SOUTH``
    * ``SOUTHWEST``
    * ``WEST``
    * ``NORTHWEST``
    """

    # Factorio 2.0 has 16 directions, before 2.0 there were 8
    NORTH = 0
    NORTHNORTHEAST = 1
    NORTHEAST = 2
    EASTNORTHEAST = 3
    EAST = 4
    EASTSOUTHEAST = 5
    SOUTHEAST = 6
    SOUTHSOUTHEAST = 7
    SOUTH = 8
    SOUTHSOUTHWEST = 9
    SOUTHWEST = 10
    WESTSOUTHWEST = 11
    WEST = 12
    WESTNORTHWEST = 13
    NORTHWEST = 14
    NORTHNORTHWEST = 15


max_underground_length = {
    'underground-belt': 4,
    'fast-underground-belt': 6,
    'express-underground-belt': 8,
}
