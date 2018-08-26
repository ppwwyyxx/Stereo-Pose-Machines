#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# File: triangulate.py


import numpy as np
import sys, os
import scipy.linalg as la

__all__ = ['Camera', 'triangulate', 'read_temple_camera']

class Camera(object):
    def __init__(self, K,R,t):
        self.K = K
        self.R = R
        self.t = t
        self.invR = self.R.T
        self.P = np.matmul(self.K,
                np.concatenate((self.R, self.t.reshape((3,1))), axis=1))
        self.invP3 = la.inv(self.P[:3,:3])
        self.center = np.matmul(-self.invP3, self.P[:3,3])

    @staticmethod
    def buildK(v):
        return np.asarray([[v[0],0,v[2]],
                [0,v[1],v[3]],
                [0,0,1]], dtype='float32')

def cam_center_vector(cam, m):
    vector = np.matmul(cam.invP3, m)
    return cam.center, vector

def triangulate(cam1, cam2, p1, p2):
    p1 = np.asarray([p1[0],p1[1],1])
    p2 = np.asarray([p2[0],p2[1],1])
    c1, v1 = cam_center_vector(cam1, p1)
    c2, v2 = cam_center_vector(cam2, p2)
    t = c2 - c1
    v3 = np.cross(v1, v2)
    X = np.stack((v1, v3, -v2), axis=1)

    alpha = np.matmul(la.inv(X), t)
    output = c1 + v1 * alpha[0] + alpha[1]*0.5*v3
    return output

def read_temple_camera():
    f = open('templeR_par.txt')
    lines = f.readlines()
    CAM = []
    def parse_21(data):
        K = np.asarray(data[:9]).reshape((3,3))
        R = np.asarray(data[9:18]).reshape((3,3))
        t = np.asarray(data[18:])
        return K,R,t
    for line in [lines[0], lines[2]]:
        line = line.strip().split()[1:]
        line = map(float, line)
        CAM.append(Camera(*parse_21(line)))
    return CAM

if __name__ == '__main__':

    CAM = read_temple_camera()
    pts = np.loadtxt('inlier.txt').astype('float32')
    pts3d = []
    print [c.R for c in CAM]
    for line in pts:
        print line
        out = triangulate(CAM[0], CAM[1], line[:2], line[2:])
        print out
        pts3d.append(out)
    pts3d = np.asarray(pts3d)


    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(pts3d[:,0],pts3d[:,1],pts3d[:,2])
    ax.set_aspect('equal')
    #plt.axes().set_aspect('equal')
    plt.show()



