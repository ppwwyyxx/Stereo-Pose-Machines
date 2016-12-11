#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: background.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import sys
import numpy as np
import glob
import cv2
from tensorpack.utils.viz import interactive_imshow

class BackgroundSegmentor():
    def __init__(self, bgim):
        if not isinstance(bgim, list):
            bgim = [bgim]
        bgim = np.asarray(bgim)
        self.bgim = bgim.mean(axis=0).astype('float32')
        self.kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2,2))

    def segment(self, im):
        mask = np.square(im.astype('float32') - self.bgim
                ).sum(axis=2) / 20
        mask = np.clip(mask, 0, 255).astype('uint8')
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        return (mask > 40).astype('float32') *255
        return mask.astype('float32') * 255


if __name__ == '__main__':
    recording_dir = sys.argv[1]
    bgs = [cv2.imread('./{}/cam0/000{:02d}-0.jpg'.format(recording_dir, k))
            for k in range(1,21)]
    b = BackgroundSegmentor(bgs)

    for v in sorted(glob.glob('./{}/cam0/*.jpg'.format(recording_dir))):
        im = cv2.imread(v)
        seg = b.segment(im)
        seg = seg.astype('uint8')
        seg = cv2.cvtColor(seg, cv2.COLOR_GRAY2RGB)
        viz = np.concatenate((seg, im), axis=1)
        cv2.imshow(" ", viz)
        cv2.waitKey()

