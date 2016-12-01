#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: cpmtriangulate.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import numpy as np
import glob
import cv2
import os
from triangulate import *

def coordinate_recover(p):
    y, x = p[0], p[1]
    y, x = x, y
    fac = 640.0 / 368.0
    y *= fac
    x *= fac
    x += 1600 * 0.3
    y += 1200 * 0.233333333
    return np.asarray([x, y])

def viz3d(pts3d):
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(pts3d[:,0],pts3d[:,1],pts3d[:,2])
    ax.set_aspect('equal')
    #plt.axes().set_aspect('equal')
    plt.show()

def cpmtriangulate(pts):
    pts = pts[:,::-1,:]
    c1 = Camera(Camera.buildK(
        #[564.5793378468188, 562.7507396707426, 807.514870534443, 638.3417715516073]),
        [517.2287393382929, 525.0704075144106, 774.5928420208769, 591.6267497011125]),
        np.eye(3),
        np.zeros((3,1)))

    P2 = np.array([
        #[0.9987049032311739, 0.005161677353747297, -0.05061495183159303, 0.0975936934184045],
    #[-0.004173863762698966, 0.9997991391796881, 0.01960255485522677, 0.00181642123998563],
    #[0.05070596733431972, -0.01936590773647232, 0.9985258466831194, 0.006270242291420671]
  [0.9997257921076083, -0.002649760120974218, -0.023266270996836397, 0.09259191413077857],
  [0.0027696869905852674, 0.9999830374718406, 0.005123826943546446, -0.0014153393536146166],
  [0.02325229942975788, -0.005186862237858692, 0.9997161732368524, -0.0005078842007711909]
    ])
    c2 = Camera(Camera.buildK(
            [521.1484829793496, 526.8842673949462, 789.4993718170895, 576.4476020205435]),
        P2[:,:3],
        P2[:,3])
    #c1, c2 = read_temple_camera()
    npts = pts.shape[0]

    pts_coord = [[], []]
    for p in pts:
        p1, p2 = p[0], p[1]
        p1, p2 = coordinate_recover(p1), coordinate_recover(p2)
        pts_coord[0].append(p1)
        pts_coord[1].append(p2)

    pts1 = np.asarray(pts_coord[0]).reshape((npts,1,2)).astype('float32')
    pts2 = np.asarray(pts_coord[1]).reshape((npts,1,2)).astype('float32')
    if True:    # do undistort:
        pts1 = cv2.undistortPoints(pts1, c1.K,
                np.array([-0.23108204 ,0.03321534, 0.00227184 ,0.00240575]))
        #pts1 = cv2.undistortPoints(pts1, c1.K,
                #np.array([0,0,0,0]))
        pts1 = pts1.reshape((npts,2))

        pts2 = cv2.undistortPoints(pts2, c2.K,
                np.array([-0.23146758 ,0.03342091 ,0.00133691 ,0.00034652]))
        #pts2 = cv2.undistortPoints(pts2, c2.K,
                #np.array([0,0,0,0]))
        pts2 = pts2.reshape((npts,2))

        c1 = Camera(np.eye(3),c1.R,c1.t)
        c2 = Camera(np.eye(3),c2.R,c2.t)
    else:
        pts1 = pts1[:,0,:]
        pts2 = pts2[:,0,:]

    pts3d = []
    for p1, p2 in zip(pts1, pts2):
        p3d = triangulate(c1, c2, p1, p2)
        pts3d.append(p3d)
    pts3d = np.array(pts3d)
    return pts3d

if __name__ == '__main__':
    #pts = np.loadtxt('inlier-12.txt').reshape(-1,2,2)
    #pts = np.load('pts3.npy')
    #pts = pts[:,::-1,:]
    #pts3d = cpmtriangulate(pts)
    #print pts3d
    #viz3d(pts3d)
    #sys.exit()

    ret = []
    for f in sorted(glob.glob('pts2/*.npy')):
        pts = np.load(f)
        print pts.shape
        pts3d = cpmtriangulate(pts)
        ret.append(pts3d)
    ret = np.array(ret)

    np.save('all.npy', ret)
