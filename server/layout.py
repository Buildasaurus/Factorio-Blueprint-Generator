'''
Functions related to placing machines on a grid.
'''

import logging

from constants import Direction

MACHINES_WITH_RECIPE = {
    'assembling-machine-1',
    'assembling-machine-2',
}

log = logging.getLogger(__name__)

class ConstructionSite:
    '''Representation of the area to layout a factory'''

    def __init__(self, x_size, y_size):
        # self.reserved is a sparse array, containing only those cells that
        # have been reserved. This means it will work for very large
        # dimensions as long as they are not fully utilized.
        self.reserved = {}
        self.dim_x = x_size
        self.dim_y = y_size
        self.entities = []

    def size(self):
        '''Return an (width, height) tuple'''
        return (self.dim_x, self.dim_y)

        if len(self.reserved) == 0:
            self.dim_x, self.dim_y = 0, 0
            return
    def is_reserved(self, x, y) -> bool:
        '''Test if a given grid cell is free or not'''
        pos = (int(x), int(y))
        return self.reserved.get(pos, False)

    def reserve(self, x, y) -> bool:
        '''Allocate the given grid cell'''
        pos = (int(x), int(y))
        if self.is_reserved(*pos):
            raise ValueError(f'Cell {pos} is already reserved')
        self.reserved[pos] = True

    def __str__(self) -> str:
        result = []
        for y in range(self.dim_y):
            for x in range(self.dim_x):
                ch = '#' if self.is_reserved(x, y) else '.'
                result.append(ch)
            result.append('\n')
        return ''.join(result)

    def add_entity(self, kind, pos, direction, recipe=None, type=None, recipe_quality=None, items=None, bar=None, control_behavior=None,
            request_filters=None
        ):
        '''Add an entity to the construction site

        :param kind:  Entity type name
        :param pos:  An (x,y) tuple pointing at the top left corner where the machine should be placed.
            Note: This is different from how Factorio blueprints works
        :param direction:  Entity direction
        :param recipe:  What recipe should the machine produce
        :param recipe_quality:  What quality should the machine produce
        :param items:  Modules installed in machine
        :param type:  Must be set to "input" or "output" for underground belts.
        :param bar:  ?? found on passive-provider-chest
        :param control_behavior:  ?? found on logistic_condition
        :param request_filters: ??
        '''
        x, y = pos
        if not (
            (isinstance(x, int) or x.is_integer())
            and (isinstance(y, int) or y.is_integer())
        ):
            raise ValueError(f'Position must be integer only. Was {pos}')

        # Only allow recipe on machines we know can have one
        if recipe is not None and kind not in MACHINES_WITH_RECIPE:
            raise ValueError(f"I'm not aware that a {kind} can have a recipie")
        if recipe is not None and not isinstance(recipe, str):
            raise ValueError(f"The recipe must be a string, but was a {type(recipe)}")

        # Type is used for underground belt
        UNDERGROUND_KIND = ['underground-belt', 'fast-underground-belt', 'express-underground-belt']
        if kind in UNDERGROUND_KIND:
            VALID_TYPE = ['input', 'output']
            if type not in VALID_TYPE:
                raise ValueError(f"Underground belt must have a type specified, either input or output")
        else:
            if type is not None:
                raise ValueError('"type" parameter is only valid for underground belt')

        # Place machine
        for ofs in iter_entity_area(kind, direction):
            self.reserve(pos[0] + ofs[0], pos[1] + ofs[1])

        # Remember machine information
        entity = dict(kind=kind, pos=pos[:], direction=direction)
        if recipe:
            entity['recipe'] = recipe
        if recipe_quality:
            entity['recipe_quality'] = recipe_quality
        if items:
            entity['items'] = items
        if type:
            entity['type'] = type
        if bar:
            entity['bar'] = bar
        if control_behavior:
            entity['control_behavior'] = control_behavior
        if request_filters:
            entity['request_filters'] = request_filters
        self.entities.append(entity)

    def get_entity_list(self):
        '''Return all entities added in a form ready for Blueprint generation'''

        center_pos = {i: center_position(e['kind'], e['direction'], e['pos'])
                      for i, e in enumerate(self.entities)}
        EXPORT_KEYS = set([
            'recipe',
            'recipe_quality',
            'items',
            'type',
            'bar',
            'control_behavior',
            'request_filters',
        ])
        result = []
        for i, e in enumerate(self.entities):
            result.append(dict(
                name=e['kind'],
                position=dict(x=center_pos[i][0], y=center_pos[i][1]),
                direction=e['direction'],
                entity_number=i+1
            ))
            for key in EXPORT_KEYS.intersection(e.keys()):
                result[-1][key] = e[key]
        return result

ENTITY_SIZE = {
    'wooden-chest': (1,1),
    'iron-chest': (1,1),
    'transport-belt': (1,1),
    'underground-belt': (1,1),
    'fast-underground-belt': (1,1),
    'express-underground-belt': (1,1),
    'small-electric-pole': (1,1),
    'medium-electric-pole': (1,1),
    'inserter': (1,1),
    'gun-turret': (2,2),
    'aai-strongbox': (2,2),
    'electric-mining-drill': (3,3),
    'assembling-machine-1': (3,3),
    'assembling-machine-2': (3,3),
    'assembling-machine-3': (3,3),
    'se-electric-boiler': (3,2),
    'logistic-chest-requester': (1,1),
    'logistic-chest-passive-provider': (1,1),
}

def factoriocalc_entity_size(machine_name):
    import factoriocalc
    machine_class = factoriocalc.mchByName.get(machine_name)
    if machine_class is None:
        return None
    machine_instance = machine_class()
    return machine_instance.width, machine_instance.height

def entity_size(entity_name, direc: Direction = 0):
    size = factoriocalc_entity_size(entity_name)
    size = ENTITY_SIZE.get(entity_name) if size is None else size
    assert size is not None, f'Unknown entity {entity_name}'
    if direc in [Direction.EAST, Direction.WEST]:
        # Switch x and y size
        y, x = size
        size = [x,y]
    return size

def center_position(entity_name, direc: Direction, top_left_pos):
    '''Factorio blueprint position are at the center of the entity,
    which has 1/2 grid resolution
    '''
    size = entity_size(entity_name, direc)
    return [top_left_pos[i] + size[i]/2 for i in range(2)]

def top_left_pos(kind, direction, center_pos):
    '''ConstructionSite position is at the top left of the entity'''
    size = entity_size(kind, direction)
    return [center_pos['x'] - size[0]/2,
            center_pos['y'] - size[1]/2]


def iter_area(size):
    '''Iterate over all possible offsets for a given entity size,
    relative to the upper left corner.

    :param size: Tuple (width, height) with two integer values
    :return: (offset x, offset y) tuples
    '''
    for y_ofs in range(size[1]):
        for x_ofs in range(size[0]):
            yield x_ofs, y_ofs

def iter_entity_area(entity_name, direc: Direction):
    '''Compute all possible offset for the named entity.
    No offset is negative, so only right-down

    Note: This is not how Factorio blueprint works with offset

    :param entity_name:  Kind of entity
    :param direction:    Rotation of entity
    '''
    size = entity_size(entity_name, direc)
    if size is None:
        raise NotImplementedError(f'Unknown size of entity {entity_name}')
    return iter_area(size)

def factorio_version_string_as_int(version_string='0.17.13.65519'):
    # 65519 = 0xffef = -17 in two's complement 16 bit
    '''return a 64 bit integer, corresponding to a version string.'''
    version_parts = [int(part) for part in version_string.split('.')]
    if len(version_parts) > 4:
        raise ValueError('Up to 4 parts accepted in version string')
    version_int = 0
    for part in version_parts:
        if part < 0 or part > 0xffff:
            raise ValueError('Each version string part must fit in 16 bit')
        version_int = version_int << 16 | part
    version_int <<= 16 * (4 - len(version_parts))
    return version_int

def factorio_version_int_as_string(version):
    '''return string, corresponding to a a 64 bit integer version integer from a blueprint'''
    version_hex = f'{version:016x}'
    version_parts = [int(version_hex[4*a:4*a+4], base=16) for a in range(4)]
    return '.'.join([str(p) for p in version_parts])

def empty_blueprint_dict():
    '''Return a dict that has all the mandatory objects in a blueprint'''
    # As defined at https://wiki.factorio.com/Blueprint_string_format
    return {'blueprint': {
        'icons': [
            dict(
                signal = dict(
                    type='item', name='assembling-machine-1'
                ),
                index=int(1)
            )
        ],
        'entities': [
            # dict(
            #   name=machine type
            #   position = dict(x:0, y:0)
            #   direction=int
            #   entity_number = int
            #   recipe= str
            # )
        ],
        'item': 'blueprint', # name (type) of this entity
        'version': factorio_version_string_as_int(),
        'label': 'Uninitialized Blueprint'
    }}

def site_as_blueprint_string(site, label='Unnamed ConstructionSite', icons=None, description=None):
    '''Given a ConstructionSite, return a valid blueprint string'''
    bp_dict = empty_blueprint_dict()
    blueprint = bp_dict['blueprint']
    blueprint['entities'] = site.get_entity_list()
    blueprint['label'] = label
    if icons is not None:
        blueprint['icons'] = icons
    if description is not None:
        blueprint['description'] = description
    return export_blueprint_dict(bp_dict)

def export_blueprint_dict(bp_dict):
    '''Encodes a blueprint as an exchange string

    :param blueprint:  a dict representing the blueprint, containing elements defined by
        https://wiki.factorio.com/Blueprint_string_format
    '''

    # This code is copied from factoriolib.dictToExchangeString
    import base64
    import json
    import zlib
    jsonString = json.dumps(bp_dict)
    jsonBytes = jsonString.encode("utf-8")
    compressedJson = zlib.compress(jsonBytes, 9)
    VERSION = "0"
    encodedString = VERSION + base64.b64encode(compressedJson).decode("utf-8")

    return encodedString

def import_blueprint_dict(exchangeString, auto_upgrade=True) -> dict:
    '''Decodes a blueprint exchange string
    :param exchangeString:  A blueprint exchange string
    :param auto_upgrade:  Determine if blueprints before factorio 2.0 should be upgraded
    :return:  a dict representing the blueprint
        https://wiki.factorio.com/Blueprint_string_format
    '''

    # This code is mostly copied from factoriolib.stringToJsonBytes
    import base64
    import json
    import zlib
    version_byte = exchangeString[0] # currently always zero
    if not version_byte == '0':
        raise ValueError('Exchange string version {VERSION} not supported')
    payload = exchangeString[1:]
    decodedString = base64.b64decode(payload)
    decompressedData = zlib.decompress(decodedString)
    jsonString = decompressedData.decode("utf-8")
    bp_dict = json.loads(jsonString)
    if auto_upgrade:
        upgrade_blueprint_version(bp_dict)
    return bp_dict

def upgrade_blueprint_version(bp_dict) -> dict:
    '''Upgrade blueprint version to the one supported.
    A blueprint < 2.0 has only 8 directions, where as >= 2.0 have 16 directions'''
    orig_version = bp_dict['blueprint']['version']
    target_version = factorio_version_string_as_int('2.0.0.65535')
    if orig_version < factorio_version_string_as_int('2.0'):
        log.warning(f'Upgrading blueprint from version 0x{orig_version:016x} to 0x{target_version:016x}')
        # 1.x has 8 directions, 2.x has 16 directions
        for entity in bp_dict['blueprint']['entities']:
            if 'direction' in entity:
                entity['direction'] *= 2
        bp_dict['blueprint']['version'] = target_version

def place_blueprint_on_site(site: ConstructionSite, bp_dict, offset=(0,0)):
    '''Add objects from blueprint dict to construction site at the specified offset

    :param site:  The ConstructionSite where the blueprint will be placed
    :param bp_dict:  The blueprint that will be placed on the site
    :param offset:  An (x,y) tuple that will be added to all blueprint
        coordinates to find the site coordinate.
    '''
    x, y = offset
    if not (
        (isinstance(x, int) or x.is_integer())
        and (isinstance(y, int) or y.is_integer())
    ):
        raise ValueError(f'Offset must be integer only. Was {offset}')

    blueprint = bp_dict['blueprint']
    for entity in blueprint['entities']:
        kwarg = {
            'kind': entity['name'],
            'pos': top_left_pos(
                entity['name'],
                entity.get('direction', 0),
                entity['position']
            ),
            'direction': 0, # Default - may be overwritten
            **entity
        }
        del kwarg['entity_number']
        del kwarg['name']
        del kwarg['position']
        log.debug(f'Add entity {kwarg}')
        site.add_entity(**kwarg)

#
#  Helper functions
#

def direction_to(s, t) -> Direction:
    '''Find direction from s to t'''
    # x,y increases right-down
    #  NW N NE
    #  W  +  E
    #  SW S SE
    if t[0] > s[0]:
        # east-like
        if t[1] < s[1]:
            return Direction.NORTHEAST
        elif t[1] == s[1]:
            return Direction.EAST
        else:
            return Direction.SOUTHEAST
    elif t[0] == s[0]:
        # north-south
        if t[1] > s[1]:
            return Direction.SOUTH
        else: # == or <
            return Direction.NORTH
    else: # t[0] < s[0]
        # west-like
        if t[1] < s[1]:
            return Direction.NORTHWEST
        elif t[1] == s[1]:
            return Direction.WEST
        else:
            return Direction.SOUTHWEST

#
#  Layout algorithms
#

def belt_path(site: ConstructionSite, point_list, belt_type='transport-belt'):
    '''Layout a path of transport belts

    :param site:  The ConstructionSite to place belts on
    :param point_list: The points that should be connected. There should be at least two points. Any following points are only allowed to modify one dimension.
    :param belt_type: The entity name of the belt to place.

    Note: The cell pointed to by the last point in point_list is not laid out, it is only used to set direction of the second-last belt cell. For example point_list = [(0,0), (10,0)] will place 10 belt cells, at (0,0) .. (9,0)
    '''
    for i in range(len(point_list) - 1):
        s, t = point_list[i][:], point_list[i + 1]
        if s[0] != t[0] and s[1] != t[1]:
            raise ValueError('Any pair of following points must only change one dimension. This is not true for {s}, {t}')
        if s[0] == t[0] and s[1] == t[1]:
            raise ValueError(f'Duplicate points are not allowed. This happens at index {i} and {i+1}')
        d = direction_to(s, t)
        sign = lambda a: -1 if a < 0 else 1 if a > 0 else 0
        step = [sign(t[i] - s[i]) for i in range(2)]
        while s != t:
            site.add_entity(belt_type, s, d)
            s[0] += step[0]
            s[1] += step[1]

def site_to_test(site: 'ConstructionSite', source, target) -> 'str':
    coordinates = []
    for y in range(site.dim_y):
        for x in range(site.dim_x):
            if site.is_reserved(x, y):
                coordinates.append((x,y))

    start = source.position
    end = target.position
    start_type = type(source)
    end_type = type(target)
    try:
        start_type = source.machine
    except:
        pass
    try:
        end_type = target.machine
    except:
        pass

    final_string = f"""
        print("{start_type} and {end_type}")
        width = {site.dim_x}
        height = {site.dim_y}
        site = layout.ConstructionSite(width, height)
        source = solver.FakeMachine(Vector{str(start)}, (3,3))
        target = solver.FakeMachine(Vector{str(end)}, (3,3))

        # Drawing flipped on its head
        coordinates = {str(coordinates)}
        for coordinat in coordinates:
            site.add_entity(INSERTER, coordinat, 0)

        log.debug(f"On site that looks like this:\\n {"{"}site{"}"} ")
        log.debug(f"Find path from {str(start)} to {str(end)}")
        spring_visuals = PathFindingVisuals(width, height, site, fps=60 )
        pos_list = solver.connect_machines(site, source, target, spring_visuals)
        log.debug(pos_list)
        """

    return final_string
