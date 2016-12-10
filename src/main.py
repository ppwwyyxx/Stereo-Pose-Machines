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
from model import colorize, argmax_2d
from tensorpack.utils.serialize import dumps

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
    cnt = 0
    while True:
        cnt += 1
        m1 = camera.get_for_py(0)
        m1 = np.array(m1, copy=False)
        m2 = camera.get_for_py(1)
        m2 = np.array(m2, copy=False)

        o1, o2 = runner(m1, m2)

        # buf = dumps([m1, m2, o1, o2])
        # f = open('recording/{:03d}.npy'.format(cnt), 'w')
        # f.write(buf)
        # f.close()

        c1 = colorize(m1, o1[:,:,:-1].sum(axis=2))
        c2 = colorize(m1, o1[:,:,:-1].sum(axis=2))
        viz = np.concatenate((c1, c2), axis=1)
        cv2.imshow('color', viz / 255.0)

def dump_2dcoor():
    camera = libcpm.Camera()
    camera.setup()
    runner = get_parallel_runner('../data/cpm.npy')
    cv2.namedWindow('color')
    cv2.startWindowThread()
    cnt = 0
    while True:
        cnt += 1
        m1 = camera.get_for_py(0)
        m1 = np.array(m1, copy=False)
        m2 = camera.get_for_py(1)
        m2 = np.array(m2, copy=False)

        o1, o2 = runner(m1, m2)
        pts = []
        for k in range(14):
            pts.append((argmax_2d(o1[:,:,k]),
                argmax_2d(o2[:,:,k])))
        pts = np.asarray(pts)
        np.save('pts{}.npy'.format(cnt), pts)
        cv2.imwrite("frame{}.png".format(cnt), m1);
        if cnt == 10:
            break

def capture_pair():
    camera = libcpm.Camera()
    camera.setup()
    im1 = camera.get_new(0)
    im1 = np.array(im1, copy=False)
    im2 = camera.get_new(1)
    im2 = np.array(im2, copy=False)
    cv2.imwrite("1.png", im1)
    cv2.imwrite("2.png", im2)


if __name__ == '__main__':

    #test_viewer()
    stereo_cpm_viewer()
    #dump_2dcoor()
    #capture_pair()


