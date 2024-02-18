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

    def add_machine(self, kind, pos, direction, recipe=None):
        '''Add a machine to the construction site
        :param kind:  Machine name
        :param pos:  An (x,y) tuple where the machine shold be added
        :param direction:  Machine direction
        :param recipe:  What recipe should the machine produce
        '''
        x, y = pos

        # Only allow recipe on machines we know can have one
        if recipe is not None and kind not in MACHINES_WITH_RECIPE:
            raise ValueError(f"I'm not aware that a {kind} can have a recipie")

        # Place machine. This will raise an error if there is no room
        # FIXME assume machine is 3x3
        for y_ofs in [-1, 0, 1]:
            for x_ofs in [-1, 0, 1]:
                self.reserve(x + x_ofs, y + y_ofs)

        # Remember machine information
        entity = dict(kind=kind, pos=pos, direction=direction)
        if recipe:
            entity['recipe'] = recipe
        self.entities.append(entity)

    def get_entity_list(self):
        '''Return all entities added in a form ready for Blueprint generation'''
        return [
            dict(
                name=e.kind,
                position=dict(x=e.pos[0], y=e.pos[1]),
                direction=e.direction,
                entity_number=i+1
            )
            for i, e in enumerate(self.entities)
        ]

