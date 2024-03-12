"""
A class to generate blueprints from a certain input, to a certain output, on a certain
amount of space in factorio.
"""

import matplotlib.pyplot as plt
import matplotlib.patches

import random
from typing import List

from factoriocalc import Machine, Item, fracs, itm
from vector import Vector


import layout
import math

WIDTH = 96  # blueprint width
HEIGHT = 96  # blueprint height

with_visuals = True

#
#  classes
#


class LocatedMachine:
    "A data class to store a machine and its position"

    def __init__(self, machine: Machine, position=None):
        self.connections = []
        self.machine = machine
        self.position = position
        # Items pr second - True to make it calculate actual value.
        a = machine.flows(True).byItem
        #FIXME Available production should also be a dictionary for multiple outputs
        self.available_production =  sum(item.rateOut for item in machine.flows(True).byItem.values())

        self.users = []
        self.missing_input = {key: value.rateIn for key, value in machine.flows(True).byItem.items() if value.rateIn != 0}
        print(self.missing_input)

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
        '''
        Returns the production this machine could provide'''
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
        '''
        Returns if the connection satisfied the remaining requirements
        Input is necessary if machine produces multiple thing
        '''
        assert isinstance(otherMachine, LocatedMachine)
        self.connections.append(otherMachine)
        b = self.missing_input[item_type]
        a =  self.machine.flows().byItem
        print(type(a))
        extra_input = otherMachine.set_user(self, self.missing_input[item_type])
        self.missing_input[item_type] -= extra_input


    def getConnections(self) -> List["LocatedMachine"]:
        return self.connections

    def directionTo(self, other_machine: "LocatedMachine") -> Vector:
        """
        Returns a vector pointing from this machine, to the other machine.
        """
        return other_machine.position - self.position

    def distance_to(self, othermachine: "LocatedMachine") -> int:

        summed_vectors = self.position - othermachine.position
        return math.sqrt(summed_vectors.inner(summed_vectors))

    def move(self, direction: "Vector"):
        self.position += direction
        # TODO Hacky solution, move shouldn't do this, but I want it to work.
        # with negative numbers it should handle it in another smarter way.
        self.position = Vector(
            self.position.values[0] % WIDTH, self.position.values[1] % HEIGHT
        )

    def overlaps(self, other_machine: "LocatedMachine"):
        # TODO - don't assume size is 4
        return (
            abs(self.position[0] - other_machine.position[0]) < 4
            and abs(self.position[1] - other_machine.position[1]) < 4
        )


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
                machine.connect(source_machine, input)

    # IDEA Examine algorithms found when searching for
    #      "force directed graph layout algorithm"
    #      One of these is a chapter in a book, published by Brown University
    #      Section 12.2 suggests using logarithmic springs and a repelling force
    plt.axis([0, WIDTH, 0, HEIGHT])
    ax = plt.gca()

    c1 = 1
    c2 = 6  # this value is the preferred balanced distance
    c3 = 1
    c4 = 1
    resultant_forces = [Vector() for i in range(len(machines))]
    for iteration_no in range(
        20
    ):  # lots of small iterations with small movement in each - high resolution
        machine_index = 0
        for machine in machines:
            # calculating how all other machines affect this machine
            connections = machine.getConnections()
            for other_machine in machines:
                if machine == other_machine:
                    continue

                distance = machine.distance_to(other_machine)

                if (
                    other_machine in connections
                ):  # Spring is an attracting force, positive values if far away
                    spring_force = c1 * math.log(distance / c2)
                else:
                    spring_force = 0

                repelling_force = c3 / distance**2

                # Force is the force the other machine is excerting on this machine
                # positive values means that the other machine is pushing this machine away.
                force = repelling_force - spring_force
                force_vector = machine.directionTo(other_machine).normalize() * -force
                # idk why it's not minus.
                resultant_forces[machine_index] += force_vector
            machine_index += 1

        for i in range(len(resultant_forces)):
            if with_visuals:
                machine_shape = matplotlib.patches.Rectangle(machines[i].position.values, width=3, height=3)
                ax.add_patch(machine_shape)
                

            machines[i].move(resultant_forces[i] * c4)
            resultant_forces[i] = Vector(0, 0)

        if with_visuals:
            plt.pause(0.1)
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
    if len(machine_list) > 1:
        minimum = 99999
        machine_to_connect = machine_list[0]
        for machine in machine_list:
            if machine.available_production < minimum:
                minimum = machine.available_production
                machine_to_connect = machine

        return machine_to_connect
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
                # raise NotImplementedError("Machines touch")
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
                dir_list.append(layout.direction_to(pos_list[i], pos_list[i + 1]))
            for i in range(len(dir_list)):
                kind = (
                    "inserter" if i == 0 or i + 1 == len(dir_list) else "transport-belt"
                )
                dir = dir_list[i]
                if kind == "inserter":
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
