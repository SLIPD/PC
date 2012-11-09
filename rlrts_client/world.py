from math import sqrt, floor
from collections import Counter

import pygame

from rlrts_client.funcs import scale, percent_colour
from rlrts_server import config
from rlrts_client.values import black, purple


territory_side = int(sqrt(config.N_TERRITORIES))

n_bins = 100


def around(num, n):
    return int(floor(float(num) / n) * n)


class Drawable(object):
    def set_zoom(self, z):
        self._zoom = z
        self._out_surface = scale(self._surface, z)

    @property
    def out_surface(self):
        try:
            return self._out_surface
        except AttributeError:
            return self._surface


class Territory(Drawable):
    def __init__(self, world, (i, j)):
        pass


class World(Drawable):
    def __init__(self, (width, height), (bx, by, bz)):
        self.dimensions = (self.width, self.height) = (width, height)
        self._wr = float(self.width) / territory_side
        self._hr = float(self.height) / territory_side
        self.base_location = (self.bx, self.by, self.bz) = (bx, by, bz)

        self.n_rows = round(self.height / config.MESH_SQUARE_SIDE)
        self.n_cols = round(self.width / config.MESH_SQUARE_SIDE)

        self.x_res = self.n_rows // n_bins
        self.y_res = self.n_cols // n_bins

        self.bin_size = self.x_res * self.y_res

        self._init_mesh()

        self._surface = pygame.surface.Surface((self.n_rows, self.n_cols))

    def set_territory(self, index, team):
        (i, j) = index
        territory_index = tuple(map(int, ((i // self._wr), (j // self._hr))))

        self.territories[territory_index].team = team

    def set_steps(self, indices):
        self.steps = indices
        self.bins = Counter([(around(i, self.x_res), around(j, self.y_res))
                            for (i, j) in indices])

        self._surface.fill(black)
        w, h = self.x_res, self.y_res
        bs = self.bin_size / 2
        for (i, j), f in self.bins.iteritems():
            p = min(float(f) / bs, 1)
            print p
            pygame.draw.rect(self._surface,
                             percent_colour(purple, p),
                             (i, j, w, h)
                            )

    def _init_mesh(self):
        self.steps = []

        self.territories = dict([((i, j), Territory(self, (i, j)))
                                for i in range(territory_side)
                                for j in range(territory_side)])

        self.bins = {}

    def draw(self):
        return (self.out_surface, 0, 0, 0)
