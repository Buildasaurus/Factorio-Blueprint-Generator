from factoriocalc import *
from factoriocalc.presets import *
import random

class LocatedMachine:
    position = None
    machine = None
    def __init__(self, machine, position):
        self.machine = machine
        self.position = position

    def __str__(self) -> str:
        return  str(self.machine) + " at " + str(self.position)


# Input for the blueprint
inputItems = [itm.iron_plate, itm.copper_plate]

# Output for the blueprint
desiredOutput = itm.electronic_circuit

throughput = 30 # items pr second

#machines for construciton - assemblytypes & smelting type
config.machinePrefs.set(MP_LATE_GAME)
config.machinePrefs.set([mch.AssemblingMachine2()])

factory = produce([desiredOutput @ throughput], using = inputItems).factory

machineCounts = factory.inner.machine.machines
locatedMachines = []

for machine in machineCounts:
    for i in range(machine.num):
        pos = [random.random(), random.random()]
        locatedMachine = LocatedMachine(machine.machine, pos)
        locatedMachines.append(locatedMachine)

for locatedMachine in locatedMachines:
    print(locatedMachine)
