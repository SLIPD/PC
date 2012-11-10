from math import sqrt, floor
from collections import Counter

import pygame

from rlrts_client.funcs import scale, percent_colour
from rlrts_server import config
from rlrts_client.values import black, purple, yellow, white


territory_side = int(sqrt(config.N_TERRITORIES))

n_bins = 100


def around(num, n):
    return int(floor(float(num) / n) * n)


class Drawable(object):
    def __init__(self):
        self._zoom = 1.0
        self.dirty = True

    def set_zoom(self, z):
        self._zoom = z
        self.rezoom()

    def rezoom(self):
        self._out_surface = scale(self._surface, self._zoom)
        self.dirty = False

    @property
    def out_surface(self):
        if self.dirty:
            self.rezoom()
        return self._out_surface


class Unit(Drawable):
    def __init__(self, name, (x, y)):
        super(Unit, self).__init__()
        self.font = pygame.font.Font(pygame.font.match_font('ubuntu'), 20)

        self.name = name
        dims = (100, 50)
        radius = 5
        self.circle_loc = (radius, dims[1] - radius)

        self._surface = pygame.surface.Surface(dims)
        self._surface.set_colorkey(black)
        self.x, self.y = x, y
        t = self.font.render(name, True, white)
        self._surface.blit(t, (10, 20))
        pygame.draw.circle(self._surface, white, self.circle_loc, radius)

    def draw(self):
        dx, dy = self.circle_loc
        return (self.out_surface, self.x - dx, self.y - dy, 2)


class Territory(Drawable):
    def __init__(self, world, (i, j)):
        super(Territory, self).__init__()
        self.world = world
        self.w = (world.n_cols + 0.5) / float(territory_side)
        self.h = (world.n_rows + 0.5) / float(territory_side)
        self.i, self.j = i, j
        self.x, self.y = i * self.w, j * self.h

        self.team = None

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def team(self):
        return self._team

    @team.setter
    def team(self, team):
        self._team = team
        if team is None:
            self._surface = pygame.surface.Surface((self.w, self.h))
            self._surface.set_colorkey(black)
            self.dirty = True
            return
        color = white if team == self.world.team else yellow
        self._draw(color)

    def _draw(self, color):
        self._surface = pygame.surface.Surface((self.w, self.h))
        self._surface.set_alpha(51)

        pygame.draw.rect(self._surface,
                         color,
                         (0, 0, self.w, self.h)
                        )
        self.dirty = True

    def draw(self):
        return (self.out_surface, self.x, self.y, 1)


class World(Drawable):
    def __init__(self, (width, height), (bx, by, bz), team):
        super(World, self).__init__()

        self.team = team
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
        self.territories[index].team = team

    def set_steps(self, indices):
        self.steps = indices
        self.bins = Counter([(around(i, self.x_res), around(j, self.y_res))
                            for (i, j) in indices])

        self._surface.fill(black)
        w, h = self.x_res, self.y_res
        bs = self.bin_size / 4
        for (i, j), f in self.bins.iteritems():
            p = min(float(f) / bs, 1)
            pygame.draw.rect(self._surface,
                             percent_colour(purple, p),
                             (i, j, w, h)
                            )
        self.dirty = True

    def _init_mesh(self):
        self.steps = []

        self.territories = dict([((i, j), Territory(self, (i, j)))
                                for i in range(territory_side)
                                for j in range(territory_side)])

        self.bins = {}

    def draw(self):
        return (self.out_surface, 0, 0, 0)
