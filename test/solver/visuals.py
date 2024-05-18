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
        self.ax.set_aspect("equal")
        self.ax.figure.canvas.mpl_connect('close_event', lambda event: self.max_speed())
        self.machines = None

    def max_speed(self):
        self.frame_duration = 0

    def set_machines(self, machines):
        self.machines = machines

    def machine_name(self, inx):
        node = self.machines[inx]
        if hasattr(node, 'machine'):
            return f'build {node.machine.recipe.alias}'
        if len(node.missing_input) > 0:
            item_type = list(node.missing_input.keys())[0]
            return f'provide {item_type}'
        if len(node.unused_output) > 0:
            item_type = list(node.unused_output.keys())[0]
            return f'request {item_type}'
        return hex(node.__hash__)

    def machine_colour(self, inx):
        hash_value = self.machine_name(inx).__hash__()
        r = ((hash_value >> 16) & 255) / 255.0
        g = ((hash_value >> 8) & 255) / 255.0
        b = (hash_value & 255) / 255.0
        return r, g, b

    def show_frame(self, movement=None, iteration=None, iteration_limit=None):
        if not hasattr(self, 'progress_bar'):
            import tqdm
            self.progress_bar = tqdm.tqdm(total=iteration_limit)
        self.progress_bar.set_description(f'movement={movement:.3f} ')
        self.progress_bar.update()
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        color_legend = {}
        for i, m in enumerate(self.machines):

            color = self.machine_colour(i)
            size = m.size()
            machine_shape = matplotlib.patches.Rectangle(
                m.position.values,
                width=size[0],
                height=size[1],
                color=color,
            )

            self.ax.add_patch(machine_shape)

            # Add the color and its label to the dictionary
            color_legend[self.machine_name(i)] = (
                matplotlib.patches.Patch(
                    color=color, label=self.machine_name(i)
                )
            )

        # Draw connections between machines
        color = (0.5, 0.1, 0.1)
        for m1 in self.machines:
            x1, y1 = m1.center().values
            for m2 in m1.getConnections():
                x2, y2 = m2.center().values
                self.ax.plot([x1, x2], [y1, y2], color=color)

        # Create a custom legend using the color and label pairs in the dictionary
        self.ax.legend(
            handles=list(color_legend.values()),
            bbox_to_anchor=(0.7, 0.7),
            loc="upper left",
        )

        plt.pause(self.frame_duration)

    def close(self):
        if hasattr(self, 'progress_bar'):
            self.progress_bar.close()
        print("Closing plot")
        plt.close()
