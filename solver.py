"""
A class to generate blueprints from a certain input, to a certain output, on a certain
amount of space in factorio.
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
from pathfinding.core.node import GridNode
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
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
        self.connections = []
        self.machine = machine
        # Items pr second - True to make it calculate actual value.
        a = machine.flows(True).byItem
        # FIXME Available production should also be a dictionary for multiple outputs
        self.available_production = sum(
            item.rateOut for item in machine.flows(True).byItem.values()
        )

        self.users = []
        self.missing_input = {
            key: value.rateIn
            for key, value in machine.flows(True).byItem.items()
            if value.rateIn != 0
        }
        #print(self.missing_input)

    def size(self):
        # TODO - don't assume size is 4
        return (4, 4)

    def set_random_position(self, site_size):
        """Place the machine on a random position inside the provided dimension"""
        my_size = layout.entity_size(self.machine.name)
        corner_range = [site_size[i] - my_size[i] for i in range(2)]
        self.position = Vector(
            random.random() * corner_range[0], random.random() * corner_range[1]
        )
        #print(self.position.values)

    def to_int(self):
        """Converts the stored position to integers.
        Truncates towards zero to avoid placement outside site."""
        self.position = Vector(
            int(self.position.values[0]), int(self.position.values[1])
        )

    def __str__(self) -> str:
        "Converts the LocatedMachine to a nicely formatted string"
        return str(self.machine) + " at " + str(self.position)

    def set_user(self, other_machine: "LocatedMachine", usage) -> int:
        """Returns the production this machine could provide"""
        assert isinstance(other_machine, LocatedMachine)
        used = 0
        if self.available_production > 0:
            self.users.append(other_machine)
            if self.available_production < usage:
                used = self.available_production
                self.available_production = 0
            else:
                used = usage
                self.available_production -= usage

        #print(self.available_production)
        return used

    def connect(self, otherMachine: "LocatedMachine", item_type) -> bool:
        """Set up a connection from other to this machine
        :param otherMachine:  source of items
        :param item_type:  item type to get from source
        :return:  True, if all input requirements were satisfied
        """
        assert isinstance(otherMachine, LocatedMachine)
        self.connections.append(otherMachine)
        b = self.missing_input[item_type]
        a = self.machine.flows().byItem
        extra_input = otherMachine.set_user(self, self.missing_input[item_type])
        self.missing_input[item_type] -= extra_input

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
    for machine in machines:
        for input in machine.machine.inputs:
            found_machine_count = 0
            while machine.missing_input[input] > 0:
                source_machine = find_machine_of_type(machines, input)
                if source_machine is None:
                    break
                found_machine_count += 1
                machine.connect(source_machine, input)

            if found_machine_count == 0:
                pass  # TODO External input should be fixed at the edge of the construction site

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
        if iteration_no/max_iterations*100 % 10 == 0:
            print(f"{iteration_no} of at most {max_iterations}")
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
            iteration_visitor()

        if max_dist < iteration_threshold:
            break

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
    else:
        # Find the machine with the least available output, above 0
        minimum = 99999
        machine_to_connect = machine_list[0]
        for machine in machine_list:
            if (
                machine.available_production < minimum
                and machine.available_production > 0
            ):
                minimum = machine.available_production
                machine_to_connect = machine

        if machine_to_connect.available_production == 0:
            # In case we never went past machine 0, which might have 0 available production
            return None
        return machine_to_connect


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
        inserter='inserter', belt='transport-belt'):
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
    # Find connection points on machines
    pos = source.center()
    tgtpos = target.center()
    # Find an open path between machines
    grid_node_list = find_path(site, pos, tgtpos)
    pos_list = [(n.x, n.y) for n in grid_node_list]
    # Find proper orientation of belt cells
    dir_list = []
    for i in range(len(pos_list) - 1):
        dir_list.append(layout.direction_to(pos_list[i], pos_list[i + 1]))
    # Add belt and inserters to site
    for i in range(len(dir_list)):
        kind = (
            inserter if i == 0 or i + 1 == len(dir_list) else belt
        )
        dir = dir_list[i]
        if kind == inserter:
            dir = (dir + 4) % 8
        site.add_entity(kind, pos_list[i], dir, None)

def find_path(site: ConstructionSite, start_pos, end_pos) -> List[GridNode]:
    """Generates a list of coordinates, to walk from one coordinate to the other
    :param site: The site knows which coordinates are already taken
    :param start_pos: Start position
    :param end_pos: Target position
    :returns: a list of GridNodes
    """
    startx = start_pos[0]
    starty = start_pos[1]
    endx = end_pos[0]
    endy = end_pos[1]
    map = []
    for c in range(site.size()[0]):
        col = []
        for r in range(site.size()[1]):
            col.append(0 if site.is_reserved(c,r) else 1)
        map.append(col)
    grid = Grid(matrix=map)
    start = grid.node(startx, starty)
    end = grid.node(endx, endy)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(start, end, grid)

    print("operations:", runs, "path length:", len(path))
    print(grid.grid_str(path=path, start=start, end=end))
    #print(type(path))

    return path


if __name__ == "__main__":
    """Test code executed if run from command line"""
    import test.solver
    import unittest

    unittest.main(defaultTest="test.solver", verbosity=2)
