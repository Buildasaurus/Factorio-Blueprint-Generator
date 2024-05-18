import matplotlib.patches
import matplotlib.pyplot as plt
from typing import List


class PathFindingVisuals:
    """Show path algorithm as the pathfinder looks for direction."""

    def __init__(self, width, height, fps) -> None:
        self.width = width
        self.height = height
        self.frame_duration = 1 / fps
        plt.axis([0, self.width, 0, self.height])
        self.ax = plt.gca()
        self.ax.figure.canvas.mpl_connect("close_event", lambda event: self.max_speed())
        self.open_list = None
        self.closed_list = None
        self.rect_size = 1  # pixels width

    def max_speed(self):
        self.frame_duration = 0

    def set_open_list(self, machines):
        self.open_list = machines

    def set_closed_list(self, closed_list):
        self.closed_list = closed_list

    def set_start_squares(self, start_coordinates: List['tuple']):
        self.start_squares = start_coordinates

    def set_end_squares(self, end_coordinates: List['tuple']):
        self.end_squares = end_coordinates

    def show_frame(self):
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        color_legend = {}

        def drawsquare(coordinat, color):
            machine_shape = matplotlib.patches.Rectangle(
                coordinat,
                width=self.rect_size,
                height=self.rect_size,
                color=color,
            )

            self.ax.add_patch(machine_shape)




        for counter, open in enumerate(self.open_list):
            drawsquare(open.position, (0, 0, 1))  # Blue meaning open

        for counter, closed in enumerate(self.closed_list):
            drawsquare(closed.position, (1, 0, 0))  # Red meaning closed

        for end in self.end_squares:
            drawsquare(end, (0, 1, 0))  # Target squares are green
        for start in self.start_squares:
            drawsquare(start, (0, 0, 0))  # Start squares are black

        # Create a custom legend using the color and label pairs in the dictionary
        self.ax.legend(
            handles=list(color_legend.values()),
            bbox_to_anchor=(0.7, 0.7),
            loc="upper left",
        )

        plt.pause(self.frame_duration)
