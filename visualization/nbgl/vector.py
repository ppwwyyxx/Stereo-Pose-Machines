# -*- coding: utf-8 -*-
# $File: vector.py
# $Date: Tue Aug 28 10:16:59 2012 +0800
# $Author: jiakai <jia.kai66@gmail.com>

from math import sqrt

class Vector:
    x = None
    y = None
    z = None
    def __init__(self, x = 0, y = 0, z = 0):
        (self.x, self.y, self.z) = (x, y, z)
    def __add__(self, op):
        return Vector(self.x + op.x, self.y + op.y, self.z + op.z)
    def __sub__(self, op):
        return Vector(self.x - op.x, self.y - op.y, self.z - op.z)
    def __mul__(self, op):
        return Vector(self.x * op, self.y * op, self.z * op)
    def __div__(self, op):
        return Vector(self.x / op, self.y / op, self.z / op)
    def __str__(self):
        return '{' + ', '.join(str(i) for i in (self.x, self.y, self.z)) + '}'
    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)
    def cross(self, op):
        (x1, y1, z1) = (self.x, self.y, self.z)
        (x2, y2, z2) = (op.x, op.y, op.z)
        return Vector(y1 * z2 - y2 * z1, x2 * z1 - x1 * z2, x1 * y2 - x2 * y1)
    def dot(self, op):
        return self.x * op.x + self.y * op.y + self.z * op.z
    def mod(self):
        return sqrt(self.mod_sqr())
    def mod_sqr(self):
        [x, y, z] = [self.x, self.y, self.z]
        return x * x + y * y + z * z
    def normalize(self):
        self *= 1 / self.mod()
        return self
    def tolist(self):
        return [self.x, self.y, self.z]
