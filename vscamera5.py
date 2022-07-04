import io
import picamera
from threading import Condition, Thread
import socket
import selectors
import RPi.GPIO as GPIO
import time
from functools import partial
from urllib.parse import parse_qs

import numpy as np

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
