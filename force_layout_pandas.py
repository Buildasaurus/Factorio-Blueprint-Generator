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

    # Copy node positions to a DataFrame
    machine_pos = lambda m: (m.position.values[0], m.position.values[1])
    node_pos = pd.DataFrame([machine_pos(m) for m in machines], columns=['x', 'y'])
    node_force = pd.DataFrame(((0.0, 0.0), ), index=np.arange(len(machines)), columns=['x', 'y'])

    def accumulate_force(machine_index: int, force: Vector):
        '''Accumulate force for the specified machine.
        This function is intended for backwards compability while I convert the code
        It should not be present in the final set of code'''
        node_force.at[machine_index, 'x'] += force[0]
        node_force.at[machine_index, 'y'] += force[1]
    
    def compute_node_repulsion():
        for machine_index, machine in enumerate(machines):
            # calculating how all other machines affect this machine
            for other_machine in machines:
                if machine == other_machine:
                    continue

                distance = machine.distance_to(other_machine)

                spring_force = 0 # computed in compute_edge_force

                repelling_force = c3 / distance**2

                # Force is the force the other machine is excerting on this machine
                # positive values means that the other machine is pushing this machine away.
                force = repelling_force - spring_force
                force_vector = other_machine.direction_to(machine).normalize() * force

                accumulate_force(machine_index, force_vector)

    def compute_edge_force():
        for machine_index, machine in enumerate(machines):
            # calculating how all other machines affect this machine
            connections = set(machine.getConnections()) | set(machine.getUsers()) - set([machine])
            for other_machine in connections:

                distance = machine.distance_to(other_machine)

                # Spring is an attracting force, positive values if far away
                spring_force = c1 * math.log(distance / c2)

                repelling_force = 0 # computed in compute_node_repulsion

                # Force is the force the other machine is excerting on this machine
                # positive values means that the other machine is pushing this machine away.
                force = repelling_force - spring_force
                force_vector = other_machine.direction_to(machine).normalize() * force

                accumulate_force(machine_index, force_vector)

    def compute_border_repulsion():
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
                accumulate_force(machine_index, Vector(*force))

    def update_positions():
        '''Update node positions and clear force accumulator for next iteration

        :return:  Max movement performed by a node
        '''
        # Compute node movement from node force
        move_step = node_force * c4
        node_force['x'] = 0.0
        node_force['y'] = 0.0

        # Update node positions
        nonlocal node_pos
        node_pos += move_step
        move_step['norm'] = np.sqrt(np.square(move_step['x']) + np.square(move_step['y']))
        max_node_movement = move_step['norm'].max()

        # Copy node positions to machines to allow visualisation every iteration
        for i, m in enumerate(machines):
            m.position.values = (node_pos.at[i, 'x'], node_pos.at[i, 'y'])

        return max_node_movement

    for iteration_no in range(max_iterations):
        # lots of small iterations with small movement in each - high resolution

        compute_node_repulsion()
        compute_edge_force()
        compute_border_repulsion()

        max_dist = update_positions()

        if iteration_visitor:
            iteration_visitor(movement=max_dist, iteration=iteration_no, iteration_limit=max_iterations)

        if max_dist < iteration_threshold:
            break

    return machines
    