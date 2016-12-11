//File: main.cpp
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#include <opencv2/highgui/highgui.hpp>
#include <chrono>

#include "lib/timer.hh"
#include "lib/utils.hh"
#include "camera.hh"
#include "viewer.hh"
#include "config.hh"
using namespace cv;
using namespace std;
using namespace std::this_thread;

int main(int argc, char* argv[]) {

	Camera c;
	c.setup();
  if (argc == 2) {
    int desired_num_camera = atoi(argv[1]);
    m_assert(c.num_cameras == desired_num_camera);
  }

  StereoCameraViewer viewer(c);
  viewer.start();
  int cnt = 0;
  while (true) {
    cnt ++;
    auto im0 = c.get_for_calibrate(0);
    auto im1 = c.get_for_calibrate(1);
    cv::imwrite(ssprintf("images/cam0/%05d-0.jpg", cnt), im0);
    cv::imwrite(ssprintf("images/cam1/%05d-1.jpg", cnt), im1);
  }
  viewer.stop();

	c.shutdown();
}
