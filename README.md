# Stereo Pose Machines

![demo](./demo/poster.jpg)

[Video Demo](tbd)

## Dependencies:
+ A Pair of Pylon Cameras
+ Eigen3
+ OpenCV
+ [tensorpack](https://github.com/ppwwyyxx/tensorpack)
+ PyYaml
+ PyOpenGL

## Compile:
```
cd src/cpp && make
```

## Test Cameras:
```
cd src/cpp && ./main.bin
```
Stereo cameras may be detected in any order. To make things consistent, `src/cpp/pylon_camera.cc`
assumes that the camera whose name contains "711" is the first camera. You'll need to change it
for your case.

## Calibrate Cameras:
Use `main.bin` to take images and Kalibr to produce a yaml with the same format in `calibr-1211`.
Change the path in `main.py` to your own calibration results. Also change the undistortion
coefficients in `cpp/camera.hh`.

## Test CPM is working:
Download model to `data/cpm.npy`.
```
cd src/cpp && python2 main.py -t 'cpm-viewer'
```
It will use 2 GPU to run 2 CPMs in parallel.

## Test Visualization is working:
```
cd visualization && python2 main.py ../data/final-demo.npy
```
Its OpenGL bindings doesn't work on some systems (e.g. Ubuntu). Don't know why.

## Run Stereo CPM:
```
cd src/cpp && python2 main.py -t 'cpm3d'
```
This will send 3d point coordinates to `0.0.0.0:8888`. You can use `-h <ip address>` to change the IP.

To start a server (maybe on some other computers) to receive points and visualize:
```
cd visualization && python main-server.py
```
