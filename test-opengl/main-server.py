#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: main-server.py

import time
from nbgl import GLDrawer
import numpy as np
import threading
import sys
from time import sleep, time
import zmq

from tensorpack.utils.serialize import loads
from main import Sphere, build_cylinder_from_3dpts, Frame, run_app

if __name__ == '__main__':
    B = 600.0
    drawer = GLDrawer('winname', [(-B,B)]*3)
    drawer.start()

    cnt = 0

    ctx = zmq.Context()
    sok = ctx.socket(zmq.PULL)
    sok.bind('tcp://0.0.0.0:8888')
    def get_frame():
        global cnt
        cnt += 1
        data = loads(sok.recv(copy=False).bytes)
        data = data * 100
        print data
        spheres = [Sphere(3, pos) for pos in data]
        spheres[0].radius = 10
        cyls = build_cylinder_from_3dpts(data)
        f = Frame(spheres, cyls)
        return f

    run_app(drawer.draw_callback, get_frame)
    sleep(100)
