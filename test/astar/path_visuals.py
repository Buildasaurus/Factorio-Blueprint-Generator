import matplotlib.patches
import matplotlib.pyplot as plt
from typing import List
from layout import ConstructionSite

enabled = False


class PathFindingVisuals:
    """Show path algorithm as the pathfinder looks for direction."""

    def __init__(self, width, height, site: "ConstructionSite", fps) -> None:
        self.width = width
        self.height = height
        self.frame_duration = 1 / fps
        if enabled:
            plt.axis([0, self.width, 0, self.height])
            self.ax = plt.gca()
            self.ax.set_aspect("equal")
            self.ax.figure.canvas.mpl_connect("close_event", lambda event: self.max_speed())
        self.open_list = None
        self.closed_list = None
        self.site = site
        self.rect_size = 0.7  # pixel width of square
        self.squares = {}

    def max_speed(self):
        self.frame_duration = 0

    def reset(self):
        self.squares.clear()
        for patch in reversed(self.ax.patches):
            patch.remove()

    def set_open_list(self, machines):
        self.open_list = machines

    def set_closed_list(self, closed_list):
        self.closed_list = closed_list

    def set_start_squares(self, start_coordinates: List["tuple"]):
        self.start_squares = start_coordinates

    def set_end_squares(self, end_coordinates: List["tuple"]):
        self.end_squares = end_coordinates

    def show_frame(self, back_trace_steps: List['tuple'] = None):
        if not enabled:
            return
        color_legend = {}

        def drawsquare(coordinat, color):
            if coordinat not in self.squares:
                self.squares[coordinat] = matplotlib.patches.Rectangle(
                    coordinat,
                    width=self.rect_size,
                    height=self.rect_size,
                    color=color,
                )
                self.ax.add_patch(self.squares[coordinat])
            else:
                self.squares[coordinat].set_color(color)

        for reserved_position in self.site.reserved:
            drawsquare(reserved_position, (0, 0, 0))  # Machines and obstacles are black

        if self.open_list is not None:
            for open in self.open_list:
                drawsquare(open.position, (0, 0, 1))  # Blue meaning open

        if self.closed_list is not None:
            for closed in self.closed_list:
                drawsquare(closed.position, (1, 0, 0))  # Red meaning closed

        for end in self.end_squares:
            drawsquare(end, (0, 1, 0))  # Target squares are green

        for start in self.start_squares:
            drawsquare(start, (0.5, 0.5, 0.5))  # Start squares are gray

        if back_trace_steps is not None:
            for step in back_trace_steps:
                drawsquare(step, (1, 0.55, 0))  # backtracing is dark orange

        # Create a custom legend using the color and label pairs in the dictionary
        self.ax.legend(
            handles=list(color_legend.values()),
            bbox_to_anchor=(0.7, 0.7),
            loc="upper left",
        )

        plt.pause(self.frame_duration)
