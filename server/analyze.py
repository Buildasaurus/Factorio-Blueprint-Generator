'''
This module has a number of functions to analyse a blueprint
    - extract the flow graph
    - [TODO] find flow bottlenecks
    - [TODO] expand flow graph for desired production
'''

from vector import Vector
import flow



def vec_from_xydict(xydict):
    '''Convert a blueprint position to a Vector'''
    return Vector(xydict['x'], xydict['y'])

def vec_from_dir(dir):
    return Vector(1, 0)

def extract_flow_from_site(site):
    '''Extract flow graph from construction site
    :param site: A construction site with machines and belts

    :return:  A flow.Graph with constraints set from entity prototype values. You can use this as input to flow.
    '''
    G = flow.Graph()
    entity_type = {}
    entity_center = {}
    center_entity = {}
    entity_dir = {}
    for entity in site.get_entity_list():
        try:
            enr = int(entity['entity_number'])
            entity_type[enr] = entity['name']
            pos = vec_from_xydict(entity['position'])
            entity_center[enr] = pos
            center_entity[pos] = enr
            entity_dir[enr] = entity.get('direction', 0)
            node = flow.Node(id=enr, name=entity_type[enr])
            G.add_node(node)
        except KeyError as ex:
            raise ValueError(f'Entity is incomplete: {entity}') from ex
        except:
            print(entity)
            raise
    print(G)

    # Group entities by type
    entity_kind_list = {}
    for enr, kind in entity_type.items():
        ekl = entity_kind_list.get(kind)
        if ekl is None:
            ekl = []
            entity_kind_list[kind] = ekl
        ekl.append(enr)

    # Link transport belts
    for belt in entity_kind_list.get('transport-belt', []):
        flow_dir = vec_from_dir(entity_dir[belt])
        next_pos = entity_center[belt] + flow_dir
        next_belt = center_entity.get(next_pos)
        print(f'belt {belt} at {entity_center[belt]} reach for {next_pos}, found belt {next_belt}')
        if next_belt:
            G.add_edge(belt, next_belt)

    print('---- after belt linked up ----')
    print(G)

    raise NotImplementedError()
    return G

def extract_flow_from_blueprint(bp_dict):
    '''Extract flow graph from blueprint
    :param bp_dict: A blueprint dict as exported from
    :return:  A flow.Graph with constraints set from entity prototype values. You can use this as input to flow.
    '''
    assert isinstance(bp_dict, dict)
    if not 'blueprint' in bp_dict:
        raise ValueError('Dict does not contain a blueprint')
    print(f'Blueprint content: {bp_dict["blueprint"].keys()}')
    if not 'entities' in bp_dict['blueprint']:
        raise ValueError('Not a valid blueprint dict. No entities found')
    entity_list = bp_dict['blueprint']['entities']

    # Validate entity types
    SUPPORTED_ENTITY_TYPES = set(['transport-belt'])
    IGNORED_ENTITY_TYPES = set([
        'se-electric-boiler', 'inserter', 'medium-electric-pole','aai-strongbox',
        'electric-mining-drill',
        # Ignored
        'gate', 
        'stone-wall', 
        'gun-turret', 
        'display-panel', 

        # Item transport
        'assembling-machine-1', 
        'assembling-machine-2', 
        'steel-furnace', 
        'electric-furnace', 

        'wooden-chest', 
        'storage-chest', 
        'iron-chest', 
        'steel-chest', 

        'burner-inserter', 
        'bulk-inserter', 
        'fast-inserter', 
        'stack-inserter', 
        'long-handed-inserter', 

        'fast-transport-belt', 

        'fast-underground-belt', 
        'underground-belt', 

        'splitter', 
        'fast-splitter',

        # Science
        'lab', 
        # Fluid (Water) infrastructure
        'pipe', 
        'pipe-to-ground', 
        'offshore-pump', 
        'pump', 
        'boiler',
        # Oil infrastructure
        'storage-tank', 
        'pumpjack', 
        'oil-refinery', 
        'chemical-plant',
        # Rail infrastructure
        'straight-rail', 
        'curved-rail-a', 
        'curved-rail-b', 
        'half-diagonal-rail', 
        'train-stop', 
        'rail-signal',
        'rail-chain-signal', 
        # Electricity flow
        'steam-engine', 
        'small-electric-pole', 
        'power-switch',
        'solar-panel',
        'substation', 
        'accumulator', 
        # Modules
        'beacon', 
        # Robot infrastructure
        'roboport', 
        'passive-provider-chest',
        'requester-chest',
        # Circuit network
        'decider-combinator', 
    ])
    ALLOWED_ENTITY_TYPES = SUPPORTED_ENTITY_TYPES | IGNORED_ENTITY_TYPES
    found_entity_types = set([entity['name'] for entity in entity_list])
    invalid_entity_types = found_entity_types - ALLOWED_ENTITY_TYPES
    if len(invalid_entity_types) > 0:
        raise ValueError(f'Unsupported entity types: {invalid_entity_types}')
