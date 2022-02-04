'''Audio connection module. Create thread to listen new connection'''

import socket
from threading import Condition, Thread
import selectors
import sounddevice as sd
import numpy as np
from functools import partial

class AudioConnection():

    host =''
    lportout = 65001
    lportin = 65002
    lsockout = None
    lsockin = None
    outSock = None
    outFile = None
    inSock = None
    inFile = None
    audioOutStream = None
    audioInStream = None
    fs = 44100

    def __init__(self):
        self.t_listen_in = Thread(target = self.__listen)
        self.t_listen_out = Thread(target = self.__listen)
        self.condition_out = Condition()
        self.condition_in = Condition()

    def __del__(self):
        print('Audio connection destructor called.........')

    def __listen(self, mode):
        # Listen for new connection
        if mode == 'audioin':
            try:
                self.lsockout = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.lsockout.bind((self.host,self.lportout))
                self.lsockout.listen()    # should add for timeout
                # ---Wait for connection---
                print('listening audio connection on, ', (self.host,self.lportout))
                self.outSock, addr = self.lsockout.accept()
                print ('accepted connection from ', addr)
                self.outFile = self.outSock.makefile('wb')
                # Create audio input stream
                self.create_audio_in_stream()
            except:
                self.close_out_connection()

        elif mode =='audioout':
            try:
                self.lsockin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.lsockin.bind((self.host,self.lportin))
                self.lsockin.listen()    # should add for timeout
                # ---Wait for connection---
                print('listening audio connection on, ', (self.host,self.lportin))
                self.inSock, addr = self.lsockin.accept()
                print ('accepted connection from ', addr)
                self.inFile = self.inSock.makefile('rb')
                # Create audio output stream
                self.create_audio_out_stream()
            except Exception as e:
                print (e)
                self.close_in_connection()

    def listen_thread(self, mode = 'audioin'):
        # Starting the listen thread
        if mode == 'audioin':
            if not self.t_listen_in.is_alive():
                self.t_listen_in = Thread(target = partial(self.__listen, mode))
                self.t_listen_in.start()
                print ('audioin thread is started')
            else:
                print ('audioin thread is still alive')

        if mode == 'audioout':
            if not self.t_listen_out.is_alive():
                self.t_listen_out = Thread(target = partial(self.__listen, mode))
                self.t_listen_out.start()
                print ('audioin thread is started')
            else:
                print ('audioin thread is still alive')

    def close_out_connection(self):
        if self.lsockout:
            print ('closing lsockout')
            self.lsockout.close()
            self.lsockout = None
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
        with self.condition_out:
            print ('notify all')
            self.condition_out.notify_all()
        self.audioInStream = None


    def close_in_connection(self):
        if self.lsockin:
            print ('closing lsockin')
            self.lsockin.close()
            self.lsockin = None
        if self.inSock:
            print ('closing inSock')
            self.inSock.close()
            self.inSock = None
            self.inFile.close()
            self.inFile = None

        #if self.audioOutStream:
        with self.condition_in:
            print ('notify all')
            self.condition_in.notify_all()
        self.audioOutStream = None


    def audioOutStream_callback(self, outdata, nsample, time, status):
        if self.inFile:
            try:
                #print ('OK')
                sockData = self.inFile.read(4096)
                temp = np.frombuffer(sockData, dtype=np.float32)
                temp = np.reshape(temp, (1024,1))
                outdata[:1024] = temp
            except Exception as e:
                print (e)
                self.close_in_connection()
        else:
            pass

    def create_audio_out_stream(self):
        if not self.audioOutStream:
            print ('creating audio out stream')
            self.audioOutStream = sd.OutputStream(callback = self.audioOutStream_callback, samplerate = self.fs, channels = 1, blocksize=1024)

            with self.audioOutStream:
                with self.condition_in:
                    self.condition_in.wait()
                print('audio out stream closed')

    def audioInStream_callback(self, indata, nsample, time, status):
        if self.outFile:
            try:
                #print ('OK')
                self.outFile.write(indata.tobytes())
            except Exception as e:
                print ('exception input')
                print (e)
                self.close_out_connection()
        else:
            pass

    def create_audio_in_stream(self):
        if not self.audioInStream:
            print ('creating audio in stream')
            self.audioInStream = sd.InputStream(callback = self.audioInStream_callback, samplerate = self.fs, channels = 1, blocksize=1024)

            with self.audioInStream:
                with self.condition_out:
                    self.condition_out.wait()
                print('audio in stream closed')
