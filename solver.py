"""
A class to generate blueprints from a certain input, to a certain output, on a certain
amount of space in factorio.
"""
import random

from typing import List
from factoriocalc import Machine, config, itm, mch, produce
from factoriocalc.presets import MP_LATE_GAME

import layout

WIDTH = 96 # blueprint width
HEIGHT = 96 # blueprint height

class LocatedMachine:
    'A data class to store a machine and its position'
    def __init__(self, machine: Machine, position=None):
        self.connections = []
        self.machine = machine
        if position is None:
            self.position = [random.random()*WIDTH, random.random()*HEIGHT]
        else:
            self.position = position

    def to_int(self):
        'Converts the stored position to integers. Rounds off.'
        self.position[0] = round(self.position[0])
        self.position[1] = round(self.position[1])


    def __str__(self) -> str:
        'Converts the LocatedMachine to a nicely formatted string'
        return  str(self.machine) + " at " + str(self.position)

    def connect(self, otherMachine: Machine):
        self.connections.append(otherMachine)

    def getConnections(self):
        return self.connections

def randomly_placed_machines(factory):
    '''
    Gives machines needed by the factory a random location.

    :returns: a list of LocatedMachines.
    '''
    boxed_machines = factory.inner.machine.machines

    located_machines = []
    for machine in boxed_machines:
        for _ in range(machine.num):
            located_machine = LocatedMachine(machine.machine)
            located_machines.append(located_machine)

    # FIXME remove this debug code
    for located_machine in located_machines:
        print(located_machine)

    return located_machines


def spring(machines: List[Machine]):
    '''
    Does the spring algorithm on the given machines, and returns them after
    Will treat input as a list of floats
    '''
    for machine in machines:
        for input in machine.machine.inputs:
            machine.connect(find_machine_of_type(machines, input))

    # FIXME write code to do the springing

    return machines

def find_machine_of_type(machines: List[Machine], machine_type: dict[any, None]):
    print("looking for machine that produces " + str(machine_type))

    import factoriocalc.core
    def machine_produces(machine: Machine, output: factoriocalc.core.Item):
        assert isinstance(machine, Machine)
        assert isinstance(output, factoriocalc.core.Item)
        if machine.recipe is None:
            return False # No recipe means no output
        for recipe_output in machine.recipe.outputs:
            if recipe_output.item == output:
                return True
        return False
    
    machine_list = [m for m in machines if machine_produces(m, machine_type)]
    if len(machine_list) < 1:
        raise IndexError(f'No machine in list produces {machine_type}')
    if len(machine_list) > 1:
        raise ValueError(f'More than one machine in list produces {machine_type}')
    return machine_list[0]


def machines_to_int(machines: List[Machine]):
    'Assumes that the machiens are not overlapping in any way'
    for machine in machines:
        machine.to_int()

def place_on_site(site, machines: List[Machine]):
    '''
    Place machines on the construction site

    :param site:  A ConstructionSite that is sufficiently large
    :param machines:  A list of LocatedMachine
    '''
    for lm in machines:
        machine = lm.machine
        site.add_machine(machine.name, lm.position, 0, machine.recipe)

def connect_points(site):
    'Generates a list of coordinates, to walk from one coordinate to the other'
    pass # do A star

def main():
    '''Test code executed if run from command line'''
    # Input for the blueprint
    input_items = [itm.iron_plate, itm.copper_plate]

    # Output for the blueprint
    desired_output = itm.electronic_circuit

    throughput = 1 # items pr second

    #machines for construciton - assemblytypes & smelting type
    config.machinePrefs.set(MP_LATE_GAME)
    config.machinePrefs.set([mch.AssemblingMachine2()])
    factory = produce([desired_output @ throughput], using=input_items, roundUp=True).factory
    machines = randomly_placed_machines(factory)
    spring(machines)
    machines_to_int(machines)
    site = layout.ConstructionSite(WIDTH, HEIGHT)
    place_on_site(site, machines)
    connect_points(site)
    print(site)
    print(layout.site_as_blueprint_string(site, label='test of blueprint code'))

if __name__ == '__main__':
    main()