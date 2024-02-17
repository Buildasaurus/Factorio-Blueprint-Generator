from factoriocalc import *
from factoriocalc.presets import *
import random

width = 96 # blueprint width
height = 96 # blueprint height

class LocatedMachine:
    position = None
    machine = None
    def __init__(self, machine, position):
        self.machine = machine
        self.position = position

    def __init__(self, machine):
        self.position = [random.random()*width, random.random()*height]
        self.machine = machine

    def toInt(self):
        self.position[0] = round(self.position[0])
        self.position[1] = round(self.position[1])


    def __str__(self) -> str:
        return  str(self.machine) + " at " + str(self.position)

factory = None

def randomlyPlacedMachines():
    boxedMachines = factory.inner.machine.machines
    locatedMachines = []

    for machine in boxedMachines:
        for i in range(machine.num):
            locatedMachine = LocatedMachine(machine.machine)
            locatedMachines.append(locatedMachine)

    for locatedMachine in locatedMachines:
        print(locatedMachine)

    return locatedMachines


def spring(machines):
    return machines

def machinesToInt(machines):
    'Assumes that the machiens are not overlapping in any way'
    for machine in machines:
        machine.toInt()

def generateBitMap(machines):
    'Assumes taht machiens given have integers as coordinates.'
    arr = [[0 for i in range(width)] for i in range(height)]
    for machine in machines:
        print('What is the size of the machine??')
        arr[machines.position[1]][machines.position[0]] = 1



def connectPoints(map):
    'Generates a list of coordinates, to walk from one coordinate to the other'
    pass # do A star

if __name__ == '__main__':
    # Input for the blueprint
    inputItems = [itm.iron_plate, itm.copper_plate]

    # Output for the blueprint
    desiredOutput = itm.electronic_circuit

    throughput = 1 # items pr second

    #machines for construciton - assemblytypes & smelting type
    config.machinePrefs.set(MP_LATE_GAME)
    config.machinePrefs.set([mch.AssemblingMachine2()])
    factory = produce([desiredOutput @ throughput], using = inputItems, roundUp=True).factory
    machines = randomlyPlacedMachines()
    spring(machines)
    machinesToInt(machines)
    bitMap = generateBitMap(machines)
