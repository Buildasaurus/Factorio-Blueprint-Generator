"""
A module that generate blueprints from a certain input, to a certain output, on a certain
amount of space in Factorio.
"""

# Standard imports
import math
import random
from typing import List

# Third party imports
from factoriocalc import Machine, Item

# First party imports
from vector import Vector

# Guide at https://github.com/brean/python-pathfinding/blob/main/docs/01_basic_usage.md
from pathfinding_extensions import *

from layout import ConstructionSite

import layout


#
#  classes
#


class FactoryNode:
    """An abstraction of machines and ports used to find rough layout."""

    def __init__(self, position=None):
        """Create a FactoryNode

        :param position:  Upper left position of node
        """
        self.position = position

    def size(self):
        """Returns a tuple representing the size"""
        return (0, 0)

    def center(self) -> Vector:
        """Returns a position at the center of the node. Coordinates may be floats."""
        return self.position + (Vector(*self.size()) / 2)

    def move(self, direction: Vector):
        """Move node position the specified amount"""
        self.position += direction

    def overlaps(self, other: "FactoryNode") -> bool:
        """Check if two square nodes overlap"""
        min_dist = [(self.size()[i] + other.size()[i]) / 2 for i in range(2)]
        return (
            abs(self.center()[0] - other.center()[0]) < min_dist[0]
            and abs(self.center()[1] - other.center()[1]) < min_dist[1]
        )


class Port(FactoryNode):
    """A point where a factory exchanges items with its surroundings.
    This is usually a transport-belt tile, but can also be a provider chest
    or requester chest."""

    def __init__(self, item_type, rate, position=None):
        """Create an external port for a factory.

        :param item_type:  The item type exchanged here
        :param rate:  The flow through this port, measured in items per second.
            Positive means output from factory, negative means input to factory.
        :param position:  The position of the port
        """
        super().__init__(position)
        self.item_type = item_type
        self.rate = rate

    def size(self):
        return (1, 1)


class LocatedMachine(FactoryNode):
    "A data class to store a machine and its position"

    def __init__(self, machine: Machine, position=None):
        super().__init__(position)
        self.machine = machine
        # Items pr second - True to make it calculate actual value.
        flow_by_item = machine.flows(True).byItem

        # Input to machine
        self.connections = []
        self.missing_input = {
            key: value.rateIn
            for key, value in flow_by_item.items()
            if value.rateIn != 0
        }

        # Output from machine
        self.users = []
        self.unused_output = {
            key: value.rateOut
            for key, value in flow_by_item.items()
            if value.rateOut != 0
        }

    def size(self):
        return layout.entity_size(self.machine.name)

    def set_random_position(self, site_size):
        """Place the machine on a random position inside the provided dimension"""
        my_size = self.size()
        top_left = (0, 0)
        corner_range = [site_size[i] - my_size[i] for i in range(2)]
        self.position = random_position(top_left, corner_range)

    def to_int(self):
        """Converts the stored position to integers.
        Truncates towards zero to avoid placement outside site."""
        self.position = Vector(
            int(self.position.values[0]), int(self.position.values[1])
        )

    def __str__(self) -> str:
        "Converts the LocatedMachine to a nicely formatted string"
        return str(self.machine) + " at " + str(self.position)

    def consume_from(self, other: "LocatedMachine", item_type):
        """Set up a connection from other machine to this machine

        :param other:  source of items
        :param item_type:  item type to get from source
        """
        assert isinstance(other, LocatedMachine)

        # Rename parameters
        source = other
        target = self

        # Link machines
        target.connections.append(source)
        source.users.append(target)

        # Compute how much flow is still not accounted for
        output_items = set(source.unused_output.keys())
        input_items = set(target.missing_input.keys())
        def decrease_flow(dict, key, value):
            dict[key] -= value
            if dict[key] == 0:
                del dict[key]
        for item_type in output_items.intersection(input_items):
            flow_rate = min(source.unused_output[item_type], 
                            target.missing_input[item_type])
            decrease_flow(source.unused_output, item_type, flow_rate)
            decrease_flow(target.missing_input, item_type, flow_rate)

    def getConnections(self) -> List["LocatedMachine"]:
        return self.connections

    def getUsers(self) -> List["LocatedMachine"]:
        return self.users

    def directionTo(self, other_machine: "LocatedMachine") -> Vector:
        """
        Returns a vector pointing from this machine, to the other machine.
        """
        return other_machine.position - self.position

    def distance_to(self, othermachine: "LocatedMachine") -> int:

        summed_vectors = self.position - othermachine.position
        return math.sqrt(summed_vectors.inner(summed_vectors))


def random_position(min_pos, max_pos):
    """Provide a random position in the given bounderies"""
    random_pos = [min_pos[i] + random.random() * (max_pos[i] - min_pos[i]) for i in range(2)]
    return Vector(*random_pos)

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

    return located_machines


def add_connections(machines: List[LocatedMachine]):
    """
    Connect machines such that input and output match.
    """
    for machine in machines:
        for item_type in machine.machine.inputs:
            found_machine_count = 0
            while machine.missing_input.get(item_type, 0) > 0:
                source_machine = find_machine_with_unused_output(machines, item_type)
                if source_machine is None:
                    break
                found_machine_count += 1
                machine.consume_from(source_machine, item_type)

            if found_machine_count == 0:
                pass  # TODO External input should be fixed at the edge of the construction site

def spring(
    machines: List[LocatedMachine],
    iteration_visitor=None,
    iteration_threshold=0.1,
    borders=None,
    max_iterations=200,
):
    """
    Does the spring algorithm on the given machines, and returns them after
    Will treat input as a list of floats

    :param machines:  The machines to move
    :param iteration_visitor:  A visitor function called after each iteration
    :param borders:  Boundaries for machine position ((min_x, min_y), (max_x, max_y))
    """

    # IDEA Examine algorithms found when searching for
    #      "force directed graph layout algorithm"
    #      One of these is a chapter in a book, published by Brown University
    #      Section 12.2 suggests using logarithmic springs and a repelling force

    c1 = 1  # Spring force multiplier
    c2 = 6  # Preferred distance along connections
    c3 = 5  # Repelling force multiplier
    c4 = 1  # Move multiplier
    preferred_border_distance = 3

    resultant_forces = [Vector() for i in range(len(machines))]
    for iteration_no in range(max_iterations):
        # lots of small iterations with small movement in each - high resolution
        for machine_index, machine in enumerate(machines):
            # calculating how all other machines affect this machine
            connections = machine.getConnections()
            connections2 = machine.getUsers()
            for other_machine in machines:
                if machine == other_machine:
                    continue

                distance = machine.distance_to(other_machine)

                if other_machine in connections or other_machine in connections2:
                    # Spring is an attracting force, positive values if far away
                    spring_force = c1 * math.log(distance / c2)
                else:
                    spring_force = 0

                repelling_force = c3 / distance**2

                # Force is the force the other machine is excerting on this machine
                # positive values means that the other machine is pushing this machine away.
                force = repelling_force - spring_force
                force_vector = other_machine.directionTo(machine).normalize() * force

                resultant_forces[machine_index] += force_vector

        if borders is not None:
            # Borders repell if you get too close
            min_pos = borders[0]
            max_pos = borders[1]
            for machine_index, machine in enumerate(machines):
                force = [0, 0]
                for d in range(2):
                    past_min_border = (
                        min_pos[d]
                        - machine.position.values[d]
                        + preferred_border_distance
                    )
                    if past_min_border > 0:
                        force[d] += past_min_border / preferred_border_distance
                    past_max_border = (
                        machine.position.values[d]
                        - max_pos[d]
                        + preferred_border_distance
                    )
                    if past_max_border > 0:
                        force[d] -= past_max_border / preferred_border_distance
                resultant_forces[machine_index] += Vector(*force)

        # Check for no more movement
        max_dist = 0
        for i in range(len(resultant_forces)):
            move_step = resultant_forces[i] * c4
            machines[i].move(move_step)
            resultant_forces[i] = Vector(0, 0)
            max_dist = max(max_dist, move_step.norm())

        if iteration_visitor:
            iteration_visitor(movement=max_dist, iteration=iteration_no, iteration_limit=max_iterations)

        if max_dist < iteration_threshold:
            break

    return machines


def find_machine_with_unused_output(machines: List[LocatedMachine], item_type):
    '''Find a machine with excess production'''
    print("looking for machine that has unused " + str(item_type))

    # Each candidate is a pair (unused_output, machine)
    machine_candidates = [(m.unused_output[item_type], m)
            for m in machines
            if m.unused_output.get(item_type, 0) > 0]
    
    if len(machine_candidates) == 0:
        print(f" no machine has unused {item_type}")
        return None
    
    unused_output = lambda candidate: candidate[0]
    return min(machine_candidates, key=unused_output)[1]


def machines_to_int(machines: List[LocatedMachine]):
    "Assumes that the machines are not overlapping in any way"
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
        for source in target.getConnections():
            connect_machines(site, source, target)


def connect_machines(
    site: ConstructionSite,
    source: FactoryNode,
    target: FactoryNode,
    inserter="inserter",
    belt="transport-belt",
):
    """Connect two machines by adding a transport belt to the
    construction site.

    :param site: The site to build on
    :param source: Source machine
    :param target: Target machine
    :param inserter: Type of inserter to use
    :param belt: Type of belt to use
    """
    # Check for unsupported configuration
    if target.overlaps(source):
        raise ValueError("Machines overlap")
    # Find an open path between machines
    pos_list = find_path(site, source, target)
    if len(pos_list) == 0:
        raise ValueError("No possible path")
    assert len(pos_list) >= 3, "Path below length 3 is not supported"
    # Find proper orientation of belt cells
    dir_list = []
    for i in range(len(pos_list) - 1):
        dir_list.append(layout.direction_to(pos_list[i], pos_list[i + 1]))
    dir_list.append(dir_list[-1])  # repeat last direction

    # Add belt and inserters to site
    for i in range(len(dir_list)):
        kind = inserter if i == 0 or i + 1 == len(dir_list) else belt
        dir = dir_list[i]
        if kind == inserter:
            dir = (dir + 4) % 8
        site.add_entity(kind, pos_list[i], dir, None)


def find_path(
    site: ConstructionSite, source: FactoryNode, target: FactoryNode
) -> List[tuple]:
    """Generates a list of coordinates, to walk from one machine to the other

    :param site: The site knows which coordinates are already taken
    :param source: Source machine
    :param target: Target machine
    :returns: a list of site coordinates between the two machines
    """
    map = []
    BLOCKED = 0
    NORMAL = 1
    EXPENSIVE = 2
    for r in range(site.size()[1]):
        row = []
        for c in range(site.size()[0]):
            row.append(BLOCKED if site.is_reserved(c, r) else NORMAL)
        map.append(row)

    # Make source and target machines expensive, but not impossible to travel
    # For each direction in the two dimensions, create starting squares
    # x and y are the inserter coordinates
    def add_entry_if_free(inserter_pos, step, entry_list):
        x, y = inserter_pos
        if not is_in_bounds(x, y, map) or map[y][x] == BLOCKED:
            return
        x, y = (Vector(*inserter_pos) + Vector(*step)).values
        if not is_in_bounds(x, y, map) or map[y][x] == BLOCKED:
            return
        entry_list.append(GridNode(x, y))
        x, y = inserter_pos
        map[y][x] = BLOCKED

    coordinates = [[] for i in range(2)]
    for i, m in enumerate([source, target]):
        pos = m.position.as_int()

        for row in range(m.size()[1]):

            # right side
            x = pos[0] + m.size()[0]
            y = pos[1] + row
            add_entry_if_free((x, y), (1, 0), coordinates[i])

            # left side
            x = pos[0] - 1
            y = pos[1] + row
            add_entry_if_free((x, y), (-1, 0), coordinates[i])

        for column in range(m.size()[0]):

            # downwards side
            x = pos[0] + column
            y = pos[1] + m.size()[1]
            add_entry_if_free((x, y), (0, 1), coordinates[i])

            # upwards side
            x = pos[0] + column
            y = pos[1] - 1
            add_entry_if_free((x, y), (0, -1), coordinates[i])

    grid = Grid(matrix=map)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(coordinates[0], coordinates[1], grid)

    print("operations:", runs, "path length:", len(path))
    print(grid.grid_str(path=path, start=coordinates[0], end=coordinates[1]))
    # print(type(path))

    # Add inserter at both ends of path
    sign = lambda x: 1 if x > 0 else -1
    def step_one(ofs: Vector):
        if abs(ofs.values[0]) > abs(ofs.values[1]):
            # move horizontally
            return Vector(sign(ofs.values[0]), 0)
        else:
            # move vertically
            return Vector(0, sign(ofs.values[1]))
    belt_center = lambda xy: Vector(*xy) + Vector(0.5, 0.5)
    def step_towards(machine, origin):
        next_pos = Vector(*origin) + step_one(machine.center() - belt_center(origin))
        return (next_pos[0], next_pos[1])
    xypath = [(n.x, n.y) for n in path]
    if len(xypath) > 0:
        xypath.insert(0, step_towards(source, xypath[0]))
        xypath.append(step_towards(target, xypath[-1]))
    
    return xypath


def is_in_bounds(x, y, map):
    return x >= 0 and y >= 0 and x < len(map[0]) and y < len(map)


if __name__ == "__main__":
    """Test code executed if run from command line"""
    import test.solver
    import unittest

    unittest.main(defaultTest="test.solver", verbosity=2)
