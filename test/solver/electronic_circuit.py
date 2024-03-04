# Test solver by producing electronic circuits

import unittest
import logging

import factoriocalc as fc
import factoriocalc.presets as fcc

import layout
import solver

#
#  Logging
#

LOG_FILE = 'fbg.log'

def config_logging():
    formatter = logging.Formatter(style='{',
        fmt='{asctime} {module} {levelname} {message}' )

    handler = logging.FileHandler(filename=LOG_FILE, mode='w', encoding='utf-8')
    handler.setFormatter(formatter)

    root_log = logging.getLogger()
    root_log.addHandler(handler)
    root_log.setLevel(logging.DEBUG)
    return root_log

log = config_logging()
log.info('unittest of solver module')

#
#  Test
#

class TestElectronicCircuit(unittest.TestCase):
    def test_problem_to_layout(self):
        # Input for the blueprint
        input_items = [fc.itm.iron_plate, fc.itm.copper_plate]

        # Output for the blueprint
        desired_output = fc.itm.electronic_circuit

        throughput = 1 # items pr second

        #machines for construciton - assemblytypes & smelting type
        fc.config.machinePrefs.set(fcc.MP_LATE_GAME)
        fc.config.machinePrefs.set([fc.mch.AssemblingMachine2()])
        factory = fc.produce([desired_output @ throughput], using=input_items, roundUp=True).factory
        machines = solver.randomly_placed_machines(factory)
        solver.spring(machines)
        solver.machines_to_int(machines)
        site = layout.ConstructionSite(solver.WIDTH, solver.HEIGHT)
        for machine in machines:
            print(machine)
        solver.place_on_site(site, machines)
        solver.connect_points(site)
        print(site)
        print(layout.site_as_blueprint_string(site, label='test of blueprint code'))
