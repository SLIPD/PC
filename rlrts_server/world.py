from rlrts_server import config
import numpy


class Unit(object):
    def __init__(self, team, (x, y)):
        self.team = team
        self.coords = (x, y)

    def move(self, (x, y)):
        self.coords = (x, y)


class Team(object):
    def __init__(self, connection, units):
        self.connection = connection
        self.units = units


class World(object):
    def __init__(self, teams, (width, height), (base_x, base_y)):
        self.teams = teams
        self.dimensions = (self.width, self.height) = (width, height)
        self.base_location = (self.base_x, self.base_y) = (base_x, base_y)

        self._init_mesh()

    def _init_mesh(self):
        n_rows = round(self.height / config.MESH_SQUARE_SIDE)
        n_cols = round(self.width / config.MESH_SQUARE_SIDE)

        self.mesh = numpy.zeros((n_rows, n_cols), dtype=numpy.float64)
