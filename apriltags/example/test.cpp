using namespace std;
#include <iostream>
#include <cstring>
#include <vector>
#include <list>
#include <sys/time.h>
#include <libv4l2.h>
#include <linux/videodev2.h>
#include <fcntl.h>
#include <errno.h>
#include "opencv2/opencv.hpp"
#include "AprilTags/TagDetector.h"
#include "AprilTags/Tag36h11.h"
#include <cmath>
#ifndef PI
const double PI = 3.14159265358979323846;
#endif
const double TWOPI = 2.0*PI;
const char* windowName = "distance_test";
/**
 * Normalize angle to be within the interval [-pi,pi].
 */
inline double standardRad(double t) {
  if (t >= 0.) {
    t = fmod(t+PI, TWOPI) - PI;
  } else {
    t = fmod(t-PI, -TWOPI) + PI;
  }
  return t;
}

double tic() {
  struct timeval t;
  gettimeofday(&t, NULL);
  return ((double)t.tv_sec + ((double)t.tv_usec)/1000000.);
}

/**
 * Convert rotation matrix to Euler angles
 */
void wRo_to_euler(const Eigen::Matrix3d& wRo, double& yaw, double& pitch, double& roll) {
    yaw = standardRad(atan2(wRo(1,0), wRo(0,0)));
    double c = cos(yaw);
    double s = sin(yaw);
    pitch = standardRad(atan2(-wRo(2,0), wRo(0,0)*c + wRo(1,0)*s));
    roll  = standardRad(atan2(wRo(0,2)*s - wRo(1,2)*c, -wRo(0,1)*s + wRo(1,1)*c));
}


class Test{
	AprilTags::TagDetector* m_tagDetector;
  	AprilTags::TagCodes m_tagCodes;
  	bool m_draw; // draw image and April tag detections?
  	int m_width; // image size in pixels
  	int m_height;
  	double m_tagSize; // April tag side length in meters of square black frame
  	double m_fx; // camera focal length in pixels
  	double m_fy;
  	double m_px; // camera principal point
  	double m_py;
  	int m_deviceId; // camera id (in case of multiple cameras)
  	list<string> m_imgNames;
  	cv::VideoCapture m_cap;
  	int m_gain;
  	int m_brightness;
public:
	Test() :
		m_tagDetector(NULL),
		m_tagCodes(AprilTags::tagCodes36h11),
	    m_draw(false),
	    m_width(640),
	    m_height(480),
	    m_tagSize(0.10),
	    m_fx(600),
	    m_fy(600),
	    m_px(m_width/2),
	    m_py(m_height/2),
	    m_gain(-1),
	    m_brightness(-1),
	    m_deviceId(0)
	    {}
    void setup(){
    	m_tagDetector = new AprilTags::TagDetector(m_tagCodes);
    	if (m_draw){
    		cv::namedWindow(windowName,1);
    	}
    }
    void videoSetup(){
    	cv::VideoCapture m_cap;
        if(!m_cap.open("http://localhost:80/test.jpg")) {
      		cerr << "ERROR: Can't find video device " << m_deviceId << "\n";
      		exit(1);
    	}
    	m_cap.set(CV_CAP_PROP_FRAME_WIDTH, m_width);
    	m_cap.set(CV_CAP_PROP_FRAME_HEIGHT, m_height);
    	cout << "Camera successfully opened (ignore error messages above...)" << endl;
    	cout << "Actual resolution: "
         	 << m_cap.get(CV_CAP_PROP_FRAME_WIDTH) << "x"
         	 << m_cap.get(CV_CAP_PROP_FRAME_HEIGHT) << endl;
    }

    void print_result(AprilTags::TagDetection& detection) const{
    	cout << "  Id: " << detection.id;
    	Eigen::Vector3d translation;
    	Eigen::Matrix3d rotation;
    	detection.getRelativeTranslationRotation(m_tagSize, m_fx, m_fy, m_px, m_py,
                                             translation, rotation);
    	Eigen::Matrix3d F;
	    F <<
	      1, 0,  0,
	      0,  -1,  0,
	      0,  0,  1;
	    Eigen::Matrix3d fixed_rot = F*rotation;
	    double yaw, pitch, roll;
	    wRo_to_euler(fixed_rot, yaw, pitch, roll);

	    cout << "  distance=" << translation.norm()
	         << "m, x=" << translation(0)
	         << ", y=" << translation(1)
	         << ", z=" << translation(2)
	         << ", yaw=" << yaw
	         << ", pitch=" << pitch
	         << ", roll=" << roll
	         << endl;
    }

    void processImage(cv::Mat& image, cv::Mat& image_gray){
    	cv::cvtColor(image, image_gray, CV_BGR2GRAY);
    	double t0;
    	vector<AprilTags::TagDetection> detections = m_tagDetector->extractTags(image_gray);
    	for (int i=0; i<detections.size(); i++) {
    		print_result(detections[i]);
    	}
    	if (m_draw) {
      		for (int i=0; i<detections.size(); i++) {
        		detections[i].draw(image);
     		}
      		imshow(windowName, image); 
    	}
    }
  	void loop(){
  		cv::Mat image;
  		cv::Mat image_gray;
  		int frame = 0;
  		double last_t = tic();
  		while (true){
  			m_cap.read(image);
  			processImage(image, image_gray);
  			frame++;
      		if (frame % 10 == 0) {
        		double t = tic();
        		cout << "  " << 10./(t-last_t) << " fps" << endl;
        		last_t = t;
      		}
      		if (cv::waitKey(1) >= 0) break;
  		}
  	}
};

int main(int argc, char* argv[]){
	Test test;
	test.setup();
	test.videoSetup();
	test.loop();
	return 0;
}