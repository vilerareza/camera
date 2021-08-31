import io
import picamera
import logging
from threading import Condition
import threading

#myFrameCollector = None
camera = None

def start_camera(output):
    global camera
    if not camera:
        camera = picamera.PiCamera(resolution='640x480', framerate = 15)
        camera.start_recording(output, format='mjpeg')
        print("Camera is started")
    else:
        print("Camera already started")

def stop_camera():
    global camera
    if (camera):
        camera.stop_recording()
        camera.close()
        camera = None
        print("Camera is stopped")

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

def frame_gen(output):
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
            yield (frame)

'''
class FrameCollector():

    output = StreamingOutput()
    start_camera(output)
#    t_start_camera = threading.Thread()
#    camera = picamera.PiCamera(resolution='640x480', framerate=24)

    def __start_camera(self):
        self.camera.start_recording(self.output, format='mjpeg')
        print("Camera is started")

    def stop_camera(self):
        self.camera.stop_recording()
        camera.close()
        camera = None
        print("Camera is stopped")

    def start_thread(self):
        if not (self.t_start_camera.is_alive()):
            self.t_start_camera = threading.Thread(target = self.__start_camera)
            self.t_start_camera.start()
           print ("Camera thread is "+ str(self.t_start_camera.is_alive()))

    def stop_camera(self):
        self.camera.stop_recording()
        camera.close()
        camera = None
        print("Camera is stopped")    def stop_thread(self):
        if (self.t_start_camera.is_alive()):
            self.t_start_camera.join()

    def frame_gen(self):
        while True:
            with self.output.condition:
                self.output.condition.wait()
                frame = self.output.frame
                yield (frame)
'''

def app(environ, start_response):

    #global myFrameCollector
    #myFrameCollector = None

    if (environ['QUERY_STRING'] == "start"):

        print('request received: start')
        output = StreamingOutput()
        start_camera(output)
#        myFrameCollector = FrameCollector()
#        myFrameCollector.start_thread()
#        myFrameCollector.start_camera()
        status = '200 OK'
        response_headers = [
            ('Content-type', 'image/jpeg'),
            ]

        start_response(status,response_headers)
        print (environ['REMOTE_ADDR'])
#        return iter ([b'data']) #myFrameCollector.frame_gen())
        return (frame_gen(output))

    else:

#        if (myFrameCollector == None):
#            print('stopping camera')
#            try:
#                myFrameCollector.stop_camera()
#                myFrameCollector = None
#                myFrameCollector.stop_thread()
#            except Exception as e:
#                print(e)
#                print ('camera close error')

        print('disconnecting')

        stop_camera()
        data = b'OK'
        status = '200 OK'
        response_headers = [
            ('Content-type', 'image/jpeg'),
            ]
        start_response(status,response_headers)
        return iter ([data])
