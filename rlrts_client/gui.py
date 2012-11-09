import pygame

from rlrts_client.world import Drawable
from rlrts_client.values import black


class Slider(Drawable):
    def __init__(self, (x, y), width):
        super(Slider, self).__init__()
        self.callback = None
        self.width = width

        self.pos = width // 2

        self.x, self.y = x, y

        self.color = (100, 100, 100)

        self.bg = pygame.surface.Surface((width + 1, 50))
        pygame.draw.line(self.bg, self.color, (0, 0), (0, 50))
        pygame.draw.line(self.bg, self.color, (width, 0), (width, 50))
        pygame.draw.line(self.bg, self.color, (0, 25), (width, 25))

        self._surface = pygame.surface.Surface((width + 1, 50))
        self._surface.set_colorkey(black)

        self.draw_slider()

    def on_update(self, callback):
        self.callback = callback

    def have_point(self, (x, y)):
        in_x = self.x <= x and x <= self.x + self.width
        in_y = self.y <= y and y <= self.y + 50

        return in_x and in_y

    def have_mouse(self, (x, y), (b1, b2, b3)):
        if not b1:
            return False
        else:
            return self.have_point((x, y))

    def update_pos(self, (x, y), bs=(False, False, False)):
        local_x = x - self.x

        if local_x < 0:
            local_x = 0
        elif local_x > self.width:
            local_x = self.width

        self.pos = local_x
        self.draw_slider()
        if self.callback is not None:
            self.callback(self.pos / float(self.width))

    def draw_slider(self):
        self._surface.blit(self.bg, (0, 0))
        pygame.draw.line(self._surface, self.color, (self.pos, 12), (self.pos, 37), 3)

    def set_zoom(self, z):
        pass

    def draw(self):
        return (self._surface, self.x, self.y, "gui")
