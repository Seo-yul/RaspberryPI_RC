#include "highgui.h"
#include "cv.h"

int main(void){
    double wsize = 320;
    double hsize = 240;

    cvNameWindow("FaceDectection", CV_WINDOW_AUTOSIZE);

    CvCapture* capture = NULL;

    capture = cvCreateCmameraCapture(0);
    cvSetCaptureProperty (capture, CV_CAP_PROP_FRAME_WIDTH, wsize);rr
}
