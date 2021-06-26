#!/usr/bin/env python3

from math import (
    acos,
    cos,
    sin,
)

# Basically lifted from
#   http://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion; thanks
#   :-)
#   Edited to be a bit faster and clearer


def qq_mult(q1, q2):
    return [
        q1[0]*q2[0] - q1[1]*q2[1] - q1[2]*q2[2] - q1[3]*q2[3],
        q1[0]*q2[1] + q1[1]*q2[0] + q1[2]*q2[3] - q1[3]*q2[2],
        q1[0]*q2[2] - q1[1]*q2[3] + q1[2]*q2[0] + q1[3]*q2[1],
        q1[0]*q2[3] + q1[1]*q2[2] - q1[2]*q2[1] + q1[3]*q2[0]
    ]


def q_conjugate(q):
    q = normalized(q)
    w, x, y, z = q
    return [w, -x, -y, -z]


def qv_mult(q1, v1):
    v1 = normalized(v1)
    q2 = [0.0] + v1
    return qq_mult(qq_mult(q1, q2), q_conjugate(q1))[1:]


def axisangle_to_q(v, theta):
    v = normalized(v)
    x, y, z = v
    theta *= 0.5
    w = cos(theta)
    x = x * sin(theta)
    y = y * sin(theta)
    z = z * sin(theta)
    return [w, x, y, z]


def q_to_axisangle(q):
    w, v = q[0], q[1:]
    theta = acos(w) * 2.0
    return normalized(v), theta


def normalized(v):
    len = (sum(x*x for x in v)) ** 0.5
    return [x / len for x in v]


def cross(v0, v1):
    return [
        v0[1] * v1[2] - v0[2] * v1[1],
        v0[2] * v1[0] - v0[0] * v1[2],
        v0[0] * v1[1] - v0[1] * v1[0]
    ]


def dot(v0, v1):
    return sum([x * y for x, y in zip(v0, v1)])
