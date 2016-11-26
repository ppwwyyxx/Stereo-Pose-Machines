//File: camera.cc

#include "camera.hh"

#include <thread>
#include <pylon/PylonIncludes.h>

using namespace Pylon;
using namespace std;

const size_t Camera::kMaxCameras;

void worker(Camera& camera) {
	CTlFactory& tlFactory = CTlFactory::GetInstance();

	// Get all attached devices and exit application if no device is found.
	DeviceInfoList_t devices;
	if ( tlFactory.EnumerateDevices(devices) == 0 ) {
		throw RUNTIME_EXCEPTION( "No camera present.");
	}

	CInstantCameraArray cameras(min(devices.size(), Camera::kMaxCameras));

	// Create and attach all Pylon Devices.
	for ( size_t i = 0; i < cameras.GetSize(); ++i) {
		cameras[i].Attach(tlFactory.CreateDevice(devices[i]));

		// Print the model name of the camera.
		cout << "Using device " << cameras[i].GetDeviceInfo().GetModelName() << endl;
	}

	// Starts grabbing for all cameras starting with index 0. The grabbing
	// is started for one camera after the other. That's why the images of all
	// cameras are not taken at the same time.
	// However, a hardware trigger setup can be used to cause all cameras to
	// grab images synchronously.
	// According to their default configuration, the cameras are
	// set up for free-running continuous acquisition.
	cameras.StartGrabbing();

	cout << "Start grabbing ..." << endl;

	// This smart pointer will receive the grab result data.
	CGrabResultPtr ptrGrabResult;
	Pylon::CImageFormatConverter formatConverter;
	formatConverter.OutputPixelFormat = Pylon::PixelType_BGR8packed;
	Pylon::CPylonImage pylonImage;
	cv::Mat openCVImage;

	try {
		while (cameras.IsGrabbing() && not camera.is_stopped()) {
			cameras.RetrieveResult(5000, ptrGrabResult,
					TimeoutHandling_ThrowException);
			if (ptrGrabResult->GrabSucceeded()) {
				formatConverter.Convert(pylonImage, ptrGrabResult);
				openCVImage = cv::Mat(
						ptrGrabResult->GetHeight(),
						ptrGrabResult->GetWidth(),
						CV_8UC3,
						(uint8_t *)pylonImage.GetBuffer());
			}

			// When the cameras in the array are created the camera context value
			// is set to the index of the camera in the array.
			// The camera context is a user settable value.
			// This value is attached to each grab result and can be used
			// to determine the camera that produced the grab result.
			intptr_t cameraContextValue = ptrGrabResult->GetCameraContext();
			int index = cameraContextValue;

			camera.m_cameras[index] = openCVImage;
		}
	} catch (const GenericException &e) {
		// Error handling
		cerr << "An exception occurred! " << endl << e.GetDescription() << endl;
		exit(1);
	}
}

void Camera::setup() {
	m_worker_th = thread([&] {
			PylonInitialize();
			worker(*this);
			PylonTerminate();
	});
}


void Camera::shutdown() {
	m_stopped = true;
	m_worker_th.join();
}
