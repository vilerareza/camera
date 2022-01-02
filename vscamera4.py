import io
import picamera
from threading import Condition
import threading
import socket
import selectors

def start_camera(output):
    '''
    Camera start procedure
    '''
    global camera
    if not camera:
        camera = picamera.PiCamera(resolution='640x480', framerate = 15)
        #camera.rotation = 0
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
        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()
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

def listen_from_socket():
    '''
    Listen for new connection
    '''
    global comSocket
    global host
    global port
    global sel
    comSocket.bind((host,port))
    comSocket.listen()
    print('listening on, ', (host,port))
    comSocket.setblocking(False)
    sel.register(comSocket, selectors.EVENT_READ, data = None)
    while True:
        events = sel.select(timeout = None) #this blocks
        for key, mask in events:
            if key.data is None:
                print('New connection accepted')
            else:
                print('Communication request')

def start_socket_thread():
    '''
    Start the socket listening thread
    '''
    global t_socket_listen
    if not (t_socket_listen):
        t_socket_listen = threading.Thread(target = listen_from_socket)
        t_socket_listen.start()
        print('Socket thread running: '+str(t_socket_listen.is_alive()))

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
# socket thread
t_socket_listen = None
# socket
comSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host, port
host = ''
port = 65001
# selector for socket
sel = selectors.DefaultSelector()

def app(environ, start_response):
    '''
    Application function for WSGI
    '''
    global output
    global camera
    global streamActive
    global t_watcher
    global audioSock

    if (environ['QUERY_STRING'] == "start"):
        '''
        Start request
        '''
        print('request received: start')

        try:
            # Start camera
            start_camera(output)
            # Start socket
            start_socket_thread()
            # Response
            status = '200 OK'
            response_headers = [
            ('Content-type', 'image/jpeg'),
            ]
            start_response(status,response_headers)
            print (environ['REMOTE_ADDR'])
            # Start thread for stream watcher
            if not (t_watcher):
                t_watcher = threading.Thread(target = watcher)
                t_watcher.start()
            # Return stream
            return (frame_gen(output))

        except Exception as e:
            print ('Camera Starting Error')
            print (e)

    elif (environ['QUERY_STRING'] == "stop"):
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

    else:
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
            ('Content-type', 'image/jpeg'),
            ]
            start_response(status,response_headers)
            print (environ['REMOTE_ADDR'])
            # Return OK
            return iter([data])

        except Exception as e:
            print ('Response error')
            print (e)
