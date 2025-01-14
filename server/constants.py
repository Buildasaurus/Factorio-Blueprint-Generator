# Copied from draftsman/constants.py

"""
Enumerations of frequently used constants.
"""

from enum import IntEnum


class Direction(IntEnum):
    """
    Factorio direction enum. Encompasses all 8 cardinal directions and diagonals
    where north is 0 and increments clockwise.

    * ``NORTH`` (Default)
    * ``NORTHEAST``
    * ``EAST``
    * ``SOUTHEAST``
    * ``SOUTH``
    * ``SOUTHWEST``
    * ``WEST``
    * ``NORTHWEST``
    """

    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7


max_underground_length = {
    'underground-belt': 4,
    'fast-underground-belt': 6,
    'express-underground-belt': 8,
}
