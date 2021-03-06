from rlrts_server import server
import pygame
import numpy
from pygame.locals import *
from math import sqrt

# Some colours
white = (255, 255, 255)
red = (239, 39, 19)
green = (88, 240, 0)
blue = (0, 88, 240)
yellow = (255, 255, 0)
black = (0, 0, 0)
purple = (116, 4, 181)

scale_factor = 12
step = 2.5 * scale_factor
unit_radius = 20


def darken((R, G, B)):
    """ Make a colour a little darker """
    return (R / 4, G / 4, B / 4)


def to_local_coords((x, y)):
    return (x * scale_factor, y * scale_factor)


def from_local_coords((x, y)):
    return (x / scale_factor, y / scale_factor)


class Renderer(object):
    def __init__(self, s=None):
        pygame.init()
        self.moving = None

        self.s = s or server.Server(self)

    def ready(self):
        self.dims = (self.w, self.h)\
                  = map(lambda d: d * scale_factor, self.s.world.dimensions)

        self.screen = pygame.display.set_mode(map(lambda n: n + 1, self.dims))
        self._do_draw()

    def draw_mesh(self):
        # Rows
        for n in numpy.arange(0, self.h + step + 1, step):
            pygame.draw.line(self.screen, purple, (n, 0), (n, self.h), 1)
        # Columns
        for n in numpy.arange(0, self.w + step + 1, step):
            pygame.draw.line(self.screen, purple, (0, n), (self.w, n), 1)

    def draw_steps(self):
        for (i, j), team in self.s.world.steps.items():
            colour = darken(blue if team.name == "Herp" else yellow)
            left = i * step
            top = j * step
            pygame.draw.rect(self.screen, colour, (left, top, step, step))

    def unit_iter(self):
        for team in self.s.teams.itervalues():
            for unit in team.units:
                yield unit

    def intersect_unit_mouse(self, unit):
        def vecDist((x1, y1), (x2, y2)):
            return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        mp = pygame.mouse.get_pos()
        up = to_local_coords(unit.coords)
        return vecDist(mp, up) < unit_radius

    def draw_units(self):
        for unit in self.unit_iter():
            pos = map(lambda d: d * scale_factor, unit.coords)
            colour = blue if unit.team.name == "Herp" else yellow
            pygame.draw.circle(self.screen, colour, pos, unit_radius, unit_radius / 2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                for unit in self.unit_iter():
                    if self.intersect_unit_mouse(unit):
                        self.moving = unit
            elif event.type == MOUSEBUTTONUP:
                self.moving = None
            elif event.type == MOUSEMOTION:
                if self.moving:
                    self.moving.move(from_local_coords(pygame.mouse.get_pos()))

    def step(self):
        self._do_draw()
        self.handle_events()

    def main_loop(self):
        done = False
        while not done:
            self._do_draw()
            self.handle_events()

    def _do_draw(self):
        self.screen.fill(black)
        self.draw_steps()
        self.draw_mesh()
        self.draw_units()
        pygame.display.flip()

if __name__ == "__main__":
    r = Renderer()
    r.s.ioloop.start()
