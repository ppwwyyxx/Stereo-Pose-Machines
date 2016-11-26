//File: pybind.cc
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#include <pybind11/pybind11.h>
namespace py = pybind11;

#include "camera.hh"

/*
 *#include <opencv2/highgui/highgui.hpp>
 *cv::Mat my_imread() {
 *  return cv::imread("cat.jpg");
 *}
 */

PYBIND11_PLUGIN(libcpm) {
    py::module m("libcpm", "CPM3D library in C++");

		// only works for 8UC3
		py::class_<cv::Mat>(m, "Mat")
				.def_buffer([](cv::Mat & m) -> py::buffer_info {
							return py::buffer_info(
								m.data,		// uchar*
								sizeof(uchar),
								py::format_descriptor<uchar>::format(),
								3,
								{ (unsigned long) m.rows, (unsigned long) m.cols, (unsigned long)m.channels() },
								{ sizeof(uchar) * m.cols * m.channels(),
									sizeof(uchar) * m.channels(),
									sizeof(uchar) }
								);
						});

    py::class_<Camera>(m, "Camera")
        .def(py::init<>())
        .def("setup", &Camera::setup)
        .def("shutdown", &Camera::shutdown)
				.def("get", &Camera::get);


		//m.def("my_imread", &my_imread, "my imread");

    return m.ptr();
}
