//File: viewer.cc
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#include "viewer.hh"
#include <string>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include "config.hh"
#include "lib/utils.hh"
using namespace std;
using namespace cv;

namespace {

const string winname = "viz";

// only works for 8UC3
cv::Mat hconcat(const cv::Mat& m1, const cv::Mat& m2) {
	int neww = m1.cols << 1;
	cv::Mat ret(m1.rows, neww, CV_8UC3);
  uchar* ptr = ret.data;
  int step = m1.cols * 3;
  for (int i = 0; i < m1.rows; ++i) {
    memcpy(ptr, m1.row(i).data, step * sizeof(uchar));
    ptr += step;
    memcpy(ptr, m2.row(i).data, step * sizeof(uchar));
    ptr += step;
  }
	return ret;
}

}

StereoCameraViewer::StereoCameraViewer(const Camera& cam):
  m_cam(cam) {
    m_assert(cam.num_cameras == 2);
    print_debug("(w,x0,x1)=(%lf,%lf,%lf)\n",CROP_W,CROP_X0,CROP_X1);
    print_debug("(h,y0,y1)=(%lf,%lf,%lf)\n",CROP_H,CROP_Y0,CROP_Y1);
}

void StereoCameraViewer::start() {
  m_worker_th = thread([&] {
      this->worker();
    });
}

void StereoCameraViewer::worker() {
  namedWindow(winname);
  namedWindow("");
  startWindowThread();
  m_timer.restart();
  double last_duration = m_timer.duration();
  while (not stopped) {
    auto im0 = m_cam.get_new(0);
    auto im1 = m_cam.get_new(1);
    resize(im0, im0, Size(VIEWER_W,VIEWER_H),0,0,cv::INTER_NEAREST);
    resize(im1, im1, Size(VIEWER_W,VIEWER_H),0,0,cv::INTER_NEAREST);
    // TODO set this in camera
    cv::rectangle(im0,
        Point(VIEWER_W*CROP_X0,VIEWER_H*CROP_Y0),
        Point(VIEWER_W*CROP_X1,VIEWER_H*CROP_Y1), Scalar(255,255,0));
    cv::rectangle(im1,
        Point(VIEWER_W*CROP_X0,VIEWER_H*CROP_Y0),
        Point(VIEWER_W*CROP_X1,VIEWER_H*CROP_Y1), Scalar(255,255,0));
    auto res = hconcat(im0, im1);

    double now = m_timer.duration();
    double fps = 1.0 / (now - last_duration);
    last_duration = now;
    putText(res, ssprintf("FPS:%.1lf", fps), Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 0.6,
        Scalar(255,255,255), 1);
    imshow(winname, res);
  }
  destroyWindow(winname);
}
