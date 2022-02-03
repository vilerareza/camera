'''Audio connection module. Create thread to listen new connection'''

import socket
from threading import Condition, Thread
import selectors
import sounddevice as sd
import numpy as np
from functools import partial

class AudioConnection():

    host =''
    port = 65001
    lsock = None
    outSock = None
    outFile = None
    inSock = None
    inFile = None
    audioOutStream = None
    audioInStream = None
    fs = 44100

    def __init__(self):
        self.t_listen = Thread(target = self.__listen)
        self.condition = Condition()

    def __del__(self):
        print('Audio connection destructor called.........')

    def __listen(self, mode):
        # Listen for new connection
        try:
            self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lsock.bind((self.host,self.port))
            self.lsock.listen()    # should add for timeout
            # ---Wait for connection---
            print('listening audio connection on, ', (self.host,self.port))
            if mode == 'audioin':
                self.outSock, addr = self.lsock.accept()
                self.outFile = self.outSock.makefile('wb')
                self.create_audio_in_stream()
            elif mode =='audioout':
                self.inSock, addr = self.lsock.accept()
                self.inFile = self.inSock.makefile('rb')
                self.create_audio_out_stream()
            print ('accepted connection from ', addr)

        except Exception as e:
            print (e)
            self.close_connection()

    def listen_thread(self, mode = 'audioin'):
        # Starting the listen thread
        if not self.t_listen.is_alive():
            self.t_listen = Thread(target = partial(self.__listen, mode))
            self.t_listen.start()
            print ('socket thread is started')
        else:
            print ('socket thread is still alive')

    def close_connection(self):
        if self.lsock:
            print ('closing lsock')
            self.lsock.close()
            self.lsock = None
        if self.inSock:
            print ('closing inSock')
            self.inSock.close()
            self.inSock = None
            self.inFile.close()
            self.inFile = None
        if self.outSock:
            try:
                print ('closing outSock')
                self.outSock.close()
                self.outFile.close()
            except Exception as e:
                print (e)
            finally:
                self.outSock = None
                self.outFile = None

        #if self.audioOutStream:
        with self.condition:
            print ('notify all')
            self.condition.notify_all()
        self.audioOutStream = None
        self.audioInStream = None

    def audioOutStream_callback(self, outdata, nsample, time, status):
        if self.inFile:
            try:
                print ('OK')
                sockData = self.inFile.read(4096)
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
        if self.outFile:
            try:
                #print ('OK')
                self.outFile.write(indata.tobytes())
            except Exception as e:
                print ('exception input')
                print (e)
                self.close_connection()
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
