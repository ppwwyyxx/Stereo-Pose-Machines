//File: patchmatch.cc


#include <iostream>
#include "patchmatch.hh"

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
using namespace std;
using namespace cv;


namespace {

const int PATCH_SIZE = 20;
const int REGION_SIZE = 30;

cv::Mat avg_image(const std::vector<cv::Mat>& mats) {
  cv::Mat curr;
  cv::Mat sum = cv::Mat::zeros(mats[0].rows, mats[0].cols, CV_32FC3);
  for (auto& m : mats) {
    m.convertTo(curr, CV_32FC3, 1.0/255.0);
    sum += curr;
  }
  float fac = 255.0 / mats.size();
  sum = sum * fac;
  return sum;  // float in [0,255]
}

cv::Mat vconcat(const cv::Mat& m1, const cv::Mat& m2) {
	int newh = m1.rows << 1;
	cv::Mat ret(newh, m1.cols, CV_8UC3);
  int sz = m1.rows * m1.cols * 3;
	memcpy(ret.data, m1.data, sz * sizeof(uchar));
  memcpy((uchar*)ret.data + sz, m2.data, sz * sizeof(uchar));
	return ret;
}

cv::Mat take_patch(cv::Mat im, int y, int x, int size) {
  cv::Mat canvas =  Mat::zeros(size*2,size*2,CV_8UC3);

  int ybegin = y - size, yoffset = 0;
  if (ybegin < 0) yoffset = -ybegin, ybegin = 0;
  int yend = y + size, yoffset2 = size * 2;
  if (yend > im.rows) yoffset2 += im.rows - yend, yend = im.rows;

  int xbegin = x - size, xoffset = 0;
  if (xbegin < 0) xoffset = -xbegin, xbegin = 0;
  int xend = x + size, xoffset2 = size * 2;
  if (xend > im.cols) xoffset2 += im.cols - xend, xend = im.cols;

  for (int i = 0; i < yend - ybegin; ++i)
    for (int j = 0; j < xend - xbegin; ++j) {
      canvas.at<Vec3b>(i + yoffset, j + xoffset) =
        im.at<Vec3b>(i + ybegin, j + xbegin);
    }
  return canvas;
}

}

void PatchMatch::init(
    const std::vector<cv::Mat>& bgs0,
     const std::vector<cv::Mat>& bgs1) {
  bg0 = avg_image(bgs0) ;
  bg1 = avg_image(bgs1);

  kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3,3));
}

void PatchMatch::init(const Camera& cam, int count) {
  std::vector<cv::Mat> bg0, bg1;
  while (count --) {
    auto m0 = cam.get_for_py(0),
         m1 = cam.get_for_py(1);
    bg0.push_back(m0);
    bg1.push_back(m1);
  }
  init(bg0, bg1);
  cout << "Background initialized ..." << endl;
}

cv::Mat PatchMatch::segment(const cv::Mat& im, const cv::Mat& bg) const {
  cv::Mat mask(im.rows, im.cols, CV_8UC1);
  for (int i = 0; i < im.rows; ++i)
    for (int j = 0; j < im.cols; ++j) {
      Vec3b origc = im.at<Vec3b>(i, j);
      Vec3f orig{(float)origc[0], (float)origc[1], (float)origc[2]};
      cv::Vec3f d = orig - bg.at<Vec3f>(i, j);
      float diff = d[0]*d[0] + d[1]*d[1] + d[2]*d[2];
      diff /= 20;
      if (diff > 255) diff = 255;
      mask.at<uchar>(i, j) = diff;
    }
  morphologyEx(mask, mask, cv::MORPH_OPEN, kernel);
  dilate(mask, mask, kernel);

  cv::Mat ret = im.clone();
  for (int i = 0; i < im.rows; ++i)
    for (int j = 0; j < im.cols; ++j) {
      if (mask.at<uchar>(i, j) < 10)
        ret.at<Vec3b>(i, j) = {0,0,0};
    }
  return ret;
}

PII PatchMatch::match(cv::Mat im0, cv::Mat im1,
    int y0, int x0, int y1, int x1) {
  auto target = take_patch(im0, y0, x0, PATCH_SIZE);
  auto region = take_patch(im1, y1, x1, REGION_SIZE);
  cv::Mat res;
  matchTemplate(region, target, res, cv::TM_CCOEFF_NORMED);
  cv::Point2i maxp;
  minMaxLoc(res, nullptr, nullptr, nullptr, &maxp);
  maxp.x += PATCH_SIZE + x1 - REGION_SIZE;
  maxp.y += PATCH_SIZE + y1 - REGION_SIZE;
  return {maxp.x, maxp.y};
}
