from rlrts_server import config
from math import floor, sqrt
import numpy
import operator


territory_side = int(sqrt(config.N_TERRITORIES))


class Unit(object):
    def __init__(self, device_id, name, (x, y), team=None):
        self.name = name
        self.team = team
        self.coords = (x, y)
        self.world = None

    def move(self, (x, y)):
        self.coords = (x, y)
        self.world.set_step_team(self.get_step_index(), self.team)

    def set_world(self, world):
        self.world = world
        self.move(self.coords)

    def get_mesh_indices(self):
        return map(lambda n: int(round(n / config.MESH_SQUARE_SIDE)), self.coords)

    def get_step_index(self):
        (i, j) = map(lambda n: int(floor(n / config.MESH_SQUARE_SIDE)), self.coords)
        return (i, j)

    def get_step_indices(self):
        return map(lambda n: floor(n / config.MESH_SQUARE_SIDE), self.coords)

    def __str__(self):
        return self.name


class Team(object):
    def __init__(self, name, units=None):
        self.units = units or []
        for unit in self.units:
            unit.team = self
        self.world = None
        self.name = name

    def add_unit(self, unit):
        self.units.append(unit)
        unit.team = self
        unit.set_world(self.world)

    def set_world(self, world):
        self.world = world
        for u in self.units:
            u.set_world(world)

    def get_steps(self):
        s = self.world.steps
        return [k for k in s if s[k] is self]

    def __str__(self):
        return self.name


class Territory(object):
    def __init__(self):
        self.teams = {}

    @property
    def owner(self):
        if len(self.teams) == 0:
            return None
        return max(self.teams.iteritems(), key=operator.itemgetter(1))[0]

    def switch(self, new_team, old_team):
        try:
            self.teams[new_team] += 1
        except KeyError:
            self.teams[new_team] = 1

        if old_team is not None:
            try:
                self.teams[old_team] -= 1
            except KeyError:
                # This shouldn't ever happen
                # because I have terrible encapsulation
                self.teams[old_team] = -1


class World(object):
    def __init__(self, (width, height), (bx, by, bz)):
        self.dimensions = (self.width, self.height) = (width, height)
        self._wr = float(self.width) / territory_side
        self._hr = float(self.height) / territory_side
        self.base_location = (self.bx, self.by, self.bz) = (bx, by, bz)

        self._init_mesh()

    def update_mesh(self, (i, j, z)):
        self.mesh[i][j] = z
        self.dirty.append((i, j))

    def get_mesh_serial(self):
        out = []
        for (i, j) in self.dirty:
            out.append((i, j, self.mesh[i][j]))
        self.dirty = []
        return out

    def set_step_team(self, index, team):
        # Hacky mess, this feels bad
        (i, j) = index
        territory_index = tuple(map(int, ((i // self._wr), (j // self._hr))))
        old_team = self.steps.get(index, None)
        self.territories[territory_index].switch(team, old_team)
        self.steps[index] = team

    def get_territories(self):
        out = []
        for (i, j), t in self.territories.iteritems():
            if t.owner is not None:
                out.append([[i, j], t.owner.name])
        return out

    def _init_mesh(self):
        n_rows = round(self.height / config.MESH_SQUARE_SIDE)
        n_cols = round(self.width / config.MESH_SQUARE_SIDE)

        self.dirty = []

        self.mesh = numpy.zeros((n_rows, n_cols), dtype=numpy.float64)
        self.steps = {}

        self.territories = dict(
                [((i, j), Territory()) for i in range(territory_side)
                                       for j in range(territory_side)])
