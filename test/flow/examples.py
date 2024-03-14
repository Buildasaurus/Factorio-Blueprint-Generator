# Test examples of Flow
import unittest
import logging

import flow

#
#  Logging
#

LOG_FILE = 'fbg.log'

def config_logging():
    formatter = logging.Formatter(style='{',
        fmt='{asctime} {module} {levelname} {message}' )

    handler = logging.FileHandler(filename=LOG_FILE, mode='w', encoding='utf-8')
    handler.setFormatter(formatter)

    root_log = logging.getLogger()
    root_log.addHandler(handler)
    root_log.setLevel(logging.DEBUG)
    return root_log

log = config_logging()
log.info('unittest of flow module')

#
#  Game constants
#

# Information from https://wiki.factorio.com/
ASSEMBLING_MACHINE_1_CRAFTING_SPEED = 0.5
TRANSPORT_BELT_TILE_SPEED = 1.875
BELT_DENSITY = 4 # one lane holds 4 items per tile
# https://wiki.factorio.com/Inserters
# speed = items/second
INSERTER_SPEED = 60/72 # 0.83 items/sec
FAST_INSERTER_SPEED = 60/26 # 2.31 items/sec

#
#  Test
#

class TestBurnerDrill(unittest.TestCase):
    '''Simple flow with burner drill and wooden box.

    A burner drill (node A) is placed such that its output drops into
      a wooden box (node B)
    '''
    def build_graph(self):
        g = flow.Graph()

        # A: Burner drill
        a = flow.Node('A')
        g.add_node(a)

        # B: wooden box
        b = flow.Node('B')
        g.add_node(b)

        g.add_edge(a, b)

        return g

    def test_burner_drill_to_box(self):
        '''Burner drill flow rate'''
        g = flow.Graph()
        g.add_node(flow.Node())

        self.assertEqual(1,1)



class TestTransportBelt(unittest.TestCase):
    '''
    Example:
    am1 : 1 iron gear + 1 iron plate = 2 transport belt
    am2 : 2 iron plate -> 1 iron gear
    At the top runs a transport belt with iron plate
    am1 gets iron gear directly from am2 with an inserter
    both machines gets iron plates from the upper transport belt via inserters

    node A: assembling-machine-1 (am1)
    node B: inserter from am2 to am1
    node C: assembling-machine-1 (am2)
    node D: inserter from upper belt to am1
    node E: inserter from upper belt to am2
    node F: belt before D
    node G: belt before E
    node H: belt between F and G

    F-H-G
    |   |
    D   E
    |   |
    A-B-C
    '''
    def build_graph(self):
        g = flow.Graph()

        # node A: am1 producing transport belt
        n = g.add_node(flow.Node('A', name='make transport belt'))
        n.set_transformation(
            outputs={'transport-belt': 1},
            inputs={'time': 0.5, 'iron-gear-wheel': 1, 'iron-plate': 1},
            crafting_speed=ASSEMBLING_MACHINE_1_CRAFTING_SPEED)

        # node B: inserter from am2 to am1
        n = g.add_node(flow.Node('B', name='inserter'))
        n.set_transformation(
            inputs={'iron-gear-wheel': 1},
            outputs={'iron-gear-wheel': 1},
            time=1/INSERTER_SPEED)

        # node C: am2 producing gears
        n = g.add_node(flow.Node('C', name='make gears'))
        n.set_transformation(
            outputs={'iron-gear-wheel': 1},
            inputs={'time': 0.5, 'iron-plate': 2},
            crafting_speed=ASSEMBLING_MACHINE_1_CRAFTING_SPEED)

        # node D: inserter from upper belt to am1
        n = g.add_node(flow.Node('D', name='inserter'))
        n.set_transformation(
            inputs={'iron-plate': 1},
            outputs={'iron-plate': 1},
            time=1/INSERTER_SPEED)

        # node E: inserter from upper belt to am2
        n = g.add_node(flow.Node('E', name='inserter'))
        n.set_transformation(
            inputs={'iron-plate': 1},
            outputs={'iron-plate': 1},
            time=1/INSERTER_SPEED)

        # node F: belt before D
        n = g.add_node(flow.Node('F', name='belt'))
        n.set_transformation(
            inputs={'iron-plate': BELT_DENSITY},
            outputs={'iron-plate': BELT_DENSITY},
            time=1/TRANSPORT_BELT_TILE_SPEED)

        # node G: belt before E
        n = g.add_node(flow.Node('G', name='belt'))
        n.set_transformation(
            inputs={'iron-plate': BELT_DENSITY},
            outputs={'iron-plate': BELT_DENSITY},
            time=1/TRANSPORT_BELT_TILE_SPEED)

        # node H: belt between F and G
        n = g.add_node(flow.Node('H', name='belt'))
        n.set_transformation(
            inputs={'iron-plate': BELT_DENSITY},
            outputs={'iron-plate': BELT_DENSITY},
            time=1/TRANSPORT_BELT_TILE_SPEED)

        g.add_edge('F','H')
        g.add_edge('H','G')
        g.add_edge('F','D')
        g.add_edge('G','E')
        g.add_edge('D','A')
        g.add_edge('E','C')
        g.add_edge('C','B')
        g.add_edge('B','A')

        return g

    def test_transport_belt_factory(self):
        '''Small factory that produces transport belts'''
        log.debug('test_transport_belt_factory')
        g = self.build_graph()
        self.assertEqual(len(g.nodes), 8)
        self.assertEqual(len(g.graph.edges), 8)
        log.debug(g)
        flow.compute_max_flow(g)
        # Look at the final assembling machine utilization
        log.debug(g.nodes['A'])
        self.assertAlmostEqual(g.nodes['A'].throttle, 0.41666, delta=0.001)

        # Change inserters moving iron-plates to fast-inserter
        def upgrade_to_fast_inserter(n):
            node = g.nodes[n]
            node.name = 'fast inserter'
            node.inputs = {item: FAST_INSERTER_SPEED for item in node.inputs.keys()}
            node.outputs = {item: FAST_INSERTER_SPEED for item in node.inputs.keys()}
        upgrade_to_fast_inserter('D')
        upgrade_to_fast_inserter('E')
        flow.compute_max_flow(g)
        log.debug(g.nodes['A'])
        self.assertAlmostEqual(g.nodes['A'].throttle, 0.83333, delta=0.001)

        # Change inserter moving gears to fast-inserter
        upgrade_to_fast_inserter('B')
        flow.compute_max_flow(g)
        log.debug(g.nodes['A'])
        self.assertAlmostEqual(g.nodes['A'].throttle, 1.0, delta=0.001)
