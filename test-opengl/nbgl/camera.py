# -*- coding: utf-8 -*-
# $File: camera.py
# $Date: Tue Aug 28 10:17:34 2012 +0800
# $Author: jiakai <jia.kai66@gmail.com>

from vector import Vector
from math import sin, cos

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Camera(object):
    center = None
    up = None
    right = None
    forward = None

    def __init__(self, center, target, up):
        lst = [center, target, up]
        for i in range(len(lst)):
            if isinstance(lst[i], list):
                lst[i] = Vector(*lst[i])
        [center, target, up] = lst
        self.center = center
        self.forward = (target - center).normalize()
        self.right = self.forward.cross(up).normalize()
        self.up = self.right.cross(self.forward)

    def move_forawrd(self, delta):
        self.center += self.forward * delta

    def move_right(self, delta):
        self.center += self.right * delta

    def _do_rotate(self, x, y, agl):
        c = cos(agl)
        s = sin(agl)
        return (x * c + y * s, -x * s + y * c)

    def rotate_up(self, agl):
        """rotate along the up axel"""
        (self.forward, self.right) = self._do_rotate(
                self.forward, self.right, agl)

    def rotate_right(self, agl):
        """rotate along the right axel"""
        (self.forward, self.up) = self._do_rotate(
                self.forward, self.up, agl)

    def setGL(self):
        glLoadIdentity()
        gluLookAt(*(self.center.tolist() + (self.center +
            self.forward).tolist() + self.up.tolist()))
