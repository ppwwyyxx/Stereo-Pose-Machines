//File: undistort.hh


#pragma once
#include <vector>
#include "homography.hh"
#include <opencv2/imgproc/imgproc.hpp>

class UnDistorter {
  public:
    UnDistorter(const std::vector<float>& intrinsics,
        const std::vector<float>& distortion):
      K{cv::Mat::eye(3,3,CV_32F)}, distortion{distortion} {
      K.at<float>(0,0) = intrinsics[0];
      K.at<float>(1,1) = intrinsics[1];
      K.at<float>(0,2) = intrinsics[2];
      K.at<float>(1,2) = intrinsics[3];
    }

    cv::Mat K;
    std::vector<float> distortion;

    cv::Mat undistort(cv::Mat im) const {
      cv::Mat ret;
      cv::undistort(im, ret, K, distortion);
      return ret;
    }

};
