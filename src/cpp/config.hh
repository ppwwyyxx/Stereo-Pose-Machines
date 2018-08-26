//File: config.hh


#pragma once

#define ORIG_W 1600
#define ORIG_H 1200
// 0.5 * W
#define SIZE 0.4

#define CROP_W SIZE
#define CROP_X0 ((1 - CROP_W) * 0.5)
#define CROP_X1 (((1 - CROP_W) * 0.5) + CROP_W)

#define CROP_H (SIZE / 0.75)
#define CROP_Y0 ((1 - CROP_H) * 0.5)
#define CROP_Y1 (((1 - CROP_H) * 0.5) + CROP_H)

#define VIEWER_W 800
#define VIEWER_H (VIEWER_W * 0.75)
