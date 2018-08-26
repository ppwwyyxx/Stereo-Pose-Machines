#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: patchmatch.py



import sys, os, cv2, glob
import numpy as np
import numpy.matlib
from collections import deque
import zmq

from model import argmax_2d
from background import BackgroundSegmentor
from tensorpack.utils.viz import *

PATCH_SIZE = 20
REGION_SIZE = 30
ORIG_SIZE = 640

def take_patch(im, y, x, size):
    #return im[y-size:y+size,x-size:x+size,:]
    canvas = np.zeros((size*2,size*2,3),im.dtype)

    ybegin = y - size
    yoffset = 0
    if ybegin < 0:
        yoffset = - ybegin
        ybegin = 0

    yend = y+size
    yoffset2 = size*2
    if yend > im.shape[0]:
        yoffset2 = size*2+(im.shape[0] - yend)
        yend = im.shape[0]

    xbegin = x - size
    xoffset = 0
    if xbegin < 0:
        xoffset = - xbegin
        xbegin = 0

    try:
        canvas[yoffset:yoffset2,xoffset:,:] = im[ybegin:yend,xbegin:x+size,:]
    except:
        import IPython;
        IPython.embed(config=IPython.terminal.ipapp.load_default_config())
    return canvas

BG0 = None
BG1 = None

class Matcher():
    def __init__(self, BG0, BG1):
        self.BG0 = BG0
        self.BG1 = BG1

    def match(self, im0, im1, hm0, hm1):
        viz = False
        mask0 = self.BG0.segment(im0)
        mask1 = self.BG1.segment(im1)

        im0 = im0 * (mask0>1e-10).astype('uint8')[:,:,np.newaxis]
        im1 = im1 * (mask1>1e-10).astype('uint8')[:,:,np.newaxis]

        if viz:
            viz0 = np.copy(im0)
            viz1 = np.copy(im1)
        pts14 = []
        for chan in range(14):
            h0 = cv2.resize(hm0[:,:,chan], (ORIG_SIZE, ORIG_SIZE))
            h1 = cv2.resize(hm1[:,:,chan], (ORIG_SIZE, ORIG_SIZE))
            y0, x0 = argmax_2d(h0)
            y1, x1 = argmax_2d(h1)

            target = take_patch(im0, y0, x0, PATCH_SIZE)
            region = take_patch(im1, y1, x1, REGION_SIZE)

            res = cv2.matchTemplate(region, target, cv2.TM_CCOEFF_NORMED)
            _, _, _, top_left = cv2.minMaxLoc(res)
            top_left = top_left[::-1]
            center_in_region = (top_left[0] + PATCH_SIZE, top_left[1] + PATCH_SIZE)
            center_in_im1 = (center_in_region[0] + y1-REGION_SIZE,
                    center_in_region[1] + x1-REGION_SIZE)

            if viz:
                cv2.circle(viz0, (x0,y0), 3, (0,0,255), -1)
                cv2.circle(viz1, tuple(center_in_im1[::-1]), 3, (0,0,255), -1)
            pts14.append([x0, y0, center_in_im1[1],center_in_im1[0]])
        if viz:
            mask0 = cv2.cvtColor(mask0, cv2.COLOR_GRAY2RGB).astype('uint8')
            mask1 = cv2.cvtColor(mask1, cv2.COLOR_GRAY2RGB).astype('uint8')
            viz = np.concatenate((mask0, viz0,viz1, mask1),axis=1)
            cv2.imshow("v", viz)
            cv2.waitKey(1)
        return np.array(pts14)
        return viz, np.array(pts14)

        #rv = np.copy(region)
        #rv[center_in_region[0],center_in_region[1]] = (0,0,255)
        #tv = cv2.resize(target, tuple(region.shape[:2][::-1]))

        #hv = np.zeros((region.shape), dtype='float32')
        #res = res - res.min()
        #res = res / res.max() * 255
        #res = cv2.cvtColor(res, cv2.COLOR_GRAY2RGB)
        #hv[PATCH_SIZE:PATCH_SIZE+res.shape[0],PATCH_SIZE:PATCH_SIZE+res.shape[1],:] = res
        #region = np.concatenate((region, rv, tv, hv), axis=1)
        #cv2.imwrite("patchmatch/region{}.png".format(chan), region)


if __name__ == '__main__':
    recording_dir = 'golden-test3'
    bgs = [cv2.imread('./{}/undistort/cam0/000{:02d}-0.jpg'.format(recording_dir, k))
            for k in range(1,21)]
    BG0 = BackgroundSegmentor(bgs)
    bgs = [cv2.imread('./{}/undistort/cam1/000{:02d}-1.jpg'.format(recording_dir, k))
            for k in range(1,21)]
    BG1 = BackgroundSegmentor(bgs)

    #pts = []
    q = deque(maxlen=10)

    for idx, k in enumerate(sorted(
        glob.glob('./{}/images/cam0/*.jpg'.format(recording_dir)))):
        if idx < 1400:
            continue
        num = os.path.basename(k).split('.')[0].split('-')[0]

        im0 = cv2.imread('./{}/undistort/cam0/{}-0.jpg'.format(recording_dir, num),
                cv2.IMREAD_COLOR)
        hm0 = np.load('./{}/cpm/cam0/{}-0.jpg.npy'.format(recording_dir, num))
        im1 = cv2.imread('./{}/undistort/cam1/{}-1.jpg'.format(recording_dir, num),
                cv2.IMREAD_COLOR)
        hm1 = np.load('./{}/cpm/cam1/{}-1.jpg.npy'.format(recording_dir, num))

        print num
        viz, pts14 = test_match(im0, im1, hm0, hm1)  #14x4
        cv2.imwrite("./{}/viz/{}.jpg".format(recording_dir, num), viz)
        q.append(pts14)
        pts2send = np.mean(list(q), axis=0)
        #pts.append(np.mean(list(q), axis=0))
    out = np.array(pts)
    out = out.transpose(1,2,0)
    print out.shape
    np.save('../data/pm-pts.npy', out)
