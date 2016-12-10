#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: process.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import cv2
import numpy as np
from scipy import signal
import glob, sys, os
from tensorpack.utils.serialize import loads
from tensorpack.utils.viz import interactive_imshow
from model import argmean_2d, argmax_2d






def searchRegion(target, region):
	# cv2.imshow("region", region)
 #   	cv2.imshow("target", target)
	target = target - target.mean()
	region = region - region.mean()
	print target.shape
	print("****")
	print region.shape

	corr = signal.correlate2d(region, target, boundary='symm', mode='same')
	print corr.shape

	y, x = np.unravel_index(np.argmax(corr), corr.shape)  # find the match
	return y,x







PATCH_SIZE = 40
SEARCH_RANGE = 40

cnt = 0
trackingPatch = list()

for f in sorted(glob.glob('../recording2/*.npy')):
    buf = open(f).read()
    m1, m2, o1, o2 = loads(buf)
    m1 = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY)
    m2 = cv2.cvtColor(m2, cv2.COLOR_BGR2GRAY)

    pts2d = []
    for k in range(14):
        p1 = argmax_2d(o1[:,:,k])
        p2 = argmax_2d(o2[:,:,k])
        print p1, p2

        # cv2.circle(m1, (int(p1[1]),int(p1[0])), 2, (0,255,255), -1)
        # cv2.circle(m2, (int(p2[1]),int(p2[0])), 2, (0,255,255), -1)

        # viz = np.concatenate((m1, m2), axis=1)
        # viz = cv2.resize(viz, (1800,900))
        # interactive_imshow(viz)
        target_1 = m1[p1[0] - PATCH_SIZE : p1[0] + PATCH_SIZE, 
        					   p1[1] - PATCH_SIZE : p1[1] + PATCH_SIZE]

        # viz = np.concatenate((search_range_1, search_range_2), axis=1)
        # viz = cv2.resize(viz, (SEARCH_RANGE*2,SEARCH_RANGE))
        # interactive_imshow(viz)

        # first frame:
        if cnt == 0:
        	trackingPatch.append(target_1)
    
    if cnt == 0:
    	cnt = cnt + 1
    	continue

    for k in range(14):
        p1 = argmax_2d(o1[:,:,k])
        p2 = argmax_2d(o2[:,:,k])
        

    	search_range_1 = m1[p1[0] - SEARCH_RANGE : p1[0] + SEARCH_RANGE, 
        					   p1[1] - SEARCH_RANGE : p1[1] + SEARCH_RANGE]

    	search_range_2 = m2[p2[0] - SEARCH_RANGE : p2[0] + SEARCH_RANGE, 
        					   p2[1] - SEARCH_RANGE : p2[1] + SEARCH_RANGE]
    	
    	y, x = searchRegion(trackingPatch[k], search_range_1)
    	
    	p1_y =  p1[0]  #+ y;
    	p1_x =  p1[1]  #+ x;

    	tmp = m1[p1[0] - PATCH_SIZE : p1[0] + PATCH_SIZE, 
        					   p1[1] - PATCH_SIZE : p1[1] + PATCH_SIZE]


    	y, x = searchRegion(tmp, search_range_2)
    	p2_y =  p2[0]  - SEARCH_RANGE + y;
    	p2_x =  p2[1]  - SEARCH_RANGE + x;

    	print  p2
    	print (p2_y, p2_x)
    	print (y, x)
    

    	cv2.circle(m1, (int(p1_x),int(p1_y)), 2, (255,255,255), -1)
        cv2.circle(m2, (int(p2_x),int(p2_y)), 2, (255,255,255), -1)
        # cv2.circle(m1, (int(p1[1]),int(p1[0])), 2, (0,0,255), -1)
        # cv2.circle(m2, (int(p2[1]),int(p2[0])), 2, (0,0,255), -1)

        viz = np.concatenate((m1, m2), axis=1)
        viz = cv2.resize(viz, (1800,900))
        interactive_imshow(viz)


    cnt = cnt + 1
