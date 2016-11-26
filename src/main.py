#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: main.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import numpy as np
import time
import cv2
import libcpm

#mattype = libcpm.Mat
camera = libcpm.Camera()
camera.setup()


for k in range(50):
    mat = camera.get(0)
    arr = np.array(mat, copy=False)
    cv2.imshow("mat", arr)
    cv2.waitKey(1)
    time.sleep(0.1)
