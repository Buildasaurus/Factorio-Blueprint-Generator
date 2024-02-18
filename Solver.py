"""
A class to generate blueprints from a certain input, to a certain output, on a certain
amount of space in factorio.
"""
import random
from factoriocalc import *
from factoriocalc.presets import *

WIDTH = 96 # blueprint width
HEIGHT = 96 # blueprint height

class LocatedMachine:
    'A data class to store a machine and its position'
    def __init__(self, machine, position=None):
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

factory = None

def randomly_placed_machines():
    '''Generates randomly placed machines from the factory variable.
        Returns a list of LocatedMachines.'''
    boxed_machines = factory.inner.machine.machines
    located_machines = []

    for machine in boxed_machines:
        for i in range(machine.num):
            located_machine = LocatedMachine(machine.machine)
            located_machines.append(located_machine)

    for located_machine in located_machines:
        print(located_machine)

    return located_machines


def spring(machines):
    'Does the spring algorithm on the given machines, and returns them after'
    return machines

def machines_to_int(machines):
    'Assumes that the machiens are not overlapping in any way'
    for machine in machines:
        machine.to_int()

def generate_bit_map(machines):
    'Assumes taht machiens given have integers as coordinates.'
    arr = [[0 for i in range(WIDTH)] for i in range(HEIGHT)]
    for machine in machines:
        print('What is the size of the machine??')
        arr[machines.position[1]][machines.position[0]] = 1



def connect_points(map):
    'Generates a list of coordinates, to walk from one coordinate to the other'
    pass # do A star

if __name__ == '__main__':
    # Input for the blueprint
    input_items = [itm.iron_plate, itm.copper_plate]

    # Output for the blueprint
    desired_output = itm.electronic_circuit

    throughput = 1 # items pr second

    #machines for construciton - assemblytypes & smelting type
    config.machinePrefs.set(MP_LATE_GAME)
    config.machinePrefs.set([mch.AssemblingMachine2()])
    factory = produce([desired_output @ throughput], using = input_items, roundUp=True).factory
    machines = randomly_placed_machines()
    spring(machines)
    machines_to_int(machines)
    bit_map = generate_bit_map(machines)
