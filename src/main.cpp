//File: main.cpp
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#include <opencv2/highgui/highgui.hpp>
#include <chrono>

#include "lib/timer.hh"
#include "camera.hh"
#include "viewer.hh"
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
  sleep_for(std::chrono::seconds(10));
  viewer.stop();

	c.shutdown();
}
