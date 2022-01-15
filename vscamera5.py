import io
import picamera
from threading import Condition, Thread
import socket
import selectors
import RPi.GPIO as GPIO
import time
from functools import partial
from cgi import parse_qs, escape

import numpy as np
from cv2 import imdecode, resize, CascadeClassifier


def start_camera(output):
    '''
    Camera start procedure
    '''
    global camera
    if not camera:
        #camera = picamera.PiCamera(resolution='HD', framerate = 30)
        camera = picamera.PiCamera(resolution = (1280, 720), framerate = 30)
        camera.rotation = 180
        camera.contrast = 0
        camera.sharpness = 50
        camera.start_recording(output, format='mjpeg')
        print('Camera is started')
    else:
        print('Camera is already started') 

def stop_camera():
    '''
    Camera stop procedure
    '''
    global camera
    global t_watcher
    if camera:
        camera.stop_recording()
        camera.close()
        camera = None
        data = b'stop_ok'
        print('Camera is stopped')
    else:
        print('Camera already stopped')
        data = b'was_stop'
    t_watcher = None   # remove stream watcher anyway
    return data

class StreamingOutput(object):
    '''
    Streaming output object
    '''
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        global detector

        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()

            # Face detection
            buff = np.asarray(bytearray(self.buffer.read()))
            img = imdecode(buff, 1)
            bboxes = detector.detectMultiScale(img)
            if len(bboxes)>0:   # Face detected, proceed to recognition
                print ('face detected')

            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

def frame_gen(output):
    '''
    Stream generator function. Stream every frame from output object
    '''
    global streamActive
    global streamCondition
    global isFrameSent
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (frame)
        with streamCondition:
            streamActive = True
            streamCondition.notify_all()

def watcher():
    '''
    Stream watcher function. Stop the camera when stream is not active
    '''
    global streamCondition
    global camera
    while True:
        with streamCondition:
            if (not streamCondition.wait(timeout=5)): # timeout only occur when there is no stream
                if camera:
                    stop_camera()
                    print ('watch stop')
                    break


def servo_start():
    # Servo init
    global servo1
    global servo_center_pos

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11,GPIO.OUT)
    servo1 = GPIO.PWM(11,50)
    servo1.start(0)
    time.sleep(0.1)

def servo_close():
    # Servo cleanup
    global servo1

    servo1.stop()
    GPIO.cleanup()
    servo1 = None

def servo_init():
    global servo1
    global pos
    global servo_center_pos

    servo_start()

    pos = servo_center_pos
    servo1.ChangeDutyCycle(pos)
    time.sleep(0.3)
    servo1.ChangeDutyCycle(0)
    time.sleep(0.3)
    print ('init ok')

    servo_close()


def move_left(distance):
    global moveThread
    global servo1
    global pos
    global posMax
    global step
    # Start servo
    servo_start()
    # Move servo
    if pos < posMax:
        if (pos + distance) >= posMax:
            pos = posMax
        else:
            pos += distance
        print (f'pos: {pos}, step: {step}')
        servo1.ChangeDutyCycle(pos)
        time.sleep(0.1)
        servo1.ChangeDutyCycle(0)
        time.sleep(0.1)
    moveThread = None
    # Stop servo
    servo_close()

def start_move_left(distance):
    global moveThread
    # Start the move thread
    if not moveThread:
        moveThread = Thread(target = partial(move_left, distance))
        moveThread.start()

def move_right(distance):
    global moveThread
    global servo1
    global pos
    global posMin
    global step
    # Start servo
    servo_start()
    # Move servo
    if pos > posMin:
        if (pos - distance) <= posMin:
            pos = posMin
        else:
            pos -= distance
        print (f'pos: {pos}, step: {step}')
        servo1.ChangeDutyCycle(pos)
        time.sleep(0.1)
        servo1.ChangeDutyCycle(0)
        time.sleep(0.1)
    moveThread = None
    # Stop servo
    servo_close()

def start_move_right(distance):
    global moveThread
    # Start the move thread
    if not moveThread:
        moveThread = Thread(target = partial(move_right, distance))
        moveThread.start()


# Camera object
camera = None
# Streaming output object
output = StreamingOutput()
# Stream condition
streamCondition = Condition()
# is streaming active
streamActive = False
# watcher thread
t_watcher = None
# selector for socket
sel = selectors.DefaultSelector()
# live thread
t_live = None
# move thread
moveThread = None
# Servo parameter
servo1 = None
posMin = 3
posMax = 11
servo_center_pos = 7
pos = servo_center_pos
nStep = 50
step = (posMax-posMin) / nStep

# Initialize the servo
servo_init()

# Detector
detector = CascadeClassifier("haarcascade_frontalface_default.xml")


'''app function for wsgi'''

def app(environ, start_response):
    '''
    Application function for WSGI
    '''
    global output
    global camera
    global streamActive
    global t_watcher
    global t_live
    global audioSock

    requestDict = parse_qs(environ['QUERY_STRING'])
    print (requestDict)

    if (requestDict.get('start', '0')[0] == '1'):
        '''
        Start request
        '''
        print('request received: start')

        try:
            # Start camera
            start_camera(output)
            # Start socket
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'image/jpeg'),
            ]
            start_response(status,response_headers)
            print (environ['REMOTE_ADDR'])
            # Start thread for stream watcher
            if not (t_watcher):
                t_watcher = Thread(target = watcher)
                t_watcher.start()
            # Return stream
            return (frame_gen(output))

        except Exception as e:
            print (f'{e}: Camera Starting Error')

    elif (requestDict.get('stop', '0')[0] == '1'):
        '''
        Stop request
        '''
        print('request received: stop')

        try:
            with streamCondition:
                # Check for active streaming
                if (not streamCondition.wait(timeout=1)):
                    # No active streaming, stop the camera
                    data = stop_camera()
                else:
                    # There is active streaming, dont stop the camera
                    print('Active streaming exist, camera continue running')
                    data = b'no_stop_still_streaming'
            # Response
            status = '200 OK'
            response_headers = [
                ('Content-type', 'text/plain'),
                ]
            start_response(status,response_headers)
            # Return data
            return iter ([data])

        except Exception as e:
            print ('Camera closing error')
            print (e)

    elif (requestDict.get('left', '0')[0] != '0'):
        '''
        Move left
        '''
        print ('request received: left')
        data = b'OK'

        distance = float(requestDict.get('left', '0')[0])
        print (f'distance: {distance}')

        try:
            # Move servo
            start_move_left(distance)
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)
            print (environ['REMOTE_ADDR'])
            # Return OK
            return iter([data])

        except Exception as e:
            print ('Response error')
            print (e)


    elif (requestDict.get('right', '0')[0] != '0'):
        '''
        Move right
        '''
        print ('request received: right')
        data = b'OK'

        distance = float(requestDict.get('right', '0')[0])
        print (f'distance: {distance}')

        try:
            # Move servo
            start_move_right(distance)
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)
            print (environ['REMOTE_ADDR'])
            # Return OK
            return iter([data])

        except Exception as e:
            print ('Response error')
            print (e)

    elif (requestDict.get('check', '0')[0] == '1'):
        '''
        Check request
        '''
        print('request received: check')
        print(environ['QUERY_STRING'])
        data = b'OK'

        try:
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)
            print (environ['REMOTE_ADDR'])
            # Return OK
            return iter([data])

        except Exception as e:
            print ('Response error')
            print (e)
