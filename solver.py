"""
A class to generate blueprints from a certain input, to a certain output, on a certain
amount of space in factorio.
"""

# Standard imports
import math
import random
from typing import List

# Third party imports
import matplotlib.pyplot as plt
import matplotlib.patches
from factoriocalc import Machine, Item

# First party imports
from vector import Vector
import layout


WIDTH = 96  # blueprint width
HEIGHT = 96  # blueprint height

with_visuals = True

#
#  classes
#


class FactoryNode:
    """ An abstraction of machines and ports used to find rough layout. """

    def __init__(self, position=None):
        """Create a FactoryNode
        :param position:  Upper left position of node
        """
        self.position = position

    def size(self):
        """ Returns a tuple representing the size """
        return (0, 0)

    def center(self) -> Vector:
        """ Returns a position at the center of the node. Coordinates may be floats. """
        return self.position + (Vector(*self.size()) / 2)

    def move(self, direction: Vector):
        """ Move node position the specified amount """
        self.position += direction

    def overlaps(self, other: "FactoryNode") -> bool:
        """ Check if two square nodes overlap """
        min_dist = [(self.size()[i] + other.size()[i]) / 2 for i in range(2)]
        return (
            abs(self.center()[0] - other.center()[0]) < min_dist[0]
            and abs(self.center()[1] - other.center()[1]) < min_dist[1]
        )

class Port(FactoryNode):
    """ A point where a factory exchanges items with its surroundings.
    This is usually a transport-belt tile, but can also be a provider chest
    or requester chest. """

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
        print(self.missing_input)

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
        print(self.position.values)

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

        print(self.available_production)
        return used

    def connect(self, otherMachine: "LocatedMachine", item_type) -> bool:
        """ Set up a connection from other to this machine
        :param otherMachine:  source of items
        :param item_type:  item type to get from source
        :return:  True, if all input requirements were satisfied
        """
        assert isinstance(otherMachine, LocatedMachine)
        self.connections.append(otherMachine)
        b = self.missing_input[item_type]
        a = self.machine.flows().byItem
        print(type(a))
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
    plt.axis([0, WIDTH, 0, HEIGHT])
    ax = plt.gca()

    c1 = 1
    c2 = 6  # this value is the preferred balanced distance
    c3 = 5 # Repelling force multiplier
    c4 = 1
    resultant_forces = [Vector() for i in range(len(machines))]
    for iteration_no in range(200):
        # lots of small iterations with small movement in each - high resolution
        machine_index = 0
        for machine in machines:
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
            machine_index += 1

        color_legend = {}

        for i in range(len(resultant_forces)):
            machines[i].move(resultant_forces[i] * c4)
            resultant_forces[i] = Vector(0, 0)
        if with_visuals:
            for i in range(len(resultant_forces)):
                # Chat-gpt generated
                def hash_to_rgb(hash_value):
                    r = ((hash_value >> 16) & 255) / 255.0
                    g = ((hash_value >> 8) & 255) / 255.0
                    b = (hash_value & 255) / 255.0
                    return r, g, b

                color = hash_to_rgb(machines[i].machine.recipe.alias.__hash__())
                machine_shape = matplotlib.patches.Rectangle(
                    machines[i].position.values,
                    width=3,
                    height=3,
                    color=color,
                )

                ax.add_patch(machine_shape)

                # Add the color and its label to the dictionary
                color_legend[machines[i].machine.recipe.alias] = (
                    matplotlib.patches.Patch(
                        color=color, label=machines[i].machine.recipe.alias
                    )
                )


        if with_visuals:
            # Create a custom legend using the color and label pairs in the dictionary
            ax.legend(
                handles=list(color_legend.values()),
                bbox_to_anchor=(0.7, 0.7),
                loc="upper left",
            )

            plt.pause(0.05)
            ax.clear()
            ax.set_xlim(0, WIDTH)
            ax.set_ylim(0, HEIGHT)

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
        for source in target.connections:
            # Check for unsupported configuration
            if target.overlaps(source):
                raise ValueError("Machines overlap")

            # Find connection points on machines
            pos = [source.position[i] + 1 for i in range(2)]
            tgtpos = [target.position[i] + 1 for i in range(2)]

            # Connect connection points with a transport belt
            connect_points(site, pos, tgtpos)


def connect_points(site, source, target):
    """Connect two points with a transport belt"""
    # TODO A-star search around obstacles on site
    # The current implementation is much simpler

    # Check for unsupported corner cases
    dist = [target[i] - source[i] for i in range(2)]
    abs_dist = [abs(dist[i]) for i in range(2)]
    max_dist = max(abs_dist)
    if min(abs_dist) in [1, 2]:
        raise NotImplementedError("Path algorithm cannot handle small offsets")
    assert max_dist > 3
    belt_count = sum(abs_dist) - 3 - 2 * 1
    if belt_count < 1:
        raise NotImplementedError("Points can connect with single inserter")

    # Find tiles needed
    pos = source[:]
    tgtpos = target[:]
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

    # Find belt direction
    dir_list = []
    for i in range(len(pos_list) - 1):
        dir_list.append(layout.direction_to(pos_list[i], pos_list[i + 1]))

    # Add to site
    for i in range(len(dir_list)):
        kind = (
            "inserter" if i == 0 or i + 1 == len(dir_list) else "transport-belt"
        )
        d = dir_list[i]
        if kind == "inserter":
            d = (d + 4) % 8
        site.add_entity(kind, pos_list[i], d, None)



if __name__ == "__main__":
    """Test code executed if run from command line"""
    import test.solver
    import unittest

    unittest.main(defaultTest="test.solver", verbosity=2)
