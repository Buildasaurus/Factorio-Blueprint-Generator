from factoriocalc import *
from factoriocalc.presets import *

# Input for the blueprint
inputItems = [itm.iron_plate, itm.copper_plate]

# Output for the blueprint
desiredOutput = itm.electronic_circuit

throughput = 30 # items pr second

#machines for construciton - assemblytypes & smelting type
config.machinePrefs.set(MP_LATE_GAME)
config.machinePrefs.set([mch.AssemblingMachine2()])

factory = produce([desiredOutput @ throughput], using = inputItems).factory
print(factory.summary())
