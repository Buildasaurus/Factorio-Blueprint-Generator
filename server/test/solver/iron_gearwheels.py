# Test solver by producing iron gear wheels

import unittest
import logging

import factoriocalc as fc
import factoriocalc.presets as fcc

import layout
import solver
from test.layout.route_finding import INSERTER
from test.solver.visuals import ForceAlgorithmVisuals
from test.astar.path_visuals import PathFindingVisuals
from vector import Vector

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
log.info("unittest of solver with iron gear wheels")


#
#  Test
#

WIDTH = 96  # blueprint width
HEIGHT = 96  # blueprint height


class TestElectronicCircuit(unittest.TestCase):
    def test_problem_to_layout(self):
        # Input for the blueprint
        input_items = [fc.itm.iron_plate]

        # Output for the blueprint
        desired_output = fc.itm.iron_gear_wheel



        throughput = 1  # items pr second.

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
        log.debug("Machines are at: " + str([machine.position for machine in machines]))
        solver.machines_to_int(machines)
        log.debug("Machines are at: " + str([machine.position for machine in machines]))
        spring_visuals = PathFindingVisuals(WIDTH, HEIGHT,site, fps=60)
        solver.place_on_site(site, machines, spring_visuals)
        log.debug(site)
        log.debug(layout.site_as_blueprint_string(site, label="test of blueprint code"))
        log.debug("End of test")

    '''Demonstrates problem with underground inserters that want to be placed on undergruond belts.'''
    def test_recurring_incorrect_belt(self):
        print("AssemblingMachine2(iron_gear_wheel; @0.888889) and <class 'solver.Port'>")
        width = 96
        height = 96
        site = layout.ConstructionSite(width, height)
        source = solver.FakeMachine(Vector(46, 47), (3,3))
        target = solver.FakeMachine(Vector(41, 54), (3,3))

        # Drawing flipped on its head
        coordinates = [(46, 47), (47, 47), (48, 47), (36, 48), (37, 48), (38, 48), (46, 48), (47, 48), (48, 48), (36, 49), (37, 49), (38, 49), (46, 49), (47, 49), (48, 49), (36, 50), (37, 50), (38, 50), (46, 50), (37, 51), (38, 51), (44, 51), (46, 51), (37, 52), (38, 52), (39, 52), (44, 52), (46, 52), (37, 53), (39, 53), (40, 53), (41, 53), (42, 53), (43, 53), (44, 53), (45, 53), (46, 53), (37, 54), (38, 54), (39, 54), (40, 54), (41, 54), (44, 54), (43, 55), (44, 55), (41, 56), (42, 56), (43, 56), (44, 56), (40, 57), (41, 57), (44, 57), (45, 57), (46, 57), (47, 57), (48, 57), (49, 57), (19, 58), (20, 58), (21, 58), (40, 58), (47, 58), (48, 58), (49, 58), (19, 59), (20, 59), (21, 59), (38, 59), (39, 59), (40, 59), (47, 59), (48, 59), (49, 59), (16, 60), (17, 60), (18, 60), (19, 60), (20, 60), (21, 60), (38, 60), (39, 60), (40, 60), (16, 61), (38, 61), (39, 61), (40, 61), (16, 62), (16, 63), (16, 64), (16, 65), (23, 65), (16, 66), (16, 67), (17, 67), (18, 67), (19, 67), (19, 68), (19, 69), (19, 70), (20, 70), (21, 70), (19, 71), (20, 71), (21, 71), (19, 72), (20, 72), (21, 72)]
        for coordinat in coordinates:
            site.add_entity(INSERTER, coordinat, 0)

        log.debug(f"On site that looks like this:\n {site} ")
        log.debug(f"Find path from (46, 47) to (41, 54)")
        spring_visuals = PathFindingVisuals(width, height, site, fps=10 )
        pos_list = solver.connect_machines(site, source, target, spring_visuals)
        log.debug(pos_list)
