''' Flow computation.
This module computes max flow in a graph. Each node represent some kind of processing,
that could be an assembling machine or a transport belt. Edges represents transitions
from one unit to another.

Example:
  A burner drill (node A) is placed such that its output drops into a wodden box (node B)

Example:
  am1 : 1 iron gear + 1 iron plate = 2 transport belt
  am2 : 2 iron plate -> 1 iron gear
  At the top runs a transport belt with iron plate
  am1 gets iron gear directly from am2 with an inserter
  both machines gets iron plates from the upper transport belt via inserters

  node A: am1
  node B: inserter from am2 to am1
  node C: am2
  node D: inserter from upper belt to am1
  node E: inserter from upper belt to am2
  node F: belt before D
  node G: belt before E
  node H: belt between F and G

'''

import logging

import networkx

#
#  Logging
#
log = logging.getLogger(__name__)

#
#  Classes
#


class Node:
    '''A flow node represents the flow of items through an area on the map.
    It has a max capacity, that is often a complex relation between inputs and outputs.
    It may contain a recipe, in which case it also transforms some
    items to others.

    '''
    def __init__(self, id=None, name=None, inputs=None, outputs=None) -> None:
        '''
        :param id: Unique identifier for node. If left out, an UUID4 is generated.
        :param name:  Game item name, eg. 'fast-inserter'
        :param inputs:  Inbound flow. Dict that maps internal-name to quantity per second
        :param outputs:  Outbound flow. Dict that maps internal-name to quantity per second
        '''
        if id is None:
            # Use a random UUID as identifier
            import uuid
            id = uuid.uuid4()
        self.id = id

        self.name = name

        # Recipe / transformation information
        self.inputs = inputs
        self.outputs = outputs

        # Flow information
        self.throttle = 1 # 0..1 where 1 means full capacity flow

    def __repr__(self) -> str:
        name = '' if self.name is None else f'"{self.name}" '
        return f'{self.id}: {name}in={self.inputs}, out={self.outputs}, throttle={self.throttle}'

    def set_transformation(self, inputs, outputs, crafting_speed=1, time=None):
        ''' Scale a recipe by crafting speed and cycle time.
        :param inputs:  dict that maps recipe inputs to quantity per cycle
        :param outputs: dict that maps recipe outputs to quantity per cycle
        :param crafting_speed:  Machine efficiency.
            Multiply this value to the cycle speed, to find the real speed.
        :param time:  Time needed to perform one cycle of flow
        '''
        self.inputs = dict(inputs)
        self.outputs = dict(outputs)
        if 'time' in inputs:
            if time is not None:
                raise ValueError('You cannot specify time both in input and as parameter')
            time = inputs['time']
            del self.inputs['time']
        if time is None:
            raise ValueError('You must specify how much time is needed')
        # Scale max flow according to crafting speed multiplier, and recipe time
        flow_scale = crafting_speed / time
        for i in self.inputs:
            self.inputs[i] *= flow_scale
        for i in self.outputs:
            self.outputs[i] *= flow_scale


class Graph:
    '''A flow graph that links Nodes. Links are unbounded, Nodes are not.

    Edges hold a dict
        item -> items/sec
    that is computed by compute_max_flow()
    '''
    def __init__(self) -> None:
        self.graph = networkx.DiGraph()
        self.nodes = dict()

    def add_node(self, node):
        '''Add a node to the graph'''
        assert isinstance(node, Node)
        self.graph.add_node(node.id)
        self.nodes[node.id] = node
        return node

    def add_edge(self, u, v):
        '''Add a flow from node u to node v'''
        if isinstance(u, Node):
            u = u.id
        if isinstance(v, Node):
            v = v.id
        if not (u in self.nodes and v in self.nodes):
            raise ValueError("You cannot make edges between nodes the graph does not know about.")
        self.graph.add_edge(u, v)
        # Automatically determine items that can flow
        outputs = set(self.nodes[u].outputs.keys())
        inputs = set(self.nodes[v].inputs.keys())
        for item in outputs.intersection(inputs):
            self.graph.edges[u, v][item] = 1 # will be scaled by compute_max_flow

    def __str__(self) -> str:
        '''String representation of flow graph'''
        result = []
        for n in list(networkx.topological_sort(self.graph)):
            node = self.nodes[n]
            def show(s):
                return '(null)' if len(s) == 0 else ", ".join(s)
            inbound = list(self.graph.predecessors(n))
            outbound = list(self.graph.successors(n))
            result.append(f'node {node.id} - from {show(inbound)} to {show(outbound)} throttle {int(node.throttle*100)}%')
            for prev in inbound:
                for item, value in self.graph.edges[prev, n].items():
                    result.append(f'  in-flow from {prev}: {value} * {item}')
            for next in outbound:
                for item, value in self.graph.edges[n, next].items():
                    result.append(f'  out-flow  to {next}: {value} * {item}')
        return '\n'.join(result)




def join_inputs(G: Graph, n):
    '''Compute inbound flow. Reduce throttle to match'''
    node = G.nodes[n]
    log.debug(f'{n}: join inputs of {node.name} from {list(G.graph.predecessors(n))}')
    # Sum flow from all input edges
    flow_in = dict()
    v = n
    for u in G.graph.predecessors(v):
        for item, value in G.graph.edges[u, v].items():
            if item not in flow_in:
                flow_in[item] = 0
            flow_in[item] += value

    # Reduce throttle to match input
    if len(flow_in) == 0:
        # Spring node, assume throttle is correct
        pass
    else:
        assert set(flow_in.keys()) == set(node.inputs.keys())
        # Cap throttle by in-flow
        in_throttle = min(flow_in[item] / node.inputs[item] for item in flow_in)
        assert in_throttle <= node.throttle, f'{n}: FAIL {in_throttle} <= {node.throttle}'
        node.throttle = min(node.throttle, in_throttle)
        log.debug(f'{n}: flow_in = {list(flow_in.items())}, throttle := {node.throttle}')

def split_outputs(G, n):
    '''Compute outbound flow from inner flow'''
    node = G.nodes[n]

    # Sum out-flow
    flow_out = dict()
    u = n
    for v in G.graph.successors(n):
        for item, value in G.graph.edges[u, v].items():
            if item not in flow_out:
                flow_out[item] = 0
            flow_out[item] += value

    if len(list(flow_out.keys())) == 0:
        return # This is a sink node

    # How much to scale up each existing out-flow, to match throttled node output
    factor = {item: node.outputs[item] * node.throttle / flow_out[item]
              for item in node.outputs.keys()}

    # Distribute flow over edges
    for v in G.graph.successors(n):
        for item in G.graph.edges[u, v].keys():
            G.graph.edges[u, v][item] *= factor[item]


def combine_outputs(G: Graph, n):
    '''Compute initial node throttle from outbound flow limits.'''
    log.debug(f'{n}: combine outputs to reduce throttle')
    graph = G.graph
    node = G.nodes[n]
    # Sum flow in all output edges
    flow_out = dict()
    u = n
    for v in graph.successors(u):
        for item, value in graph.edges[u, v].items():
            if item not in flow_out:
                flow_out[item] = 0
            flow_out[item] += value

    # Compute throttle needed to stay below output flow
    if len(flow_out) == 0:
        # This node is a sink node. Assume all output is consumed
        node.throttle = 1
        log.debug(f' : no outputs, throttle={node.throttle}')
    else:
        assert set(flow_out.keys()) == set(node.outputs.keys())
        # Cap out-flow with internal max-flow
        node.throttle = min(flow_out[item] / node.outputs[item] for item in flow_out)
        if node.throttle > 1:
            node.throttle = 1
        log.debug(f' : {flow_out} -> throttle={node.throttle}')

def allocate_inputs(G: Graph, n):
    '''Compute node in-flow from inner flow limits'''
    node = G.nodes[n]
    log.debug(f'{n}: compute in-flow from inner flow, throttle={node.throttle}')

    flow_in = dict()
    v = n
    for u in G.graph.predecessors(v):
        for item, value in G.graph.edges[u, v].items():
            if item not in flow_in:
                flow_in[item] = 0
            if value is None:
                value = 1
            flow_in[item] += value

    if len(list(flow_in.keys())) == 0:
        return # This is a spring-node

    # How much to scale up each existing out-flow, to match throttled node output
    assert set(node.inputs.keys()) == set(flow_in.keys()), f'{set(node.inputs.keys())} == {set(flow_in.keys())}'
    factor = {item: node.inputs[item] * node.throttle / flow_in[item]
              for item in node.inputs.keys()}

    # Distribute flow over edges
    for u in G.graph.predecessors(v):
        for item in G.graph.edges[u, v].keys():
            G.graph.edges[u, v][item] *= factor[item]


def compute_max_flow(G: Graph):
    '''Compute max flow in graph that respect local max flow for all nodes
    and edges. This is done by starting at the graph output, and working
    backwards towards the start. Then working forwards again, to update
    all nodes with the resulting flow.

    :param graph:  flow.Graph to be updated with max flow values.
    '''

    # order all nodes after flow
    ordered_nodes = list(networkx.topological_sort(G.graph))

    log.debug('---- begin backward flow ----')
    log.debug(G)

    # Flow backwards, computing throttle from output limits
    for n in reversed(ordered_nodes):
        combine_outputs(G, n)
        allocate_inputs(G, n)

    log.debug('---- begin forward flow ----')
    log.debug(G)

    # Flow forwards, updating nodes on acctual flow
    for n in ordered_nodes:
        join_inputs(G, n)
        split_outputs(G, n)
