import pygame
from pygame import mouse
from pygame.locals import *

# Some local constants
ON_PRESS = 1
WHILE_PRESSED = 2
ON_MOUSE_DOWN = 3
WHILE_MOUSE_DOWN = 4
ON_RELEASE = 5


class Control(object):
    def __init__(self):
        self.callbacks = {}
        self.mouse = []

    def register(self, key, callback, method=ON_PRESS):
        if method in self.callbacks:
            if key in self.callbacks[method]:
                self.callbacks[method][key].append(callback)
            else:
                self.callbacks[method][key] = [callback]
        else:
            self.callbacks[method] = {key: [callback]}

    def register_mouse(self, condition, callback):
        self.mouse.append((condition, callback))

    def handle_events(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if ON_PRESS in self.callbacks and event.type == KEYDOWN:
                for key, callbacks in self.callbacks[ON_PRESS].iteritems():
                    if key == event.key:
                        [callback() for callback in callbacks]
            elif ON_RELEASE in self.callbacks and event.type == KEYUP:
                for key, callbacks in self.callbacks[ON_RELEASE].iteritems():
                    if key == event.key:
                        [callback() for callback in callbacks]
        if WHILE_PRESSED in self.callbacks:
            for key, callbacks in self.callbacks[WHILE_PRESSED].iteritems():
                if keys[key]:
                    [callback() for callback in callbacks]
        for (condition, callback) in self.mouse:
            if condition(mouse.get_pos(), mouse.get_pressed()):
                    callback(mouse.get_pos(), mouse.get_pressed())
