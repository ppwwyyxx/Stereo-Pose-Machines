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
import Queue
import yaml
from triangulate import Camera
from model import colorize



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



def searchRegion(target, region):
    # cv2.imshow("region", region)
 #       cv2.imshow("target", target)
    target = target - target.mean()
    region = region - region.mean()
    print target.shape
    print("****")
    print region.shape

    corr = signal.correlate2d(region, target, boundary='symm', mode='same')
    print corr.shape

    y, x = np.unravel_index(np.argmax(corr), corr.shape)  # find the match
    return y,x






PATCH_SIZE = 15
SEARCH_RANGE = 30

cnt = 0
trackingPatch = list()


pool_1 = np.zeros((368,368,15))
pool_2 = np.zeros((368,368,15))
q = Queue.Queue()
pool_cnt = 0


C0, C1, d0, d1 = load_camera_from_calibr('./camchain-homeyihuaDesktopCPM3D_kalibrfinal3.yaml')

d0 = d0.astype('float32')
d1 = d1.astype('float32')
print C1.K

print d0, d1



#cv2.stereoRectify(C0.K, C1.K, d0, d1 , (640,640), C1.R, C1.t,)
R0, R1, C0.P, C1.P, Q , _, _= cv2.stereoRectify(C0.K, d0, C1.K, d1 , (640,640), C1.R, C1.t, newImageSize=(640, 640))


map1_C0, map2_C0 = cv2.initUndistortRectifyMap(C0.K, d0, R0, C0.P, (640,640), cv2.CV_32F)
map1_C1, map2_C1 = cv2.initUndistortRectifyMap(C1.K, d1, R1, C1.P, (640,640), cv2.CV_32F)
output_cnt = 0

for c1,c2,i1,i2 in zip(sorted(glob.glob('/media/eric/b13d4a46-a007-4c3c-b23e-c198cf4899c0/home/mscv/Data/CPM3D_Data/golden-test3/cpm/cam0/*.npy')),
    sorted(glob.glob('/media/eric/b13d4a46-a007-4c3c-b23e-c198cf4899c0/home/mscv/Data/CPM3D_Data/golden-test3/cpm/cam1/*.npy')),
    sorted(glob.glob('/media/eric/b13d4a46-a007-4c3c-b23e-c198cf4899c0/home/mscv/Data/CPM3D_Data/golden-test3/images/cam0/*.jpg')),
    sorted(glob.glob('/media/eric/b13d4a46-a007-4c3c-b23e-c198cf4899c0/home/mscv/Data/CPM3D_Data/golden-test3/images/cam1/*.jpg'))):
    
    o1 = np.load(c1)
    o2 = np.load(c2)
    o1 = np.sum(o1[:,:,0:14],2).reshape(368,368,1)
    o2 = np.sum(o2[:,:,0:14],2).reshape(368,368,1)

    m1 = cv2.imread(i1)
    m1 = cv2.remap(m1,  map1_C0, map2_C0, cv2.INTER_CUBIC)
    o1 = cv2.remap(cv2.resize(o1, (640,640)),  map1_C0, map2_C0, cv2.INTER_CUBIC)


    m2 = cv2.imread(i2)
    m2 = cv2.remap(m2,  map1_C1, map2_C1, cv2.INTER_CUBIC)
    o2 = cv2.remap(cv2.resize(o2, (640,640)),  map1_C1, map2_C1, cv2.INTER_CUBIC)

    stereo = cv2.StereoSGBM(50, 256, 15)

    m1_gray = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY)
    m2_gray = cv2.cvtColor(m2, cv2.COLOR_BGR2GRAY)

    disparity = stereo.compute(m2_gray, m1_gray)#) , disptype=cv2.CV_32F)
    # print(disparity.max())
    norm_coeff = 1.0 / disparity.max()


    viz = np.concatenate( [colorize(m2, o2), colorize(m1,o1)], axis=1).astype('uint8')

    i = 10
    while i < 640:
    	cv2.line(viz, (0, i), (640*2, i), (255,0,0), thickness=1, lineType=8, shift=0)
    	i += 50

    cv2.imshow("hehe", viz)
    cv2.imwrite("depth/depth" + str(output_cnt) + '.png',  disparity * norm_coeff * 255)
    output_cnt += 1
    # cv2.waitKey(5)

    # m1 = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY)
    # m2 = cv2.cvtColor(m2, cv2.COLOR_BGR2GRAY)

#     pts2d = []

#     if pool_cnt < 30:
#         pool_1 += o1
#         pool_2 += o2
#         q.put((o1,o2))
#         pool_cnt = pool_cnt + 1
#         continue

#     m3 = np.zeros((368,368,3))


#     for k in range(14):
#         pool_1 += o1
#         pool_2 += o2
#         q.put((o1,o2))

#         p1 = argmean_2d(pool_1[:,:,k])
#         p2 = argmean_2d(pool_2[:,:,k])
#         print p1, p2

        
#         cv2.circle(m1, (int(p1[1]),int(p1[0])), 2, (0,255,255), -1)
#         cv2.circle(m2, (int(p2[1]),int(p2[0])), 2, (0,255,255), -1)

#         cv2.circle(m3, (int(p1[1]),int(p1[0])), 2, (0,255,0), -1)
#         cv2.circle(m3, (int(p2[1]),int(p2[0])), 2, (255,0,255), -1)
#         cv2.line(m3, (int(p1[1]),int(p1[0])), (int(p2[1]),int(p2[0])), (255,0,0), thickness=1, lineType=8, shift=0)

#         r0,r1 =  q.get()
#         pool_1 -= r0
#         pool_2 -= r1

#         if pool_cnt >= 118:
#             pts[k,0,pool_cnt-118] = (int(p1[0]))
#             pts[k,1,pool_cnt-118] = (int(p1[1]))
#             pts[k,2,pool_cnt-118] = (int(p2[0]))
#             pts[k,3,pool_cnt-118] = (int(p2[1]))

#     print(m1.shape)
#     # exit(0)
#     viz = np.concatenate((m1, m2), axis=1)
#     # viz = cv2.resize(viz, (368*3,368))
#     # cv2.imshow("hehe", viz)
#     # cv2.imwrite("./compare_max/merge_" + str(pool_cnt).zfill(3)+'.png', m3)
#     # cv2.waitKey(55)

#     pool_cnt = pool_cnt + 1

# print pts.shape
# np.save('mean-smooth.npy', pts)


    # pts2d = []
    # for k in range(14):
    #     p1 = argmax_2d(o1[:,:,k])
    #     p2 = argmax_2d(o2[:,:,k])
    #     print p1, p2

    #     # cv2.circle(m1, (int(p1[1]),int(p1[0])), 2, (0,255,255), -1)
    #     # cv2.circle(m2, (int(p2[1]),int(p2[0])), 2, (0,255,255), -1)

    #     # viz = np.concatenate((m1, m2), axis=1)
    #     # viz = cv2.resize(viz, (1800,900))
    #     # interactive_imshow(viz)
    #     target_1 = m1_[p1[0] - PATCH_SIZE : p1[0] + PATCH_SIZE, 
    #                            p1[1] - PATCH_SIZE : p1[1] + PATCH_SIZE]

    #     # viz = np.concatenate((search_range_1, search_range_2), axis=1)
    #     # viz = cv2.resize(viz, (SEARCH_RANGE*2,SEARCH_RANGE))
    #     # interactive_imshow(viz)

    #     # first frame:
    #     if cnt == 0:
    #         trackingPatch.append(target_1)
    
    # if cnt == 0:
    #     cnt = cnt + 1
    #     continue

    # for k in range(14):
    #     p1 = argmax_2d(o1[:,:,k])
    #     p2 = argmax_2d(o2[:,:,k])
        

    #     search_range_1 = m1_[p1[0] - SEARCH_RANGE : p1[0] + SEARCH_RANGE, 
    #                            p1[1] - SEARCH_RANGE : p1[1] + SEARCH_RANGE]

    #     search_range_2 = m2_[p2[0] - SEARCH_RANGE : p2[0] + SEARCH_RANGE, 
    #                            p2[1] - SEARCH_RANGE : p2[1] + SEARCH_RANGE]
        
    #     # y, x = searchRegion(trackingPatch[k], search_range_1)
        
    #     p1_y =  p1[0]  #+ y;
    #     p1_x =  p1[1]  #+ x;

    #     tmp = m1_[p1[0] - PATCH_SIZE : p1[0] + PATCH_SIZE, 
    #                            p1[1] - PATCH_SIZE : p1[1] + PATCH_SIZE]

    #     m1 = np.copy(m1_)
    #     m2 = np.copy(m2_)

    #     # y, x = searchRegion(tmp, search_range_2)
    #     cv2.imshow("target", tmp)
        
    #     result = cv2.matchTemplate(search_range_2,tmp,cv2.TM_CCOEFF_NORMED)
    #     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    #     top_left = max_loc

    #     w, h,_ = tmp.shape
    #     bottom_right = (top_left[0] + w, top_left[1] + h)
    #     cv2.rectangle(search_range_2,top_left, bottom_right, 255, 2)

    #     y = top_left[1] + h/2
    #     x = top_left[0] + w/2

    #     cv2.circle(search_range_2, (x,y), 1, (0,0,255), -1)
    #     cv2.imshow("search_range_2", search_range_2)



    #     p2_y =  p2[0]   + y - SEARCH_RANGE;
    #     p2_x =  p2[1]   + x - SEARCH_RANGE;

    #     print  p2
    #     print (p2_y, p2_x)
    #     print (y, x)
    

    #     cv2.circle(m1, (int(p1_x),int(p1_y)), 2, (255,255,255), -1)
    #     cv2.circle(m2, (int(p2_x),int(p2_y)), 2, (255,255,255), -1)
    #     # cv2.circle(m1, (int(p1[1]),int(p1[0])), 2, (0,0,255), -1)
    #     # cv2.circle(m2, (int(p2[1]),int(p2[0])), 2, (0,0,255), -1)

    #     viz = np.concatenate((m1, m2), axis=1)
    #     viz = cv2.resize(viz, (1800,900))
    #     interactive_imshow(viz)


    # cnt = cnt + 1
