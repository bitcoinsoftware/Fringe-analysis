import cv
import threading
class Camera(threading.Thread):
    stan = 0
    def run(self):
        print("camera")
        self.capture =  cv.CaptureFromCAM(0)
        width =cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH)
        height = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT)
        self.writer = cv.CreateVideoWriter( "myCamCapture.avi",-1,30,(int(width), int(height)),1 )
        self.record()
    
    def record(self):
        self.stan=1
        while self.stan:
            original = cv.QueryFrame(self.capture)
            size = cv.GetSize(original)
            cv.ShowImage('Camera picture - PRESS ESC TO EXIT', original)
            k = cv.WaitKey(33)	
            if k == 0x1b: # ESC
                print 'ESC pressed. Exiting ...'
                break
            cv.WriteFrame(self.writer, original )
        #cv.ReleaseCapture(self.capture)
        cv.cvReleaseVideoWriter(self.writer)
        


        
        
"""
void main( )
{
CvCapture *capture = cvCaptureFromCAM( 0 );

int width = ( int )cvGetCaptureProperty( capture, CV_CAP_PROP_FRAME_WIDTH );
int height = ( int )cvGetCaptureProperty( capture, CV_CAP_PROP_FRAME_HEIGHT );
CvVideoWriter *writer = cvCreateVideoWriter( "myCamCapture.avi",
-1,30, cvSize(  width, height ) );
cvNamedWindow("d", CV_WINDOW_AUTOSIZE);
IplImage *frame = 0;


while( 1 )
{
    frame = cvQueryFrame( capture );

    cvShowImage("d",frame);
    cvWriteFrame( writer, frame );
    char c = cvWaitKey( 33 );
    if( c == 27 ) break;
}

cvReleaseCapture( &capture );
cvReleaseVideoWriter( &writer );
cvDestroyWindow( "d" );


    }

"""
