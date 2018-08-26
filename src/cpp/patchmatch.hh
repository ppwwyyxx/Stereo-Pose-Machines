//File: patchmatch.hh


#pragma once

#include <opencv2/core/core.hpp>
#include <utility>
#include "camera.hh"
#include "lib/timer.hh"


typedef std::pair<int, int> PII;

class PatchMatch {
  public:
    PatchMatch(){};

    void init(const Camera& cam, int count);

    void init(const std::vector<cv::Mat>& bg1,
               const std::vector<cv::Mat>& bg2);


    cv::Mat segment(const cv::Mat& im, const cv::Mat& bg) const;

    // return x,y in im1
    PII match(cv::Mat im0, cv::Mat im1,
        int y0, int x0, int y1, int x1);

    std::vector<int> match_all(cv::Mat im0, cv::Mat im1,
        std::vector<int> y0,
        std::vector<int> x0,
        std::vector<int> y1,
        std::vector<int> x1
        ) {
      m_assert(y0.size() == 14);
      std::vector<int> ret(14*4);
      im0 = segment(im0, bg0);
      im1 = segment(im1, bg1);
#pragma omp parallel for schedule(dynamic)
      for (int i = 0; i < 14; ++i) {
        int start = i * 4;
        auto p = match(im0, im1, y0[i], x0[i], y1[i], x1[i]);
        ret[start] = x0[i];
        ret[start+1] = y0[i];
        ret[start+2] = p.first;
        ret[start+3] = p.second;
      }
      return ret;
    }

    std::vector<int> match_with_hm(cv::Mat im0, cv::Mat im1,
        cv::Mat hm0, cv::Mat hm1) {
      cv::Mat splits0[14], splits1[14];
      split(hm0, splits0);
      split(hm1, splits1);

      std::vector<int> y0s, x0s, y1s, x1s;
      for (int i = 0; i < 14; ++i) {
        cv::Point2i max0, max1;
        minMaxLoc(splits0[i], nullptr, nullptr, nullptr, &max0);
        minMaxLoc(splits1[i], nullptr, nullptr, nullptr, &max1);
        x0s.emplace_back(max0.x);
        y0s.emplace_back(max0.y);
        x1s.emplace_back(max1.x);
        y1s.emplace_back(max1.y);
      }
      return match_all(im0, im1, y0s, x0s, y1s, x1s);
    }

    cv::Mat bg0, bg1;

  protected:
    cv::Mat kernel;
};
