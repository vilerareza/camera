from threading import Condition, Thread
from urllib.parse import parse_qs

from camera import Camera
from streamingoutput import StreamingOutput
from audioconnection3 import AudioConnection
from servo import Servo

from cv2 import CascadeClassifier

def frame_gen(output):
    '''
    Stream generator function. Stream every frame from output object
    '''
    global streamActive
    global streamCondition
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
                    camera.stop_camera()
                    print ('watch stop')
                    break

# Camera object
camera = Camera()
# Frame size
#frame_size = (320, 240)
frame_size = (1280, 720)
# Stream condition
streamCondition = Condition()
# is streaming active
streamActive = False
# watcher thread
t_watcher = None
# live thread
t_live = None
# Object tracking
enableTracking = False

# Servo
servo_x = Servo()
servo_y = Servo()

# Initialize the servo
servo_x.servo_init()
servo_y.servo_init()

# Detector
detector = CascadeClassifier("haarcascade_frontalface_default.xml")

# Streaming output object
output = StreamingOutput(frame_size = frame_size, enableTracking = enableTracking, detector = detector, servo_x = servo_x, servo_y = servo_y)

# Audio connection object
audioConnection = AudioConnection()


'''app function for wsgi'''

def app(environ, start_response):
    '''
    Application function for WSGI
    '''
    global camera
    global output
    global streamActive
    global t_watcher
    global t_live
    global frame_size

    requestDict = parse_qs(environ['QUERY_STRING'])
   # print (requestDict)

    if (requestDict.get('start', '0')[0] == '1'):
        '''
        Start request
        '''
        print('request received: start')

        try:
            # Start camera
            camera.start_camera(output, frame_size = frame_size, frame_rate = 15)
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
                    data = camera.stop_camera()
                    t_watcher = None   # remove stream watcher anyway
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
            servo_x.start_move_left(distance)
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)
            #print (environ['REMOTE_ADDR'])
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
            servo_x.start_move_right(distance)
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)
            #print (environ['REMOTE_ADDR'])
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
            audioConnection.listen_thread(mode = 'audioout')
            # Return OK
            return iter([data])

        except Exception as e:
            print (f'{e}: Audio Starting Error')


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
            audioConnection.listen_thread(mode = 'audioin')
            # Return OK
            return iter([data])

        except Exception as e:
            print (f'{e}: Audio input starting error')


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
            print ('Closing audioConnection')
            audioConnection.close_connection()
            # Return OK
            return iter([data])

        except Exception as e:
            print (f'{e}: Audio Stopping')


    elif (requestDict.get('check', '0')[0] == '1'):
        '''
        Check request
        '''
        #print('request received: check')
        #print(environ['QUERY_STRING'])
        data = b'OK'

        try:
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'text/plain'),
            ]
            start_response(status,response_headers)
            #print (environ['REMOTE_ADDR'])
            # Return OK
            return iter([data])

        except Exception as e:
            print ('Response error')
            print (e)
