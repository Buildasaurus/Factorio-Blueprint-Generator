# Test solver on a minimal mall

import unittest

import factoriocalc as fc
import factoriocalc.presets as fcc

import layout
import solver
from test.solver.visuals import ForceAlgorithmVisuals

#
#  Test
#

WIDTH = 64 # blueprint width
HEIGHT = 64 # blueprint height

class TestSmallMall(unittest.TestCase):
    '''This test is more complex, in that the flow is higher so there must be multiple machines for one recipe and the recipe graph is no longer a tree. However, there is still just one obvious way to solve it. No fluids involved.'''
    def test_layout_small_mall(self):
        # Input for the blueprint
        input_items = [
            fc.itm.iron_plate,
            fc.itm.steel_plate,
            fc.itm.copper_plate]

        throughput = 1 # items pr second

        # Output for the blueprint
        desired_output = [
            fc.itm.inserter @ throughput,
            fc.itm.assembling_machine_1 @ throughput,
            fc.itm.underground_belt @ throughput,
            fc.itm.transport_belt @ throughput,
            fc.itm.small_electric_pole @ throughput]


        #machines for construciton - assemblytypes & smelting type
        fc.config.machinePrefs.set(fcc.MP_LATE_GAME)
        fc.config.machinePrefs.set([fc.mch.AssemblingMachine1()])
        factory = fc.produce(desired_output, using=input_items, roundUp=True).factory
        site = layout.ConstructionSite(WIDTH, HEIGHT)
        machines = solver.randomly_placed_machines(factory, site.size())
        visuals = ForceAlgorithmVisuals(WIDTH, HEIGHT, fps=25)
        visuals.set_machines(machines)
        solver.add_connections(machines)
        solver.spring(machines,
                visuals.show_frame,
                borders=((0, 0), site.size()),
                max_iterations=200)
        solver.machines_to_int(machines)
        solver.place_on_site(site, machines)
        print(f'site dimensions: {site.size()}')
        print(site)
        #log.debug(f'site entity list (will be blueprint)\n{site.get_entity_list()}')
        print(layout.site_as_blueprint_string(site, label='test of blueprint code'))
