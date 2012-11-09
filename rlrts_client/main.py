import pygame
from pygame.locals import DOUBLEBUF, HWSURFACE, K_s, K_MINUS, K_EQUALS,\
                          K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT

import numpy.random as nprd


from rlrts_client import frame, control
from rlrts_client.world import World
from rlrts_client.values import black, white


flags = DOUBLEBUF | HWSURFACE  # | FULLSCREEN


def quit():
    global done
    done = True


def toggle_fullscreen():
    pygame.display.toggle_fullscreen()


def inc_zoom(f, i):
    def inner_func():
        if f.zoom + i > 0:
            f.zoom += i
    return inner_func


def move_camera(f, (dx, dy)):
    def inner_func():
        f.x += dx
        f.y += dy
    return inner_func


def get_steps():
    limit = 2001 / 2.5
    n = 100000

    mu = limit / 2
    sigma = limit / 4
    return zip(nprd.normal(mu, sigma, size=n), nprd.normal(mu, sigma, size=n))

old_steps = [0]
def set_steps(world):
    def inner_func():
        global old_steps
        print "Setting steps"
        steps = get_steps()
        world.set_steps(steps)
        print steps[0], old_steps[0]
        old_steps = steps
        print "Done"
    return inner_func


def main(dims):
    pygame.init()

    global done
    done = False
    screen = pygame.display.set_mode(dims, flags)
    FPS = 120.0

    clock = pygame.time.Clock()

    global f
    f = frame.Frame(screen)
    c = control.Control()

    c.register(K_ESCAPE, quit, control.ON_PRESS)
    c.register(K_EQUALS, inc_zoom(f, 0.01), control.WHILE_PRESSED)
    c.register(K_MINUS, inc_zoom(f, -0.01), control.WHILE_PRESSED)
    c.register(K_UP, move_camera(f, (0, -1)), control.WHILE_PRESSED)
    c.register(K_DOWN, move_camera(f, (0, 1)), control.WHILE_PRESSED)
    c.register(K_LEFT, move_camera(f, (-1, 0)), control.WHILE_PRESSED)
    c.register(K_RIGHT, move_camera(f, (1, 0)), control.WHILE_PRESSED)

    w = World((2000, 2000), (25, 25, 0))
    steps = get_steps()
    w.set_steps(steps)
    f.add_drawable(w)

    c.register(K_s, set_steps(w))

    f.zoom = 0.2
    f.x = dims[0] // 2
    f.y = dims[1] // 2
    while not done:
        clock.tick(FPS)

        c.handle_events()
        screen.fill(black)
        f.render()

if __name__ == "__main__":
    main((1280, 800))
