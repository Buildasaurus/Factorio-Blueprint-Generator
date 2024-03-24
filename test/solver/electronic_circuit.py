# Test solver by producing electronic circuits

import unittest
import logging

import factoriocalc as fc
import factoriocalc.presets as fcc
import matplotlib.patches
import matplotlib.pyplot as plt

import layout
import solver

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
#  Visuals for layout
#

class ForceAlgorithmVisuals:
    '''Show machine layout as the force algorithm moves them around.'''

    def __init__(self, width, height, fps) -> None:
        self.width = width
        self.height = height
        self.frame_duration = 1/fps
        plt.axis([0, self.width, 0, self.height])
        self.ax = plt.gca()
        self.ax.figure.canvas.mpl_connect('close_event', lambda event: self.max_speed())
        self.machines = None

    def max_speed(self):
        self.frame_duration = 0

    def set_machines(self, machines):
        self.machines = machines

    def machine_colour(self, inx):
        hash_value = self.machines[inx].machine.recipe.alias.__hash__()
        r = ((hash_value >> 16) & 255) / 255.0
        g = ((hash_value >> 8) & 255) / 255.0
        b = (hash_value & 255) / 255.0
        return r, g, b
    
    def show_frame(self):
        color_legend = {}
        for i in range(len(self.machines)):

            color = self.machine_colour(i)
            machine_shape = matplotlib.patches.Rectangle(
                self.machines[i].position.values,
                width=3,
                height=3,
                color=color,
            )

            self.ax.add_patch(machine_shape)

            # Add the color and its label to the dictionary
            color_legend[self.machines[i].machine.recipe.alias] = (
                matplotlib.patches.Patch(
                    color=color, label=self.machines[i].machine.recipe.alias
                )
            )

        # Draw connections between machines
        color = (0.5, 0.1, 0.1)
        for m1 in self.machines:
            x1, y1 = m1.position.values
            for m2 in m1.getConnections():
                x2, y2 = m2.position.values
                self.ax.plot([x1, x2], [y1, y2], color=color)

        # Create a custom legend using the color and label pairs in the dictionary
        self.ax.legend(
            handles=list(color_legend.values()),
            bbox_to_anchor=(0.7, 0.7),
            loc="upper left",
        )

        plt.pause(self.frame_duration)
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)


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
        visuals = ForceAlgorithmVisuals(WIDTH, HEIGHT, fps=20)
        visuals.set_machines(machines)
        solver.spring(machines, visuals.show_frame, borders=((0, 0), (WIDTH, HEIGHT)))
        print("Machines are at: " + str([machine.position for machine in machines]))
        solver.machines_to_int(machines)
        print("Machines are at: " + str([machine.position for machine in machines]))
        solver.place_on_site(site, machines)
        solver.connect_points(site,1,1, 50,50)
        print(site)
        print(layout.site_as_blueprint_string(site, label="test of blueprint code"))
