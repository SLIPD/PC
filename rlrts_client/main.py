import pygame
from pygame.locals import DOUBLEBUF, HWSURFACE, K_s, K_MINUS, K_EQUALS,\
                          K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT

import numpy.random as nprd


from rlrts_client import frame, control
from rlrts_client.world import World
from rlrts_client.gui import Slider
from rlrts_client.values import black


flags = DOUBLEBUF | HWSURFACE  # | FULLSCREEN


class Game(object):
    def quit(self):
        self.done = True

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()

    def inc_zoom(self, i):
        def inner_func(*args, **kwargs):
            if self.f.zoom + i > 0:
                self.f.zoom += i
        return inner_func

    def set_zoom(self, mini, maxi):
        def inner_func(z, *args, **kwargs):
            self.f.zoom = (z * (maxi - mini)) + mini
        return inner_func

    def move_camera(self, (dx, dy)):
        def inner_func(*args, **kwargs):
            self.f.x += dx
            self.f.y += dy
        return inner_func

    def get_steps(self):
        """ Generates random step data for testing """
        limit = 1000 / 2.5
        n = 10000

        mu = limit / 2
        sigma = limit / 4
        return zip(nprd.normal(mu, sigma, size=n),
                   nprd.normal(mu, sigma, size=n))

    def set_steps(self):
        """ Sets random step data for testing """
        steps = self.get_steps()
        self.w.set_steps(steps)

    def hit_edge(self, edge):
        """ Returns a function that returns true if the mouse is
            touching the given edge """
        (w, h) = self.dims

        def inner_func((x, y), pressed):
            if edge == "left":
                return x <= 0
            elif edge == "right":
                return x >= (w - 1)
            elif edge == "top":
                return y <= 0
            elif edge == "bottom":
                return y >= (h - 1)
        return inner_func

    def __init__(self, dims, team):
        # Initialise pygame and screen
        pygame.init()
        #pygame.event.set_grab(True)

        self.screen = pygame.display.set_mode(dims, flags)

        # Add some useful properties
        self.dims = dims
        self.done = False
        self.FPS = 120.0
        self.team = team

        self.clock = pygame.time.Clock()

        # Set up game elements
        self.w = World((1000, 1000), (25, 25, 0), team=team)
        self.f = frame.Frame(self.screen)
        self.c = control.Control()
        self.s = Slider((10, 10), 500)
        self.s.on_update(self.set_zoom(0.2, 4))

        # Register control events
        cam_speed = 2
        ## Keyboard events
        key_events = [
            # Meta functions (quit, menu)
            (K_ESCAPE, self.quit, control.ON_PRESS),

            # Zoom functions
            (K_EQUALS, self.inc_zoom(0.01), control.WHILE_PRESSED),
            (K_MINUS, self.inc_zoom(-0.01), control.WHILE_PRESSED),

            # Camera movement
            (K_UP, self.move_camera((0, -cam_speed)), control.WHILE_PRESSED),
            (K_DOWN, self.move_camera((0, cam_speed)), control.WHILE_PRESSED),
            (K_LEFT, self.move_camera((-cam_speed, 0)), control.WHILE_PRESSED),
            (K_RIGHT, self.move_camera((cam_speed, 0)), control.WHILE_PRESSED),

            # Debug
            (K_s, self.set_steps),
            ]

        for e in key_events:
            self.c.register(*e)

        ## Mouse events
        mouse_events = [
            (self.hit_edge("left"), self.move_camera((-cam_speed, 0))),
            (self.hit_edge("top"), self.move_camera((0, -cam_speed))),
            (self.hit_edge("right"), self.move_camera((cam_speed, 0))),
            (self.hit_edge("bottom"), self.move_camera((0, cam_speed))),

            # Slider control
            (self.s.have_mouse, self.s.update_pos),
            ]

        for e in mouse_events:
            self.c.register_mouse(*e)

        # Add drawable objects
        self.f.add_drawable(self.w)
        self.f.add_drawable(self.s)
        for territory in self.w.territories.values():
            self.f.add_drawable(territory)

        # Position the camera
        self.f.zoom = 1.0
        self.f.x = dims[0] // 2
        self.f.y = dims[1] // 2

        # Setup game state
        self.set_steps()

    def run_loop(self):
        while not self.done:
            self.clock.tick(self.FPS)

            self.c.handle_events()
            self.screen.fill(black)
            self.f.render()

    def __call__(self):
        self.run_loop()

if __name__ == "__main__":
    team = raw_input("Enter team name: ")
    if team == "":
        team = "Herp"
    g = Game((640, 400), team)
    g.run_loop()
