import pygame
from rlrts_client.funcs import scale


bg_scroll = 0.2


class Frame(object):
    def __init__(self, screen):
        self.objects = []
        self.screen = screen
        self.following = None
        self.x, self.y = 0, 0
        self.w, self.h = screen.get_size()
        self.background = None

        self._zoom = 1.0

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, z):
        self._zoom = z
        for obj in self.objects:
            obj.set_zoom(z)

        if self.background is not None:
            self.out_background = scale(self.background, z)

    def add_drawable(self, drawable):
        self.objects.append(drawable)

    def set_background(self, background):
        self.background = background
        self.out_background = scale(background, self._zoom)

    def blit(self, surface, (x, y), p=False):
        s = surface
        self.screen.blit(s, self.get_in_coords((x, y), p))

    def gui_blit(self, surface, (x, y)):
        self.screen.blit(surface, (x, y))

    def get_in_coords(self, (x, y), p=False):
        w = self.w / 2.0
        h = self.h / 2.0

        (x1, y1) = (x - w, y - h)
        (x2, y2) = (x1 * self.zoom, y1 * self.zoom)

        new = (int(x2 + w), int(y2 + h))

        if p:
            def p((a, b)):
                print "(%.1f + (%d), %.1f + (%d))" % (w, (a - w), h, (b - h))
            p((x, y))
            p(new)
            print "--------"

        return new

    def get_position(self):
        x = self.x - (self.w // 2)
        y = self.y - (self.h // 2)

        return (x, y)

    def render(self):
        if self.background is not None:
            self.blit(self.out_background, ((bg_scroll * -self.x) - 150, (bg_scroll * -self.y) - 100))
        layers = {}
        for obj in self.objects:
            (surface, x, y, z) = obj.draw()
            try:
                p = obj.p
            except AttributeError:
                p = False

            try:
                layers[z].append((surface, x, y, p))
            except KeyError:
                layers[z] = [(surface, x, y, p)]

        sx, sy = self.get_position()

        for key in sorted(layers.keys()):
            for (surface, x, y, p) in layers[key]:
                if key == "gui":
                    self.gui_blit(surface, (x, y))
                else:
                    self.blit(surface, (x - sx, y - sy), p)

        pygame.display.flip()
