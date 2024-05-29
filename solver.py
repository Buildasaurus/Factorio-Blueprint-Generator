"""
A module that generate blueprints from a certain input, to a certain output, on a certain
amount of space in Factorio.
"""

# Standard imports
import logging
import math
import random
from typing import List

# Third party imports
from factoriocalc import Machine, Item

# First party imports
from vector import Vector
from a_star_factorio import A_star

from layout import ConstructionSite

import layout


#
#  Logging
#
log = logging.getLogger(__name__)


#
#  Helper functions
#

def change_key_value(dict, key, value):
    if key not in dict:
        dict[key] = 0
    dict[key] += value
    assert dict[key] >= 0

#
#  classes
#

class FactoryNode:
    """An abstraction of machines and ports used to find rough layout."""

    def __init__(self, position=None, item_input={}, item_output={}):
        """Create a FactoryNode

        :param position:  Upper left position of node
        :param item_input:  Dict of requested input flow
        :param item_output:  Dict of requested output flow
        """
        self.position = position
        self.input_nodes = []
        self.output_nodes = []
        self.missing_input = dict(item_input)
        self.unused_output = dict(item_output)

    def size(self):
        """Returns a tuple representing the size"""
        return (0, 0)

    def center(self) -> Vector:
        """Returns a position at the center of the node. Coordinates may be floats."""
        return self.position + (Vector(*self.size()) / 2)

    def direction_to(self, other: "FactoryNode") -> Vector:
        """
        :return: a vector pointing from this node, to the other node.
        """
        return other.center() - self.center()

    def distance_to(self, other: "FactoryNode") -> float:
        offset = self.direction_to(other)
        return math.sqrt(offset.inner(offset))

    def move(self, direction: Vector):
        """Move node position the specified amount"""
        self.position += direction

    def overlaps(self, other: "FactoryNode") -> bool:
        """Check if two square nodes overlap"""
        min_dist = [(self.size()[i] + other.size()[i]) / 2 for i in range(2)]
        return (
            abs(self.center()[0] - other.center()[0]) < min_dist[0]
            and abs(self.center()[1] - other.center()[1]) < min_dist[1]
        )

    def getConnections(self) -> List['FactoryNode']:
        return self.input_nodes

    def getUsers(self) -> List['FactoryNode']:
        return self.output_nodes

    def change_flow_request(self, direction, item_type, delta_rate):
        '''Change requested flow of a particular item type through node.

        :param direction:  'input' for input flow, 'output' for output flow
        :param item_type:  The item flow to address
        :param delta_rate:  Change of flow measured in items per second. Negative to reduce flow'''
        if item_type is None or delta_rate == 0:
            return
        if direction == 'input':
            flow = self.missing_input
        elif direction == 'output':
            flow = self.unused_output
        else:
            raise ValueError('direction must be either "input" or "output"')
        change_key_value(flow, item_type, delta_rate)

    def consume_from(self, other: "FactoryNode", item_type):
        """Set up a connection from other node to this node

        :param other:  source of items
        :param item_type:  item type to get from source
        """
        assert isinstance(other, FactoryNode)

        # Rename parameters
        source = other
        target = self

        # Link nodes
        target.input_nodes.append(source)
        source.output_nodes.append(target)

        # Compute how much flow is still not accounted for
        output_items = set(source.unused_output.keys())
        input_items = set(target.missing_input.keys())
        flow_sum = 0
        for item_type in output_items.intersection(input_items):
            flow_rate = min(source.unused_output[item_type],
                            target.missing_input[item_type])
            flow_sum += flow_rate
            source.change_flow_request('output', item_type, -flow_rate)
            target.change_flow_request('input', item_type, -flow_rate)
        assert flow_sum > 0


class FakeMachine(FactoryNode):
    def __init__(self, position, size):
        super().__init__(position)
        self.stored_size = size

    def size(self):
        return self.stored_size

class Port(FactoryNode):
    """A point where a factory exchanges items with its surroundings.
    This is usually a transport-belt tile, but can also be a provider chest
    or requester chest."""

    def __init__(self, position=None, item_type=None, rate=0):
        """Create an external port for a factory.

        :param position:  The position of the port
        :param item_type:  The item type exchanged here
        :param rate:  The flow through this port, measured in items per second.
            Positive means output from factory, negative means input to factory.
        """
        super().__init__(position=position)
        if rate > 0:
            direction = 'output'
        elif rate < 0:
            direction = 'input'
            rate = -rate
        else:
            return
        self.change_flow_request(direction, item_type, rate)

    def size(self):
        return (1, 1)

    @property
    def name(self):
        '''Return the factoro entity name'''
        if len(self.missing_input) > 0:
            return 'logistic-chest-passive-provider'
        if len(self.unused_output) > 0:
            return 'logistic-chest-requester'
        return 'chest'



class LocatedMachine(FactoryNode):
    "A data class to store a machine and its position"

    def __init__(self, machine: Machine, position=None):
        # Items pr second - True to make it calculate actual value.
        flow_by_item = machine.flows(True).byItem

        super().__init__(
            position=position,
            item_input={
                key: value.rateIn
                for key, value in flow_by_item.items()
                if value.rateIn != 0
            },
            item_output={
                key: value.rateOut
                for key, value in flow_by_item.items()
                if value.rateOut != 0
            }
        )
        self.machine = machine

    def size(self):
        return layout.entity_size(self.machine.name)

    def set_random_position(self, site_size):
        """Place the machine on a random position inside the provided dimension"""
        my_size = self.size()
        top_left = (0, 0)
        corner_range = [site_size[i] - my_size[i] for i in range(2)]
        self.position = random_position(top_left, corner_range)

    def __str__(self) -> str:
        "Converts the LocatedMachine to a nicely formatted string"
        return str(self.machine) + " at " + str(self.position)


def random_position(min_pos, max_pos):
    """Provide a random position in the given bounderies"""
    random_pos = [min_pos[i] + random.random() * (max_pos[i] - min_pos[i]) for i in range(2)]
    return Vector(*random_pos)

def randomly_placed_machines(factory, site_size):
    """
    Gives machines needed by the factory a random location.

    :returns: a list of LocatedMachines.
    """
    boxed_machines = factory.inner.machine.machines

    located_machines = []
    for machine in boxed_machines:
        for _ in range(machine.num):
            located_machine = LocatedMachine(machine.machine)
            located_machine.set_random_position(site_size)
            located_machines.append(located_machine)

    return located_machines


def add_connections(machines: List[LocatedMachine]):
    """
    Connect machines such that input and output match.
    Add ports when input or output is missing.
    """
    new_ports = []
    port_for = {}
    def find_port(item_type, pos) -> Port:
        """Find a port ready for a connection of a specific type"""
        if item_type in port_for:
            # A port may have at most 4 connections
            port = port_for[item_type]
            connection_count = len(port.input_nodes) + len(port.output_nodes)
            if connection_count >= 4:
                del port_for[item_type]
        if item_type not in port_for:
            log.debug(f'Create Port for {item_type}')
            new_ports.append(Port(pos))
            port_for[item_type] = new_ports[-1]
        return port_for[item_type]
    def find_input_port(item, rate, pos):
        # A factory input port is a requester chest with output to the factory
        port = find_port(item_type, pos)
        port.change_flow_request('output', item_type, rate)
        return port
    def find_output_port(item, rate, pos):
        # An factory output port is a provider chest with input from the factory
        port = find_port(item_type, pos)
        port.change_flow_request('input', item_type, rate)
        return port

    # Connect all machines to suppliers
    for target_machine in machines:
        for item_type in target_machine.machine.inputs:
            while target_machine.missing_input.get(item_type, 0) > 0:
                source_machine = find_machine_with_unused_output(machines, item_type)
                if source_machine is None:
                    # Not enough supplies, get it from an input port
                    pos = target_machine.position + random_position((-1, -1), (1, 1))
                    rate = target_machine.missing_input[item_type]
                    source_machine = find_input_port(item_type, rate, pos)
                target_machine.consume_from(source_machine, item_type)

    # Find machines that supplies stuff that is not consumed
    for machine in machines:
        for item_type, rate in machine.unused_output.items():
            if rate > 0:
                pos = machine.position + random_position((-1, -1), (1, 1))
                port = find_output_port(item_type, rate, pos)
                port.consume_from(machine, item_type)

    # Add found ports to machine list
    machines.extend(new_ports)

def spring_1(
    machines: List[LocatedMachine],
    iteration_visitor=None,
    iteration_threshold=0.1,
    borders=None,
    max_iterations=200,
):
    """
    Does the spring algorithm on the given machines, and returns them after
    Will treat input as a list of floats

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

# Select which spring function to use
use_old_spring = True
if use_old_spring:
    spring = spring_1
else:
    import force_layout_pandas
    spring = force_layout_pandas.spring

def find_machine_with_unused_output(machines: List[LocatedMachine], item_type):
    '''Find a machine with excess production'''
    log.debug("looking for machine that has unused " + str(item_type))

    # Each candidate is a pair (unused_output, machine)
    machine_candidates = [(m.unused_output[item_type], m)
            for m in machines
            if m.unused_output.get(item_type, 0) > 0]

    if len(machine_candidates) == 0:
        log.debug(f" no machine has unused {item_type}")
        return None

    unused_output = lambda candidate: candidate[0]
    return min(machine_candidates, key=unused_output)[1]


def machines_to_int(machines: List[LocatedMachine]):
    "Assumes that the machines are not overlapping in any way"
    for machine in machines:
        machine.position = machine.position.as_int()


def place_on_site(site: 'ConstructionSite', machines: List[LocatedMachine], path_visiualizer = None):
    """
    Place machines on the construction site

    :param site:  A ConstructionSite that is sufficiently large
    :param machines:  A list of LocatedMachine
    """
    for lm in machines:
        if hasattr(lm, 'machine'):
            machine = lm.machine
            site.add_entity(machine.name, lm.position, 0, machine.recipe.name)
        else:
            site.add_entity(lm.name, lm.position, 0)
    for target in machines:
        for source in target.getConnections():
            try:
                before_string = layout.site_to_test(site, source, target)
                connect_machines(site, source, target, visualizer=path_visiualizer)
            except Exception as ex:
                log.error(ex)
                log.debug("Error was thrown at place on site, this is the scenario")
                log.debug(before_string)
                log.debug('This is the exception traceback', exc_info=True)
                raise



def connect_machines(
    site: ConstructionSite,
    source: FactoryNode,
    target: FactoryNode,
    visualizer = None,
    inserter="inserter",
    belt="transport-belt",
):
    """Connect two machines by adding a transport belt to the
    construction site.

    :param site: The site to build on
    :param source: Source machine
    :param target: Target machine
    :param inserter: Type of inserter to use
    :param belt: Type of belt to use
    """
    # Check for unsupported configuration
    if target.overlaps(source):
        raise ValueError("Machines overlap")
    # Find an open path between machines
    pos_list = find_path(site, source, target, path_visualizer = visualizer)
    if len(pos_list) == 0:
        raise ValueError("No possible path")
    assert len(pos_list) >= 3, "Path below length 3 is not supported"
    # Find proper orientation of belt cells
    dir_list = []
    for i in range(len(pos_list) - 1):
        dir_list.append(layout.direction_to(pos_list[i], pos_list[i + 1]))
    dir_list.append(dir_list[-1])  # repeat last direction

    # Find entity kind
    underground_belt = (
        'underground-belt'  if belt == 'transport-belt'
        else 'fast-underground-belt' if belt == 'fast-transport-belt'
        else 'express-underground-belt' if belt == 'express-transport-belt'
        else '<undefined-underground-belt>')
    #underground_belt = 'express-underground-belt'
    max_underground_length = {
        'underground-belt': 4,
        'fast-underground-belt': 6,
        'express-underground-belt': 8,
    }
    def pos_distance(i,j):
        return ( abs(pos_list[j][0] - pos_list[i][0])
               + abs(pos_list[j][1] - pos_list[i][1]) )
    def step_size(i):
        return pos_distance(i-1, i)
    # First and last is inserter, rest is transport belt
    kind_list = [inserter if i == 0 or i + 1 == len(dir_list) else belt
            for i, _ in enumerate(pos_list)]
    # Convert kind to underground input or output when there is a gap
    for i, kind in enumerate(kind_list):
        if kind == inserter: continue
        underground_length = step_size(i) - 1
        if underground_length > 0:
            # Check max length underground
            if underground_length > max_underground_length[underground_belt]:
                raise ValueError(f'{underground_belt} cannot go {underground_length} tiles under ground'
                                 +f' from {pos_list[i-1]} to {pos_list[i]}')
            # Check that input belt is aligned with underground belts
            if kind_list[i-2] == belt and dir_list[i-2] != dir_list[i-1]:
                raise ValueError(f'Underground belt from {pos_list[i-1]} to {pos_list[i]} was preceeded by a belt at {pos_list[i-2]}')
            # Check that output belt is aligned with underground belt
            if kind_list[i+1] == belt and dir_list[i-1] != dir_list[i]:
                raise ValueError(f'Underground belt from {pos_list[i-1]} to {pos_list[i]} was follwed by a belt at {pos_list[i+1]}')
            # Convert to underground section
            kind_list[i-1] = underground_belt
            kind_list[i] = underground_belt
            dir_list[i] = dir_list[i-1] # if inserter on the side

    # Add belt and inserters to site
    for i in range(len(dir_list)):
        kind = kind_list[i]
        dir = dir_list[i]
        kwarg = dict()
        if kind == inserter:
            dir = (dir + 4) % 8
        if kind == underground_belt:
            kwarg['type'] = 'input' if step_size(i) == 1 else 'output'
        log.debug(f'{kind} at {pos_list[i]} dir {dir} type {kwarg.get("type")}')
        site.add_entity(kind, pos_list[i], dir, **kwarg)


def find_path(
    site: ConstructionSite, source: FactoryNode, target: FactoryNode, path_visualizer = None
) -> List[tuple]:
    """Generates a list of coordinates, to walk from one machine to the other

    :param site: The site knows which coordinates are already taken
    :param source: Source machine
    :param target: Target machine
    :returns: a list of site coordinates between the two machines
    """
    #TODO - rewrite this, as we don't need an entire map anymore
    map = []
    BLOCKED = 0
    NORMAL = 1
    EXPENSIVE = 2
    for r in range(site.size()[1]):
        row = []
        for c in range(site.size()[0]):
            row.append(BLOCKED if site.is_reserved(c, r) else NORMAL)
        map.append(row)

    # Make source and target machines expensive, but not impossible to travel
    # For each direction in the two dimensions, create starting squares
    # x and y are the inserter coordinates
    def add_entry_if_free(inserter_pos, step, entry_list):
        x, y = inserter_pos
        if not is_in_bounds(x, y, map) or map[y][x] == BLOCKED:
            return
        x, y = (Vector(*inserter_pos) + Vector(*step)).values
        if not is_in_bounds(x, y, map) or map[y][x] == BLOCKED:
            return
        entry_list.append((x,y))
        x, y = inserter_pos

    fac_coordinates = [[] for i in range(2)]
    for i, m in enumerate([source, target]):
        pos = m.position.as_int()

        for row in range(m.size()[1]):

            # right side
            x = pos[0] + m.size()[0]
            y = pos[1] + row
            add_entry_if_free((x, y), (1, 0), fac_coordinates[i])

            # left side
            x = pos[0] - 1
            y = pos[1] + row
            add_entry_if_free((x, y), (-1, 0), fac_coordinates[i])

        for column in range(m.size()[0]):

            # downwards side
            x = pos[0] + column
            y = pos[1] + m.size()[1]
            add_entry_if_free((x, y), (0, 1), fac_coordinates[i])

            # upwards side
            x = pos[0] + column
            y = pos[1] - 1
            add_entry_if_free((x, y), (0, -1), fac_coordinates[i])

        if len(fac_coordinates[i]) == 0:
            return None

    fac_finder = A_star(site,fac_coordinates[0],fac_coordinates[1])
    fac_path = fac_finder.find_path(True, path_visualizer)
    log.debug("nodecount: " + str(len(fac_path)))
    for node in fac_path:
        log.debug(node)

    # Add inserter at both ends of path
    sign = lambda x: 1 if x > 0 else -1
    def step_one(ofs: Vector):
        if abs(ofs.values[0]) > abs(ofs.values[1]):
            # move horizontally
            return Vector(sign(ofs.values[0]), 0)
        else:
            # move vertically
            return Vector(0, sign(ofs.values[1]))
    belt_center = lambda xy: Vector(*xy) + Vector(0.5, 0.5)
    def step_towards(machine, origin):
        next_pos = Vector(*origin) + step_one(machine.center() - belt_center(origin))
        return (next_pos[0], next_pos[1])
    xypath = fac_path
    if len(xypath) > 0:
        xypath.insert(0, step_towards(source, xypath[0]))
        xypath.append(step_towards(target, xypath[-1]))

    return xypath


def is_in_bounds(x, y, map):
    return x >= 0 and y >= 0 and x < len(map[0]) and y < len(map)

if __name__ == "__main__":
    """Test code executed if run from command line"""
    import test.solver
    import test.layout
    import unittest

    #unittest.main(defaultTest="test.solver.electronic_circuit", verbosity=2)
    unittest.main(defaultTest="test.layout.route_finding", verbosity=2)
