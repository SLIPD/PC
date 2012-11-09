from math import pi, fsum, hypot, cos, sin, atan2
import operator

from pygame import transform
from pygame.color import Color


def vector_add(a, b):
    return map(operator.add, a, b)


def vector_sub(a, b):
    return map(operator.sub, a, b)


def vector_mult(a, b):
    return tuple(map(operator.mul, a, b))


def vector_norm(vec):           # warning - works only for two dimensions!
    return hypot(*vec)


def vector_distance(a, b):
    return vector_norm(vector_sub(a, b))


def vector_angle(a, b):
    try:
        v = vector_sub(a, b)
        return atan2(v[1], v[0])
    except TypeError:
        return 0


def scale(surface, z):
    (w, h) = surface.get_size()
    return transform.scale(surface, (int(w * z), int(h * z)))


def dot_product(a, b):
    return fsum(vector_mult(a, b))


def rotate(point, angle):
    (x, y) = point
    sint = sin(angle)
    cost = cos(angle)
    return (cost * x - sint * y, sint * x + cost * y)


def rotate_about(vector, point, angle):
    return tuple(map(operator.add,
                     point,
                     rotate(map(operator.sub, vector, point), angle)))


def simple_angle(a):
    # TODO: Switch to using mod
    while a >= pi:
        a -= 2 * pi
    while a <= -pi:
        a += 2 * pi
    return a


def darken((R, G, B)):
    """ Make a colour a little darker """
    return (R / 4, G / 4, B / 4)


def percent_colour(c, p):
    (h, s, v, a) = c.hsva
    cc = Color("white")
    cc.hsva = (h, s, int(v * p), a)
    return cc
