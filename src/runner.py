#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: runner.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import threading
import cv2
import tensorflow as tf
import sys
import numpy as np
import os, argparse
import multiprocessing as mp
from tqdm import tqdm

from tensorpack import *
from tensorpack.utils.gpu import change_gpu

from model import Model

def get_runner(path):
    param_dict = np.load(path, encoding='latin1').item()
    predict_func = OfflinePredictor(PredictConfig(
        model=Model(),
        session_init=ParamRestore(param_dict),
        session_config=get_default_sess_config(0.99),
        input_names=['input'],
        #output_names=['Mconv7_stage6/output']
        output_names=['resized_map']
    ))
    def func_single(img):
        # img is bgr, [0,255]
        # return the output in WxHx15
        return predict_func([[img]])[0][0]
    def func_batch(imgs):
        # img is bgr, [0,255], nhwc
        # return the output in nhwc
        return predict_func([imgs])[0]
    return func_single, func_batch

def get_parallel_runner_1(path):
    param_dict = np.load(path, encoding='latin1').item()
    cfg = PredictConfig(
        model=Model(),
        session_init=ParamRestore(param_dict),
        session_config=get_default_sess_config(0.99),
        input_names=['input'],
        output_names=['resized_map']
    )
    inque = mp.Queue()
    outque = mp.Queue()
    with change_gpu(0):
        proc = MultiProcessQueuePredictWorker(1, inque, outque, cfg)
        proc.start()
    with change_gpu(1):
        pred1 = OfflinePredictor(cfg)
    def func1(img):
        inque.put((0,[[img]]))
    func1.outque = outque
    def func2(img):
        return pred1([[img]])[0][0]
    return func1, func2

def get_parallel_runner(path):
    param_dict = np.load(path, encoding='latin1').item()
    cfg = PredictConfig(
        model=Model(),
        session_init=ParamRestore(param_dict),
        session_config=get_default_sess_config(0.99),
        input_names=['input'],
        output_names=['resized_map']
    )
    predictor = DataParallelOfflinePredictor(cfg, [0,1])

    def func(im1, im2):
        o = predictor([[im1], [im2]])
        return o[0][0], o[1][0]
    return func

def benchmark_single(path):
    im = cv2.imread('cpmtest.jpg')
    im1 = cv2.resize(im, (368,368))
    im2 = np.copy(im1)
    _, fbatch = get_runner(path)
    for k in tqdm(range(300)):
        out = fbatch([im,im])
    sys.exit()

def benchmark_parallel1(path):
    im = cv2.imread('cpmtest.jpg')
    im1 = cv2.resize(im, (368,368))
    im2 = np.copy(im1)
    f1, f2 = get_parallel_runner_1(path)
    que = f1.outque
    for k in tqdm(range(300)):
        f1(im1)
        out2 = f2(im2)
        out1 = que.get()[1][0][0]
    sys.exit()

def benchmark_parallel2(path):
    im = cv2.imread('cpmtest.jpg')
    im1 = cv2.resize(im, (368,368))
    im2 = np.copy(im1)
    f = get_parallel_runner(path)
    for k in tqdm(range(300)):
        o1, o2 = f(im1, im2)
    sys.exit()

if __name__ == '__main__':
    benchmark_parallel2()
