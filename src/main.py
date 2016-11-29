#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: main.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import numpy as np
import time
import cv2
import sys
import libcpm
from model import get_runner, colorize

def test_viewer():
    # open cameras
    camera = libcpm.Camera()
    camera.setup()
    viewer = libcpm.StereoCameraViewer(camera)
    viewer.start()
    time.sleep(100)
    sys.exit()

if __name__ == '__main__':

    test_viewer()

    camera = libcpm.Camera()
    camera.setup()
    cv2.namedWindow('color')
    cv2.startWindowThread()
    _, predictor_batch = get_runner('../data/cpm.npy')
    while True:
        print time.time()
        m1 = camera.get_for_py(0)
        m1 = np.array(m1, copy=False)
        m2 = camera.get_for_py(1)
        m2 = np.array(m2, copy=False)
        out = predictor_batch([m1, m2])
        #print out.shape
        c1 = colorize(m1, out[0,:,:,1])
        #c1 = m1
        cv2.imshow('color', c1 / 255.0)

