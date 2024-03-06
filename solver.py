"""
A class to generate blueprints from a certain input, to a certain output, on a certain
amount of space in factorio.
"""

import random
from typing import List

from factoriocalc import Machine, Item

import layout
import math

WIDTH = 96  # blueprint width
HEIGHT = 96  # blueprint height

#
#  classes
#

class LocatedMachine:
    "A data class to store a machine and its position"

    def __init__(self, machine: Machine, position=None):
        self.connections = []
        self.machine = machine
        self.position = position

    def set_random_position(self, site_size):
        '''Place the machine on a random position inside the provided dimension'''
        my_size = layout.entity_size(self.machine.name)
        corner_range = [site_size[i] - my_size[i] for i in range(2)]
        self.position = [random.random() * corner_range[i] for i in range(2)]

    def to_int(self):
        """Converts the stored position to integers.
        Truncates towards zero to avoid placement outside site."""
        self.position[0] = int(self.position[0])
        self.position[1] = int(self.position[1])

    def __str__(self) -> str:
        "Converts the LocatedMachine to a nicely formatted string"
        return str(self.machine) + " at " + str(self.position)

    def connect(self, otherMachine: "LocatedMachine"):
        assert isinstance(otherMachine, LocatedMachine)
        self.connections.append(otherMachine)

    def getConnections(self) -> List["LocatedMachine"]:
        return self.connections

    def directionTo(self, other_machine: "LocatedMachine"):
        """
        Returns a vector pointing from this machine, to the other machine.
        """
        return [
            other_machine.position[0] - self.position[0],
            other_machine.position[1] - self.position[1],
        ]

    def move(self, direction):
        for i in range(len(direction)):
            self.position[i] += direction[i]
        # TODO Hacky solution, move shouldn't do this, but I want it to work.
        # with negative numbers it should handle it in another smarter way.
        self.position[0] %= WIDTH
        self.position[1] %= HEIGHT

    def overlaps(self, other_machine : 'LocatedMachine'):
        # TODO - don't assume size is 4
        return abs(self.position[0] - other_machine.position[0]) < 4 and  abs(self.position[1] - other_machine.position[1]) < 4


def randomly_placed_machines(factory, site_size):
    """
    Gives machines needed by the factory a random location.

    :returns: a list of LocatedMachines.
    """
    boxed_machines = factory.inner.machine.machines

    located_machines = []
    for machine in boxed_machines:
        for _ in range(machine.num):
            located_machine = LocatedMachine(machine.machine)
            located_machine.set_random_position(site_size)
            located_machines.append(located_machine)

    # FIXME remove this debug code
    for located_machine in located_machines:
        print(located_machine)

    return located_machines


def spring(machines: List[LocatedMachine]):
    """
    Does the spring algorithm on the given machines, and returns them after
    Will treat input as a list of floats
    """
    for machine in machines:
        for input in machine.machine.inputs:
            source_machine = find_machine_of_type(machines, input)
            if source_machine is None:
                pass  # TODO External input should be fixed at the edge of the construction site
            else:
                machine.connect(source_machine)

    # FIXME improve code to do the springing. It is not very natural, and will probably bug with more machines than two
                # due to no smart way of making sure machines don't collide
    # IDEA Examine algorithms found when searching for
    #      "force directed graph layout algorithm"
    #      One of these is a chapter in a book, published by Brown University
    #      Section 12.2 suggests using logarithmic springs and a repelling force
    for i in range(10):
        for machine in machines:
            for connected_machine in machine.getConnections():
                machine.move([
                        machine.directionTo(connected_machine)[0] / 10,
                        machine.directionTo(connected_machine)[1] / 10,
                    ])
                connected_machine.move(
                    [
                        connected_machine.directionTo(machine)[0] / 10,
                        connected_machine.directionTo(machine)[1] / 10,
                    ]
                )

        # Remove overlapping machine
        # TODO - improve the spring algorithm instead, to make it less explosive.
        for machine in machines:
            for other_machine in machines:
                if machine == other_machine:
                    continue
                if machine.overlaps(other_machine):
                    machine.move([4 - other_machine.directionTo(machine)[0],  4 - other_machine.directionTo(machine)[1]])

    return machines


def find_machine_of_type(machines: List[LocatedMachine], machine_type: dict[any, None]):
    print("looking for machine that produces " + str(machine_type))

    def machine_produces(machine: Machine, output: Item):
        assert isinstance(machine, Machine), f" {type(machine)} is not a Machine"
        assert isinstance(output, Item), f" {type(output)} is not an Item"
        if machine.recipe is None:
            return False  # No recipe means no output
        for recipe_output in machine.recipe.outputs:
            if recipe_output.item == output:
                print(f" machine {machine} produces {recipe_output}")
                return True
        return False

    machine_list = [m for m in machines if machine_produces(m.machine, machine_type)]
    if len(machine_list) < 1:
        print(f" no machine produces {machine_type}")
        return None
    if len(machine_list) > 1:
        # TODO - This should not return error, but just choose the one that already is being used the most.
        raise ValueError(f"More than one machine in list produces {machine_type}")
    return machine_list[0]


def machines_to_int(machines: List[LocatedMachine]):
    "Assumes that the machiens are not overlapping in any way"
    for machine in machines:
        machine.to_int()


def place_on_site(site, machines: List[LocatedMachine]):
    """
    Place machines on the construction site

    :param site:  A ConstructionSite that is sufficiently large
    :param machines:  A list of LocatedMachine
    """
    for lm in machines:
        machine = lm.machine
        site.add_entity(machine.name, lm.position, 0, machine.recipe.name)

    for target in machines:
        for source in target.connections:
            dist = [target.position[i] - source.position[i] for i in range(2)]
            abs_dist = [abs(dist[i]) for i in range(2)]
            max_dist = max(abs_dist)
            # FIXME: Assume both machines are size 3x3
            if max_dist < 3:
                raise ValueError(f"Machines overlap")
            if max_dist == 3:
                pass
                #raise NotImplementedError("Machines touch")
            if min(abs_dist) in [1, 2]:
                raise NotImplementedError("Path algorithm cannot handle small offsets")
            assert max_dist > 3
            # Layout belt
            belt_count = sum(abs_dist) - 3 - 2 * 1
            if belt_count < 1:
                raise NotImplementedError("Machines can connect with single inserter")
            pos = [source.position[i] + 1 for i in range(2)]
            tgtpos = [target.position[i] + 1 for i in range(2)]
            step = 0
            pos_list = []
            while pos != tgtpos:
                step += 1
                if pos[0] != tgtpos[0]:
                    pos[0] += 1 if tgtpos[0] > pos[0] else -1
                else:
                    pos[1] += 1 if tgtpos[1] > pos[1] else -1
                if step < 2 or step > 3 + belt_count:
                    continue
                pos_list.append(pos[:])
            pos_list.append(tgtpos)
            dir_list = []
            for i in range(len(pos_list) - 1):
                dir_list.append(layout.direction_to(pos_list[i], pos_list[i+1]))
            for i in range(len(dir_list)):
                kind = 'inserter' if i == 0 or i + 1 == len(dir_list) else 'transport-belt'
                dir = dir_list[i]
                if kind == 'inserter':
                    dir = (dir + 4) % 8
                site.add_entity(kind, pos_list[i], dir, None)

def connect_points(site):
    "Generates a list of coordinates, to walk from one coordinate to the other"
    pass  # do A star


if __name__ == "__main__":
    """Test code executed if run from command line"""
    import test.solver
    import unittest

    unittest.main(defaultTest="test.solver", verbosity=2)
