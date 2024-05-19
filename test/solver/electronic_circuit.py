# Test solver by producing electronic circuits

import unittest
import logging

import factoriocalc as fc
import factoriocalc.presets as fcc

import layout
import solver
from test.solver.visuals import ForceAlgorithmVisuals
from test.astar.path_visuals import PathFindingVisuals

#
#  Logging
#

LOG_FILE = "fbg.log"


def config_logging():
    formatter = logging.Formatter(
        style="{", fmt="{asctime} {module} {levelname} {message}"
    )

    handler = logging.FileHandler(filename=LOG_FILE, mode="w", encoding="utf-8")
    handler.setFormatter(formatter)

    root_log = logging.getLogger()
    root_log.addHandler(handler)
    root_log.setLevel(logging.DEBUG)
    return root_log


log = config_logging()
log.info("unittest of solver module")


#
#  Test
#

WIDTH = 96  # blueprint width
HEIGHT = 96  # blueprint height


class TestElectronicCircuit(unittest.TestCase):
    def test_problem_to_layout(self):
        # Input for the blueprint
        input_items = [fc.itm.iron_plate, fc.itm.copper_plate]

        # Output for the blueprint
        desired_output = fc.itm.electronic_circuit

        throughput = 3  # items pr second. 3 is equivalent of 2 green circuit, 3 copper assembling 2 machines

        # machines for construciton - assemblytypes & smelting type
        fc.config.machinePrefs.set(fcc.MP_LATE_GAME)
        fc.config.machinePrefs.set([fc.mch.AssemblingMachine2()])
        factory = fc.produce(
            [desired_output @ throughput], using=input_items, roundUp=True
        ).factory

        site = layout.ConstructionSite(WIDTH, HEIGHT)
        machines = solver.randomly_placed_machines(factory, site.size())
        visuals = ForceAlgorithmVisuals(WIDTH, HEIGHT, fps=60)
        visuals.set_machines(machines)
        solver.add_connections(machines)
        solver.spring(machines, visuals.show_frame, borders=((0, 0), (WIDTH, HEIGHT)))
        visuals.close()
        print("Machines are at: " + str([machine.position for machine in machines]))
        solver.machines_to_int(machines)
        print("Machines are at: " + str([machine.position for machine in machines]))
        spring_visuals = PathFindingVisuals(WIDTH, HEIGHT,site, fps=60)
        solver.place_on_site(site, machines, spring_visuals)
        print(site)
        print(layout.site_as_blueprint_string(site, label="test of blueprint code"))
        print("End of test")
