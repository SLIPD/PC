from rlrts_server import config
from math import floor
import numpy


class Unit(object):
    def __init__(self, team, (x, y)):
        self.team = team
        self.coords = (x, y)
        self.world = None

    def move(self, (x, y)):
        self.coords = (x, y)

    def set_world(self, world):
        self.world = world

    def get_mesh_indices(self):
        return map(lambda n: round(n / config.MESH_SQUARE_SIDE), self.coords)

    def get_step_indices(self):
        return map(lambda n: floor(n / config.MESH_SQUARE_SIDE), self.coords)


class Team(object):
    def __init__(self, units):
        self.units = units

    def set_world(self, world):
        self.world = world
        [u.set_world(world) for u in self.units]


class World(object):
    def __init__(self, teams, (width, height), (base_x, base_y)):
        self.teams = teams
        self.dimensions = (self.width, self.height) = (width, height)
        self.base_location = (self.base_x, self.base_y) = (base_x, base_y)

        [t.set_world(self) for t in teams]

        self._init_mesh()

    def _init_mesh(self):
        n_rows = round(self.height / config.MESH_SQUARE_SIDE)
        n_cols = round(self.width / config.MESH_SQUARE_SIDE)

        self.mesh = numpy.zeros((n_rows, n_cols), dtype=numpy.float64)
