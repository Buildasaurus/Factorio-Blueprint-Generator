'''
Functions related to placing machines on a grid.
'''

MACHINES_WITH_RECIPE = {
    'assembling-machine-1',
    'assembling-machine-2',
}

class ConstructionSite:
    '''Representation of the area to layout a factory'''

    def __init__(self, x_size, y_size):
        # self.reserved is a sparce array, containing only those cells that
        # have been reserved. This means it will work for very large
        # dimensions as long as they are not fully utilized.
        self.reserved = {}
        self.dim_x = x_size
        self.dim_y = y_size
        self.entities = []

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

    def add_entity(self, kind, pos, direction, recipe=None):
        '''Add an entity to the construction site
        :param kind:  Entity type name
        :param pos:  An (x,y) tuple pointing at the top left corner where the machine should be placed.
            Note: This is different from how Factorio blueprints works
        :param direction:  Entity direction
        :param recipe:  What recipe should the machine produce
        '''
        x, y = pos

        # Only allow recipe on machines we know can have one
        if recipe is not None and kind not in MACHINES_WITH_RECIPE:
            raise ValueError(f"I'm not aware that a {kind} can have a recipie")

        # Place machine
        for ofs in iter_entity_area(kind):
            self.reserve(pos[0] + ofs[0], pos[1] + ofs[1])

        # Remember machine information
        entity = dict(kind=kind, pos=pos, direction=direction)
        if recipe:
            entity['recipe'] = recipe
        self.entities.append(entity)

    def get_entity_list(self):
        '''Return all entities added in a form ready for Blueprint generation'''

        center_pos = {i: center_position(e['kind'], e['direction'], e['pos'])
                      for i, e in enumerate(self.entities)}
        return [
            dict(
                name=e['kind'],
                position=dict(x=center_pos[i][0], y=center_pos[i][1]),
                direction=e['direction'],
                entity_number=i+1
            )
            for i, e in enumerate(self.entities)
        ]

ENTITY_SIZE = {
    'transport-belt': (1,1),
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
}

def factoriocalc_entity_size(machine_name):
    import factoriocalc
    machine_class = factoriocalc.mchByName.get(machine_name)
    if machine_class is None:
        return None
    machine_instance = machine_class()
    return machine_instance.width, machine_instance.height

def entity_size(entity_name):
    size = factoriocalc_entity_size(entity_name)
    return ENTITY_SIZE.get(entity_name) if size is None else size

def center_position(entity_name, direc: Direction, top_left_pos):
    '''Factorio blueprint position are at the center of the entity, which has 1/2 grid resolution'''
    size = entity_size(entity_name)
    if direc in [2, 6]:
        # Switch x and y size
        y, x = size
        size = [x,y]
    return [top_left_pos[i] + size[i]/2 for i in range(2)]

def iter_entity_area(entity_name):
    '''Compute all possible offset for the named entity.
    For an inserter, the list is 1 long.
    For a gun-turrent 4 long.
    For an assembly-machine-1, 9 long.

    No offset are negative, so only right-down

    Note: This is not how Factorio blueprint works with offset
    '''
    size = entity_size(entity_name)
    if size is None:
        raise NotImplementedError(f'Unknown size of entity {entity_name}')
    for y_ofs in range(size[1]):
        for x_ofs in range(size[0]):
            yield x_ofs, y_ofs

def factorio_version_string_as_int():
    '''return a 64 bit integer, corresponding to a version string'''
    factorio_major_version = 0
    factorio_minor_version = 17
    factorio_patch_version = 13
    factorio_dev_version = 0xffef
    return (factorio_major_version << 48
            | factorio_minor_version << 32
            | factorio_patch_version << 16
            | factorio_dev_version)

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
