#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: main.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import numpy as np
import time
import cv2
import sys
import libcpm
from runner import get_runner, get_parallel_runner
from model import colorize

def test_cpp_viewer():
    # open cameras
    camera = libcpm.Camera()
    camera.setup()
    viewer = libcpm.StereoCameraViewer(camera)
    viewer.start()
    time.sleep(100)
    sys.exit()

def stereo_cpm_viewer():
    camera = libcpm.Camera()
    camera.setup()
    runner = get_parallel_runner('../data/cpm.npy')
    cv2.namedWindow('color')
    cv2.startWindowThread()
    while True:
        m1 = camera.get_for_py(0)
        m1 = np.array(m1, copy=False)
        m2 = camera.get_for_py(1)
        m2 = np.array(m2, copy=False)

        o1, o2 = runner(m1, m2)

        c1 = colorize(m1, o1[:,:,:-1].sum(axis=2))
        c2 = colorize(m1, o1[:,:,:-1].sum(axis=2))
        viz = np.concatenate((c1, c2), axis=1)
        cv2.imshow('color', viz / 255.0)

if __name__ == '__main__':

    #test_viewer()
    stereo_cpm_viewer()


