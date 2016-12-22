//File: homography.cc
//Author: Yuxin Wu <ppwwyyxx@gmail.com>

#include "homography.hh"

#include <Eigen/Dense>
#include <vector>

//#include "lib/matrix.hh"
//#include "lib/polygon.hh"

using namespace std;

namespace {
inline Eigen::Map<Eigen::Matrix<double, 3, 3, Eigen::RowMajor>>
	to_eigenmap(const Homography& m) {
		return Eigen::Map<Eigen::Matrix<double, 3, 3, Eigen::RowMajor>>(
				(double*)m.data, 3, 3);
	}
}

Homography Homography::inverse(bool* succ) const {
	using namespace Eigen;
	Homography ret;
	auto res = to_eigenmap(ret),
			 input = to_eigenmap(*this);
	FullPivLU<Eigen::Matrix<double,3,3,RowMajor>> lu(input);
	if (succ == nullptr) {
		m_assert(lu.isInvertible());
	} else {
		*succ = lu.isInvertible();
		if (! *succ) return ret;
	}
	res = lu.inverse().eval();
	return ret;
}

Homography Homography::operator * (const Homography& r) const {
	Homography ret;
	auto m1 = to_eigenmap(*this),
			 m2 = to_eigenmap(r),
			 res = to_eigenmap(ret);
	res = m1 * m2;
	return ret;
}

