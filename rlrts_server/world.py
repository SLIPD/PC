from rlrts_server import config
from math import floor
import numpy


class Unit(object):
    def __init__(self, device_id, name, (x, y), team=None):
        self.name = name
        self.team = team
        self.coords = (x, y)
        self.world = None

    def move(self, (x, y)):
        self.coords = (x, y)
        self.world.steps[self.get_step_index] = self.team

    def set_world(self, world):
        self.world = world
        self.move(self.coords)

    def get_mesh_indices(self):
        return map(lambda n: round(n / config.MESH_SQUARE_SIDE), self.coords)

    def get_step_index(self):
        (i, j) = map(lambda n: floor(n / config.MESH_SQUARE_SIDE), self.coords)
        return "%d_%d" % (i, j)

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

    def __str__(self):
        return self.name


class World(object):
    def __init__(self, (width, height), (bx, by, bz)):
        self.dimensions = (self.width, self.height) = (width, height)
        self.base_location = (self.bx, self.by, self.bz) = (bx, by, bz)

        self._init_mesh()

    def _init_mesh(self):
        n_rows = round(self.height / config.MESH_SQUARE_SIDE)
        n_cols = round(self.width / config.MESH_SQUARE_SIDE)

        self.mesh = numpy.zeros((n_rows, n_cols), dtype=numpy.float64)
        self.steps = {}
