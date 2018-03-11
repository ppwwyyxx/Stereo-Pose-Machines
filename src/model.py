#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# File: model.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import cv2
import tensorflow as tf
import sys
import numpy as np
import os, argparse

from tensorpack import *
from tensorpack.utils.argtools import memoized
from tensorpack.tfutils.summary import *
import matplotlib.pyplot as plt

__all__ = ['colorize', 'colorize_all', 'argmax_2d', 'argmean_2d']

_CM = plt.get_cmap('jet')
def colorize(img, heatmap):
    """ img: bgr, [0,255]
        heatmap: [0,1]
    """
    heatmap = _CM(heatmap)[:,:,[2,1,0]] * 255.0
    return img * 0.5 + heatmap * 0.5

def colorize_all(img, heatmaps):
    return [colorize(img, k) for k in heatmaps]

def argmax_2d(heatmap):
    _, _, _, top_left = cv2.minMaxLoc(heatmap)
    return top_left[::-1]

def argmean_2d(heatmap):
    xs, ys, ws = [], [], []
    for y in range(heatmap.shape[0]):
        for x in range(heatmap.shape[1]):
            if heatmap[y,x] > 0.5:
                xs.append(x)
                ys.append(y)
                ws.append(heatmap[y,x])
    xs, ys, ws = map(lambda k: np.asarray(k), [xs,ys,ws])
    s = np.sum(ws)
    if s < 1e-10:
        return (0, 0)
    x = np.dot(xs, ws) / s
    y = np.dot(ys, ws) / s
    return (y, x)

@memoized
def get_gaussian_map():
    sigma = 21
    gaussian_map = np.zeros((368, 368), dtype='float32')
    for x_p in range(368):
        for y_p in range(368):
            dist_sq = (x_p - 368/2) * (x_p - 368/2) + \
                      (y_p - 368/2) * (y_p - 368/2)
            exponent = dist_sq / 2.0 / (21**2)
            gaussian_map[y_p, x_p] = np.exp(-exponent)
    return gaussian_map.reshape((1,368,368,1))

class Model(ModelDesc):
    def _get_input_vars(self):
        return [InputVar(tf.float32, (None, 368, 368, 3), 'input') ]

    def _build_graph(self, inputs):
        image = inputs[0]
        image = image / 256.0 - 0.5
        gmap = tf.constant(get_gaussian_map())
        gmap = tf.tile(gmap, tf.pack([tf.shape(image)[0], 1, 1, 1]))
        gmap = tf.pad(gmap, [[0,0],[0,1],[0,1],[0,0]])
        pool_center = AvgPooling('mappool', gmap, 9, stride=8, padding='VALID')
        with argscope(Conv2D, kernel_shape=3, nl=tf.nn.relu):
            shared = (LinearWrap(image)
                .Conv2D('conv1_1', 64)
                .Conv2D('conv1_2', 64)
                .MaxPooling('pool1', 2)
                # 184
                .Conv2D('conv2_1', 128)
                .Conv2D('conv2_2', 128)
                .MaxPooling('pool2', 2)
                # 92
                .Conv2D('conv3_1', 256)
                .Conv2D('conv3_2', 256)
                .Conv2D('conv3_3', 256)
                .Conv2D('conv3_4', 256)
                .MaxPooling('pool3', 2)
                # 46
                .Conv2D('conv4_1', 512)
                .Conv2D('conv4_2', 512)
                .Conv2D('conv4_3_CPM', 256)
                .Conv2D('conv4_4_CPM', 256)
                .Conv2D('conv4_5_CPM', 256)
                .Conv2D('conv4_6_CPM', 256)
                .Conv2D('conv4_7_CPM', 128)())

        def add_stage(stage, l):
            l = tf.concat(3, [l, shared, pool_center], name='concat_stage{}'.format(stage))
            for i in range(1, 6):
                l = Conv2D('Mconv{}_stage{}'.format(i, stage), l, 128)
            l = Conv2D('Mconv6_stage{}'.format(stage), l, 128, kernel_shape=1)
            l = Conv2D('Mconv7_stage{}'.format(stage),
                    l, 15, kernel_shape=1, nl=tf.identity)
            return l

        with argscope(Conv2D, kernel_shape=7, nl=tf.nn.relu):
            out1 = (LinearWrap(shared)
                  .Conv2D('conv5_1_CPM', 512, kernel_shape=1)
                  .Conv2D('conv5_2_CPM', 15, kernel_shape=1, nl=tf.identity)())
            out2 = add_stage(2, out1)
            out3 = add_stage(3, out2)
            out4 = add_stage(4, out3)
            out5 = add_stage(5, out4)
            out6 = add_stage(6, out4)
            out6 = tf.slice(out6, [0,0,0,0], [-1,-1,-1,14])
            resized_map = tf.image.resize_bilinear(out6,
                    [640,640],
                    name='resized_map')

def run_test(path, input):
    param_dict = np.load(path, encoding='latin1').item()
    predict_func = OfflinePredictor(PredictConfig(
        model=Model(),
        session_init=DictRestore(param_dict),
        input_names=['input'],
        output_names=['Mconv7_stage6/output']
    ))

    import tqdm
    #for k in tqdm.range(20):
    #im = cv2.imread('cpmtest.jpg')
    im = cv2.imread(input)
    im = cv2.resize(im, (368,368))  # input bgr image
    out = predict_func([[im]])[0][0]
    coords = []
    for part in range(15): # sample 5 body parts: [head, right elbow, left wrist, right ankle, left knee]
        hm = out[:,:,part]
        hm_resized = cv2.resize(hm, (0,0), fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
        coords.append(argmax_2d(hm))
        viz = colorize(im, hm_resized)
        cv2.imwrite('part-{:02d}.png'.format(part), viz)
    ptsviz = np.zeros((368,368)).astype('float32') + 255.0
    coords = np.array(coords, dtype='float32') * 8
    for c in coords:
        cv2.circle(ptsviz, tuple(c[::-1]), 8, [0,0,255], -1)
        #ptsviz[c[0],c[1]] = 1.0
    ptsviz = ptsviz / 255.0
    cv2.imwrite('points.png', colorize(im, ptsviz))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', help='comma separated list of GPU(s) to use.')
    parser.add_argument('--input', help='input image', required=True)
    parser.add_argument('--load', required=True,
                        help='.npy model file generated by tensorpack.utils.loadcaffe')
    args = parser.parse_args()
    if args.gpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
    run_test(args.load, args.input)
