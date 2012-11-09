import pygame
from pygame.locals import DOUBLEBUF, HWSURFACE, K_s, K_MINUS, K_EQUALS,\
                          K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT

import numpy.random as nprd


from rlrts_client import frame, control
from rlrts_client.world import World
from rlrts_client.gui import Slider
from rlrts_client.values import black


flags = DOUBLEBUF | HWSURFACE  # | FULLSCREEN


def quit():
    global done
    done = True


def toggle_fullscreen():
    pygame.display.toggle_fullscreen()


def inc_zoom(f, i):
    def inner_func(*args, **kwargs):
        if f.zoom + i > 0:
            f.zoom += i
    return inner_func


def set_zoom(f, mini, maxi):
    def inner_func(z, *args, **kwargs):
        f.zoom = (z * (maxi - mini)) + mini
    return inner_func


def move_camera(f, (dx, dy)):
    def inner_func(*args, **kwargs):
        f.x += dx
        f.y += dy
    return inner_func


def get_steps():
    limit = 1000 / 2.5
    n = 10000

    mu = limit / 2
    sigma = limit / 4
    return zip(nprd.normal(mu, sigma, size=n), nprd.normal(mu, sigma, size=n))


def set_steps(world):
    def inner_func(*args, **kwargs):
        steps = get_steps()
        world.set_steps(steps)
    return inner_func


def hit_edge(edge, (w, h)):
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

    cam_speed = 2

    c.register_mouse(hit_edge("left", dims), move_camera(f, (-cam_speed, 0)))
    c.register_mouse(hit_edge("top", dims), move_camera(f, (0, -cam_speed)))
    c.register_mouse(hit_edge("right", dims), move_camera(f, (cam_speed, 0)))
    c.register_mouse(hit_edge("bottom", dims), move_camera(f, (0, cam_speed)))

    w = World((1000, 1000), (25, 25, 0))
    steps = get_steps()
    w.set_steps(steps)
    f.add_drawable(w)

    c.register(K_s, set_steps(w))

    s = Slider((10, 10), 500)
    s.on_update(set_zoom(f, 0.2, 4))
    f.add_drawable(s)
    c.register_mouse(s.have_mouse, s.update_pos)

    f.zoom = 0.8
    f.x = dims[0] // 2
    f.y = dims[1] // 2
    while not done:
        clock.tick(FPS)

        c.handle_events()
        screen.fill(black)
        f.render()

if __name__ == "__main__":
    main((1280, 800))
