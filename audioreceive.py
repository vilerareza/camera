import socket
import selectors
import sounddevice as sd
import numpy as np

from threading import Condition, Thread
from cgi import parse_qs, escape
import numpy as np


class AudioConnection():

    host =''
    port = 65001
    lsock = None
    connSock = None
    sockFile = None
    audioOutStream = None
    audioInStream = None
    fs = 44100

    def __init__(self):
        self.t_listen = Thread(target = self.__listen)
        self.condition = Condition()

    def __del__(self):
        print('Destructor called.........')

    def __listen(self):
        # Listen for new connection

        try:
            self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lsock.bind((self.host,self.port))
            self.lsock.listen()
            print('listening on, ', (self.host,self.port))
            self.connSock, addr = self.lsock.accept()
            # ---Wait for connection---
            print ('accepted connection from ', addr)
            #self.sockFile = self.connSock.makefile('rb')
            self.sockFile = self.connSock.makefile('wb')
            #self.create_audio_out_stream()
            self.create_audio_in_stream()
        except Exception as e:
            print (e)
            self.close_connection()

    def listen_thread(self):
        # Starting the listen thread
        if not self.t_listen.is_alive():
            self.t_listen = Thread(target = self.__listen)
            self.t_listen.start()
            print ('socket thread is alive')

    def close_connection(self):
        if self.lsock:
            print ('closing lsock')
            self.lsock.close()
            #self.lsock = None
        if self.connSock:
            print ('closing connsock')
            self.connSock.close()
            self.connSock = None
            self.sockFile.close()
            self.sockFile = None
        if self.audioOutStream:
            with self.condition:
                print ('notify all')
                self.condition.notify_all()
            self.audioOutStream = None

    def audioOutStream_callback(self, outdata, nsample, time, status):
        if self.sockFile:
            try:
                print ('OK')
                sockData = self.sockFile.read(4096)
                temp = np.frombuffer(sockData, dtype=np.float32)
                temp = np.reshape(temp, (1024,1))
                outdata[:1024] = temp
            except Exception as e:
                print (e)
                self.close_connection()
        else:
            pass

    def create_audio_out_stream(self):
        if not self.audioOutStream:
            print ('creating audio out stream')
            self.audioOutStream = sd.OutputStream(callback = self.audioOutStream_callback, samplerate = self.fs, channels = 1, blocksize=1024)

            with self.audioOutStream:
                with self.condition:
                    self.condition.wait()
                print('audio out stream closed')

    def audioInStream_callback(self, indata, nsample, time, status):
        if self.sockFile:
            #try:
            print ('OK')
            self.sockFile.write(indata.tobytes())
            #except Exception as e:
            #    print ('exception input')
            #    print (e)
            #    self.close_connection()
        else:
            pass

    def create_audio_in_stream(self):
        if not self.audioInStream:
            print ('creating audio in stream')
            self.audioInStream = sd.InputStream(callback = self.audioInStream_callback, samplerate = self.fs, channels = 1, blocksize=1024)

            with self.audioInStream:
                with self.condition:
                    self.condition.wait()
                print('audio in stream closed')


audioConnection = AudioConnection()

'''app function for wsgi'''

def app(environ, start_response):
    '''
    Application function for WSGI
    '''

    requestDict = parse_qs(environ['QUERY_STRING'])
    print (requestDict)

    global audioConnection

    if (requestDict.get('start', '0')[0] == '1'):
        '''
        Start request
        '''
        print('request received: start')

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


    elif (requestDict.get('stop', '0')[0] == '1'):
        '''
        Stop request
        '''
        print('request received: stop')

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


    else:
        '''
        Unknown request
        '''
        print('request received: unknown')

        data = b'NA'

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
            print (f'{e}')
