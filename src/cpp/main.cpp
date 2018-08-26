//File: main.cpp


#include <opencv2/highgui/highgui.hpp>
#include <chrono>

#include "lib/timer.hh"
#include "lib/utils.hh"
#include "camera.hh"
#include "viewer.hh"
#include "patchmatch.hh"
#include "config.hh"
using namespace cv;
using namespace std;
using namespace std::this_thread;

cv::Mat vconcat(const cv::Mat& m1, const cv::Mat& m2) {
	int newh = m1.rows << 1;
	cv::Mat ret(newh, m1.cols, CV_8UC3);
  int sz = m1.rows * m1.cols * 3;
	memcpy(ret.data, m1.data, sz * sizeof(uchar));
  memcpy((uchar*)ret.data + sz, m2.data, sz * sizeof(uchar));
	return ret;
}

int main(int argc, char* argv[]) {

	Camera c;
	c.setup();
  if (argc == 2) {
    int desired_num_camera = atoi(argv[1]);
    m_assert(c.num_cameras == desired_num_camera);
  }

  PatchMatch matcher; matcher.init(c, 20);

  StereoCameraViewer viewer(c);
  viewer.start();
  int cnt = 0;
  while (true) {
    cnt ++;
    // for calibration
    auto im0 = c.get_cropped(0);
    auto im1 = c.get_cropped(1);
    cv::imwrite(ssprintf("images/cam0/%05d00000000000000.jpg", cnt), im0);
    cv::imwrite(ssprintf("images/cam1/%05d00000000000000.jpg", cnt), im1);
  }
  viewer.stop();

	c.shutdown();
}
