//File: pybind.cc
//Author: Yuxin Wu <ppwwyyxxc@gmail.com>

#include <pybind11/pybind11.h>
namespace py = pybind11;

#include "camera.hh"


PYBIND11_PLUGIN(example) {
    py::module m("libcpm", "CPM3D library in C++");

    py::class_<Camera>(m, "Camera")
        .def(py::init<>())
        .def("setup", &Camera::setup)
        .def("shutdown", &Camera::shutdown);
    return m.ptr();
}
