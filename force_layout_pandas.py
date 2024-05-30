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

    def node_connection_as_df():
        '''Build a DataFrame representing connected nodes. 
        This will be used for faster computation of edge force'''
        # Store machine indexes in machines list
        machine2index = {}
        for machine_index, machine in enumerate(machines):
            machine2index[machine] = machine_index

        # Store connections between macines
        m2m_connections = []
        for machine_index, machine in enumerate(machines):
            connections = machine.getConnections()
            connections2 = machine.getUsers()
            for other_machine in (set(connections) | set(connections2)) - set([machine]):
                other_index = machine2index[other_machine]
                m2m_connections.append((machine_index, other_index))

        return pd.DataFrame(m2m_connections, columns=['inx_a', 'inx_b'])
    
    node_connection = node_connection_as_df()
    
    def compute_node_repulsion():
        ''' Performs the following calculation on all nodes
            distance = machine.distance_to(other_machine)
            repelling_force_mag = c3 / distance**2
            force_vector = other_machine.direction_to(machine).normalize() * repelling_force_mag
            node_force[machine_index] += force_vector

        '''
        # Compute distance between all pairs of nodes
        node_inxpos = pd.DataFrame(node_pos)
        node_inxpos['inx'] = node_inxpos.index
        node_pair = pd.merge(node_inxpos, 
                             node_inxpos, 
                             how='cross', 
                             suffixes=('_a', '_b'))
        node_pair['x_d'] = node_pair['x_b'] - node_pair['x_a']
        node_pair['y_d'] = node_pair['y_b'] - node_pair['y_a']
        node_pair['distance_sq'] = np.square(node_pair['x_d']) + np.square(node_pair['y_d'])
        # Remove self-distance
        node_pair = node_pair[node_pair['inx_a'] != node_pair['inx_b']]
        # Compute repelling force (negative values push away, positive values pull closer)
        node_pair['force_mag'] = -c3 / node_pair['distance_sq']
        node_pair['dist_norm'] = np.sqrt(node_pair['distance_sq'])
        dist_xy = ['x_d', 'y_d']
        force_xy = ['x_force', 'y_force']
        node_pair['x_force'] = node_pair['x_d'] / node_pair['dist_norm'] * node_pair['force_mag']
        node_pair['y_force'] = node_pair['y_d'] / node_pair['dist_norm'] * node_pair['force_mag']
        # Add to node force
        #log.debug('SELECT sum(x_force), sum(y_force) GROUP BY inx_a')
        repulsion = node_pair.groupby(['inx_a'])[force_xy].sum()
        node_force['x'] += repulsion['x_force']
        node_force['y'] += repulsion['y_force']

    def compute_edge_force():
        ''' Performs the following calculation on all nodes
            distance = machine.distance_to(other_machine)
            spring_force = c1 * math.log(distance / c2)
            force_vector = other_machine.direction_to(machine).normalize() * spring_force
            node_force[machine_index] += force_vector
        '''
        # Build connected pairs by adding coordinates to connection list
        node_pair = node_connection.merge(node_pos.add_suffix('_a'), how='left', 
                                          left_on='inx_a', right_index=True)
        node_pair = node_pair.merge(node_pos.add_suffix('_b'), how='left', 
                                    left_on='inx_b', right_index=True)
        #log.debug(f'node_pair =\n{node_pair}')

        # Compute distance
        node_pair['x_d'] = node_pair['x_b'] - node_pair['x_a']
        node_pair['y_d'] = node_pair['y_b'] - node_pair['y_a']
        node_pair['distance_sq'] = np.square(node_pair['x_d']) + np.square(node_pair['y_d'])
        node_pair['dist_norm'] = np.sqrt(node_pair['distance_sq'])

        # Compute connection force, positive values if attracting
        node_pair['force_mag'] = c1 * np.log(node_pair['dist_norm'] / c2)
        node_pair['x_force'] = node_pair['x_d'] / node_pair['dist_norm'] * node_pair['force_mag']
        node_pair['y_force'] = node_pair['y_d'] / node_pair['dist_norm'] * node_pair['force_mag']

        # Add to node force
        #log.debug('SELECT sum(x_force), sum(y_force) GROUP BY inx_a')
        xy_force = ['x_force', 'y_force']
        attraction = node_pair.groupby(['inx_a'])[xy_force].sum()
        node_force['x'] += attraction['x_force']
        node_force['y'] += attraction['y_force']

    def compute_border_repulsion():
        if borders is None:
            return
        # Borders push you inside
        min_pos = borders[0]
        max_pos = borders[1]

        node_force['x'] += (min_pos[0] - node_pos['x'] + preferred_border_distance).clip(lower=0.0) / preferred_border_distance
        node_force['y'] += (min_pos[1] - node_pos['y'] + preferred_border_distance).clip(lower=0.0) / preferred_border_distance

        node_force['x'] -= (node_pos['x'] - max_pos[0] + preferred_border_distance).clip(lower=0.0) / preferred_border_distance
        node_force['y'] -= (node_pos['y'] - max_pos[1] + preferred_border_distance).clip(lower=0.0) / preferred_border_distance

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
    