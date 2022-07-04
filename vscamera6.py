import io
import picamera
from threading import Condition, Thread
import socket
import selectors
import RPi.GPIO as GPIO
import time
from functools import partial
from urllib.parse import parse_qs

import sounddevice as sd
from audioconnection import AudioConnection

import numpy as np
from cv2 import imdecode, imencode, rectangle, CascadeClassifier

def start_camera(output, frame_size):
    '''
    Camera start procedure
    '''
    global camera
    if not camera:
        #camera = picamera.PiCamera(resolution='HD', framerate = 30)
        camera = picamera.PiCamera(resolution = frame_size, framerate = 10)
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
    def __init__(self, frame_size = (640, 480), servo_max_move=0, move_x = None, move_y = None):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
        self.detector = None
        self.enableTracking = True
        self.servoMaxMove = servo_max_move
        self.frameSize = frame_size
        self.move_left = move_x[0]
        self.move_right = move_x[1]
        self.move_y = move_y

    def write(self, buf):

        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()

            with self.condition:
                #self.frame = self.buffer.getvalue()
                temp = self.buffer.getvalue()

                if self.enableTracking:
                    # Object tracking enabled. Perform detection
                    npFrame = np.asarray(bytearray(temp))
                    if npFrame.any():
                        img = imdecode(npFrame, 1)
                        bboxes = detector.detectMultiScale(img)
                        if len(bboxes)>0:   # Face detected, proceed to recognition
                            img = self.draw_box(img, bboxes)
                            print ('face detected. draw OK')
                            # Movement, take bboxes[0] only?
                            distance_x = self.calculate_move_x(center_x = self.frameSize[0]/2, bbox_x = bboxes[0][0])
                            if distance_x > 0.1:
                            # bbox is at left area
                                self.move_left(abs(distance_x))
                            elif distance_x < -0.1:
                            # Touch is at right area
                                self.move_right(abs(distance_x))
                        # Encode the image back from numpy to bytes
                        retval, img = imencode(".jpg", img)
                        self.frame = img.tobytes()
                        print (f'frame type: {type(self.frame)}, npFrame type: {type(npFrame)}, size: {len(npFrame)}, lenbbox : {len(bboxes)}')
                    else:
                        self.frame = self.buffer.getvalue()
                else:
                    self.frame = self.buffer.getvalue()


                self.condition.notify_all()

            self.buffer.seek(0)
        return self.buffer.write(buf)

    def enable_tracking(self, detector):
        self.enableTracking = True
        self.detector = detector

    def disable_tracking(self, detector):
        self.enableTracking = False
        self.detector = None

    def draw_box(self, img, boxes):
        if boxes.any():
            for box in boxes:
                xb, yb, widthb, heightb = box
                rectangle(img, (xb, yb), (xb+widthb, yb+heightb), color = (232,164,0), thickness = 3)
        return img

    def calculate_move_x(self, center_x, bbox_x):
        distance = (((center_x) - bbox_x)/(center_x)) * self.servoMaxMove
        print (f'move distance: {distance}, bbox_x: {bbox_x}')
        return distance


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
# Frame size
frame_size = (320, 240)
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
servo_max_move = 1.7

# Streaming output object
output = StreamingOutput(frame_size = frame_size, servo_max_move = servo_max_move, move_x = (start_move_left, start_move_right))

# Initialize the servo
servo_init()

# Detector
detector = CascadeClassifier("haarcascade_frontalface_default.xml")

# Object tracking
enableTracking = True

# Audio connection object
audioConnection = AudioConnection()


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
    global frame_size

    requestDict = parse_qs(environ['QUERY_STRING'])
    print (requestDict)

    if (requestDict.get('start', '0')[0] == '1'):
        '''
        Start request
        '''
        print('request received: start')

        try:
            # Start camera
            start_camera(output, frame_size = frame_size)
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

    elif (requestDict.get('audioout', '0')[0] == '1'):
        '''
        Start request
        '''
        print('request received: audioout')

        data = b'OK'

        try:
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)

            print (environ['REMOTE_ADDR'])

            audioConnection.listen_thread()

            return iter([data])

        except Exception as e:
            print (f'{e}: Audio Starting Error')


    elif (requestDict.get('audiostop', '0')[0] == '1'):
        '''
        Stop request
        '''
        print('request received: audiostop')

        data = b'OK'

        try:
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)

            print (environ['REMOTE_ADDR'])

            print ('Closing audioConnection')
            audioConnection.close_connection()

            # Return OK
            return iter([data])

        except Exception as e:
            print (f'{e}: Audio Stopping')


    elif (requestDict.get('audioin', '0')[0] == '1'):
        '''
        Audio in request
        '''
        print('request received: audioin')

        data = b'OK'

        try:
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)

            print (environ['REMOTE_ADDR'])

            audioConnection.listen_thread()
            #audioConnection.create_audio_in_stream()

            return iter([data])

        except Exception as e:
            print (f'{e}: Audio input starting error')


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
