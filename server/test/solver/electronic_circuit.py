# Test solver by producing electronic circuits

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
        log.debug("Machines are at: " + str([machine.position for machine in machines]))
        solver.machines_to_int(machines)
        log.debug("Machines are at: " + str([machine.position for machine in machines]))
        spring_visuals = PathFindingVisuals(WIDTH, HEIGHT,site, fps=60)
        solver.place_on_site(site, machines, spring_visuals)
        log.debug(site)
        log.debug(layout.site_as_blueprint_string(site, label="test of blueprint code"))
        log.debug("End of test")


    '''Demonstrates problem where no path is found.'''
    def test_recurring_incorrect_belt(self):
        print("AssemblingMachine1(electronic_circuit) and AssemblingMachine1(assembling_machine_1)")
        width = 64
        height = 64
        site = layout.ConstructionSite(width, height)
        source = solver.FakeMachine(Vector(38, 37), (3,3))
        target = solver.FakeMachine(Vector(36, 21), (3,3))

        # Drawing flipped on its head
        coordinates = [(35, 11), (36, 11), (37, 11), (35, 12), (36, 12), (37, 12), (39, 12), (40, 12), (41, 12), (45, 12), (35, 13), (36, 13), (37, 13), (39, 13), (40, 13), (41, 13), (35, 14), (39, 14), (40, 14), (41, 14), (14, 15), (15, 15), (16, 15), (24, 15), (25, 15), (26, 15), (31, 15), (32, 15), (33, 15), (34, 15), (35, 15), (39, 15), (14, 16), (15, 16), (16, 16), (24, 16), (25, 16), (26, 16), (31, 16), (32, 16), (33, 16), (34, 16), (38, 16), (39, 16), (46, 16), (47, 16), (48, 16), (8, 17), (9, 17), (10, 17), (14, 17), (15, 17), (16, 17), (17, 17), (18, 17), (19, 17), (24, 17), (25, 17), (26, 17), (31, 17), (32, 17), (33, 17), (34, 17), (35, 17), (36, 17), (37, 17), (38, 17), (46, 17), (47, 17), (48, 17), (8, 18), (9, 18), (10, 18), (17, 18), (18, 18), (19, 18), (24, 18), (33, 18), (34, 18), (35, 18), (36, 18), (37, 18), (38, 18), (46, 18), (47, 18), (48, 18), (8, 19), (9, 19), (10, 19), (17, 19), (18, 19), (19, 19), (24, 19), (33, 19), (34, 19), (35, 19), (36, 19), (37, 19), (38, 19), (39, 19), (46, 19), (57, 19), (24, 20), (33, 20), (34, 20), (38, 20), (42, 20), (44, 20), (45, 20), (46, 20), (24, 21), (33, 21), (34, 21), (35, 21), (36, 21), (37, 21), (38, 21), (39, 21), (40, 21), (41, 21), (42, 21), (43, 21), (44, 21), (48, 21), (49, 21), (50, 21), (17, 22), (18, 22), (19, 22), (33, 22), (34, 22), (35, 22), (36, 22), (37, 22), (38, 22), (39, 22), (40, 22), (41, 22), (48, 22), (49, 22), (50, 22), (11, 23), (17, 23), (18, 23), (19, 23), (27, 23), (31, 23), (32, 23), (33, 23), (34, 23), (35, 23), (36, 23), (37, 23), (38, 23), (39, 23), (40, 23), (41, 23), (48, 23), (49, 23), (50, 23), (17, 24), (18, 24), (19, 24), (20, 24), (21, 24), (22, 24), (23, 24), (24, 24), (31, 24), (32, 24), (33, 24), (34, 24), (35, 24), (38, 24), (40, 24), (41, 24), (24, 25), (25, 25), (29, 25), (30, 25), (31, 25), (32, 25), (33, 25), (35, 25), (38, 25), (40, 25), (41, 25), (24, 26), (25, 26), (29, 26), (35, 26), (36, 26), (37, 26), (38, 26), (40, 26), (41, 26), (44, 26), (45, 26), (46, 26), (24, 27), (25, 27), (26, 27), (27, 27), (28, 27), (29, 27), (35, 27), (36, 27), (37, 27), (38, 27), (40, 27), (41, 27), (44, 27), (45, 27), (46, 27), (24, 28), (25, 28), (26, 28), (27, 28), (35, 28), (36, 28), (37, 28), (38, 28), (39, 28), (40, 28), (41, 28), (44, 28), (45, 28), (46, 28), (24, 29), (25, 29), (26, 29), (27, 29), (28, 29), (29, 29), (30, 29), (31, 29), (32, 29), (33, 29), (34, 29), (35, 29), (36, 29), (37, 29), (39, 29), (40, 29), (41, 29), (49, 29), (50, 29), (51, 29), (24, 30), (25, 30), (26, 30), (27, 30), (28, 30), (29, 30), (30, 30), (31, 30), (32, 30), (37, 30), (38, 30), (39, 30), (40, 30), (41, 30), (49, 30), (50, 30), (51, 30), (6, 31), (7, 31), (8, 31), (29, 31), (30, 31), (31, 31), (32, 31), (33, 31), (34, 31), (35, 31), (36, 31), (37, 31), (38, 31), (39, 31), (40, 31), (41, 31), (49, 31), (50, 31), (51, 31), (6, 32), (7, 32), (8, 32), (19, 32), (29, 32), (30, 32), (31, 32), (32, 32), (33, 32), (34, 32), (35, 32), (36, 32), (37, 32), (38, 32), (39, 32), (40, 32), (41, 32), (6, 33), (7, 33), (8, 33), (29, 33), (30, 33), (31, 33), (45, 33), (46, 33), (47, 33), (45, 34), (46, 34), (47, 34), (45, 35), (46, 35), (47, 35), (57, 35), (38, 37), (39, 37), (40, 37), (38, 38), (39, 38), (40, 38), (5, 39), (6, 39), (7, 39), (25, 39), (26, 39), (27, 39), (31, 39), (32, 39), (33, 39), (38, 39), (39, 39), (40, 39), (5, 40), (6, 40), (7, 40), (25, 40), (26, 40), (27, 40), (31, 40), (32, 40), (33, 40), (5, 41), (6, 41), (7, 41), (25, 41), (26, 41), (27, 41), (31, 41), (32, 41), (33, 41), (36, 45), (37, 45), (38, 45), (44, 45), (2, 46), (30, 46), (36, 46), (37, 46), (38, 46), (9, 47), (36, 47), (37, 47), (38, 47)]
        for coordinat in coordinates:
            site.add_entity(INSERTER, coordinat, 0)

        log.debug(f"On site that looks like this:\n {site} ")
        log.debug(f"Find path from (38, 37) to (36, 21)")
        spring_visuals = PathFindingVisuals(width, height, site, fps=60 )
        pos_list = solver.connect_machines(site, source, target, spring_visuals)
        log.debug(pos_list)
