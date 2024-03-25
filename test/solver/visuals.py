import matplotlib.patches
import matplotlib.pyplot as plt

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
        self.ax.set_ylim(0, self.height
                         )
    def close(self):
        print("Closing plot")
        plt.close()
