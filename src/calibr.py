#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: calibr.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import numpy as np
import cv2
import yaml
import tqdm
import sys, os, glob
from triangulate import Camera

def load_camera_from_calibr(f):
    s = open(f).read()

    y = list(yaml.load_all(s))[0]

    K0 = Camera.buildK(y['cam0']['intrinsics'])
    C0 = Camera(K0, np.eye(3), np.zeros((3,)))

    K1 = Camera.buildK(y['cam1']['intrinsics'])
    M = y['cam1']['T_cn_cnm1'][:3]
    R1 = np.asarray([k[:3] for k in M])
    t1 = np.asarray([k[3] for k in M])
    C1 = Camera(K1, R1, t1)

    dist0 = np.asarray(y['cam0']['distortion_coeffs'])
    dist1 = np.array(y['cam1']['distortion_coeffs'])
    return C0, C1, dist0, dist1

if __name__ == '__main__':
    C0, C1, d0, d1 = load_camera_from_calibr('../calibr-1211/camchain-homeyihuaDesktopCPM3D_kalibrfinal3.yaml')
    im = cv2.imread('calibrate-image-3/cam0/0012100000000000000.jpg')
    print im is None

    #for k in tqdm.trange(300):
    und = cv2.undistort(im, C0.K, d0)


    cv2.imwrite("orig.png", im)
    cv2.imwrite("und.png", und)


