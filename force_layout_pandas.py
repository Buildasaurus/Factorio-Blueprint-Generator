'''The force layout pandas module does the same computation as found in spring.py
but it uses pandas to speed up calculations'''

# Standard imports
import logging
import math
from typing import List

# Third party imports
import numpy as np
import pandas as pd

# First party imports
from solver import FactoryNode
from vector import Vector



#
#  Logging
#
log = logging.getLogger(__name__)



#
#  Algorithms
#

def spring(
    machines: List[FactoryNode],
    iteration_visitor=None,
    iteration_threshold=0.1,
    borders=None,
    max_iterations=200,
):
    """
    Runs a force-layout algorithm on the given machines.

    :param machines:  The machines to move
    :param iteration_visitor:  A visitor function called after each iteration
    :param borders:  Boundaries for machine position ((min_x, min_y), (max_x, max_y))
    """
    # IDEA Examine algorithms found when searching for
    #      "force directed graph layout algorithm"
    #      One of these is a chapter in a book, published by Brown University
    #      Section 12.2 suggests using logarithmic springs and a repelling force

    c1 = 1  # Spring force multiplier
    c2 = 6  # Preferred distance along connections
    c3 = 5  # Repelling force multiplier
    c4 = 1  # Move multiplier
    preferred_border_distance = 3

    resultant_forces = [Vector() for i in range(len(machines))]
    for iteration_no in range(max_iterations):
        # lots of small iterations with small movement in each - high resolution
        for machine_index, machine in enumerate(machines):
            # calculating how all other machines affect this machine
            connections = machine.getConnections()
            connections2 = machine.getUsers()
            for other_machine in machines:
                if machine == other_machine:
                    continue

                distance = machine.distance_to(other_machine)

                if other_machine in connections or other_machine in connections2:
                    # Spring is an attracting force, positive values if far away
                    spring_force = c1 * math.log(distance / c2)
                else:
                    spring_force = 0

                repelling_force = c3 / distance**2

                # Force is the force the other machine is excerting on this machine
                # positive values means that the other machine is pushing this machine away.
                force = repelling_force - spring_force
                force_vector = other_machine.direction_to(machine).normalize() * force

                resultant_forces[machine_index] += force_vector

        if borders is not None:
            # Borders repell if you get too close
            min_pos = borders[0]
            max_pos = borders[1]
            for machine_index, machine in enumerate(machines):
                force = [0, 0]
                for d in range(2):
                    past_min_border = (
                        min_pos[d]
                        - machine.position.values[d]
                        + preferred_border_distance
                    )
                    if past_min_border > 0:
                        force[d] += past_min_border / preferred_border_distance
                    past_max_border = (
                        machine.position.values[d]
                        - max_pos[d]
                        + preferred_border_distance
                    )
                    if past_max_border > 0:
                        force[d] -= past_max_border / preferred_border_distance
                resultant_forces[machine_index] += Vector(*force)

        # Check for no more movement
        max_dist = 0
        for i in range(len(resultant_forces)):
            move_step = resultant_forces[i] * c4
            machines[i].move(move_step)
            resultant_forces[i] = Vector(0, 0)
            max_dist = max(max_dist, move_step.norm())

        if iteration_visitor:
            iteration_visitor(movement=max_dist, iteration=iteration_no, iteration_limit=max_iterations)

        if max_dist < iteration_threshold:
            break

    return machines
    