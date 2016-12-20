#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: main.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import numpy as np
import time
import cv2
import zmq
import sys
from collections import deque

import libcpm
from runner import get_runner, get_parallel_runner
from model import colorize, argmax_2d
from tensorpack.utils.serialize import dumps
from triangulate import triangulate
from calibr import load_camera_from_calibr
from background import BackgroundSegmentor
from patchmatch import Matcher

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

	m1s = cv2.resize(m1, (368,368))
	m2s = cv2.resize(m2, (368,368))

        o1, o2 = runner(m1s, m2s)

        #buf = dumps([m1, m2, o1, o2])
        #f = open('recording/{:03d}.npy'.format(cnt), 'w')
        #f.write(buf)
        #f.close()

        c1 = colorize(m1, o1[:,:,:-1].sum(axis=2))
        c2 = colorize(m2, o2[:,:,:-1].sum(axis=2))
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


def final():
    camera = libcpm.Camera()
    camera.setup()

    pmatcher = libcpm.PatchMatch()
    pmatcher.init(camera, 20)

    runner = get_parallel_runner('../data/cpm.npy')

    # python matcher:
    #bgs0, bgs1 = [], []
    #for k in range(20):
        #m1 = camera.get_for_py(0)
        #m1 = np.array(m1, copy=True)
        #m2 = camera.get_for_py(1)
        #m2 = np.array(m2, copy=True)
        #bgs0.append(m1)
        #bgs1.append(m2)
    #matcher = Matcher(BackgroundSegmentor(bgs0), BackgroundSegmentor(bgs1))

    viewer = libcpm.StereoCameraViewer(camera)
    viewer.start()

    C1, C0, d1, d0 = load_camera_from_calibr('../calibr-1211/camchain-homeyihuaDesktopCPM3D_kalibrfinal3.yaml')
    queue = deque(maxlen=2)

    ctx = zmq.Context()
    #sok = ctx.socket(zmq.PUSH)
    #sok.connect('tcp://172.22.45.86:8888')

    def cpp_matcher(m1, m2, o1, o2):
        o1 = libcpm.Mat(o1)
        o2 = libcpm.Mat(o2)
        out = pmatcher.match_with_hm(m1, m2, o1, o2)
        return np.asarray(out).reshape(14, 4) #14 x 2image x (x,y)

    pts3ds = []
    cnt = 0
    while True:
        cnt += 1
        print 'begin---', time.time()
        m1 = camera.get_for_py(0)
        m1r = np.array(m1, copy=False)
        m2 = camera.get_for_py(1)
        m2r = np.array(m2, copy=False)

        m1s = cv2.resize(m1r, (368,368))
        m2s = cv2.resize(m2r, (368,368))
        print 'after resize---', time.time()

        o1, o2 = runner(m1s, m2s)
        print 'after cpm---', time.time()

        #pts14x4 = matcher.match(m1r, m2r, o1, o2)
        pts14x4 = cpp_matcher(m1, m2, o1, o2)

        #to_save = (m1s, m2s, o1, o2, pts14x4)
        #fout = open('full-recording/{:04d}.dat'.format(cnt), 'wb')
        #fout.write(dumps(to_save))
        #fout.close()

        print 'after match---', time.time()
        queue.append(pts14x4)
        p2d = np.mean(queue, axis=0)
        p3ds = np.zeros((14,3))
        for c in range(14):
            p3d = triangulate(C0, C1, p2d[c,:2], p2d[c,2:])
            p3ds[c,:] = p3d
        #sok.send(dumps(p3ds))
	print p3ds
        print 'after send---', time.time()
        print '-------'

        #c1 = colorize(m1r, o1[:,:,:-1].sum(axis=2))
        #c2 = colorize(m2r, o2[:,:,:-1].sum(axis=2))
        #viz = np.concatenate((c1, c2), axis=1)
        #cv2.imshow('color', viz / 255.0)

if __name__ == '__main__':
    final()

    #test_viewer()
    #stereo_cpm_viewer()
    #dump_2dcoor()
    #capture_pair()


