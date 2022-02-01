'''Audio connection module. Create thread to listen new connection'''

from functools import partial
import socket
from threading import Condition, Thread
import selectors
import sounddevice as sd
import numpy as np

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
        self.condition = Condition()
        self.sel = selectors.DefaultSelector()
        self.t_listen = Thread(target = self.__listen)

    def __del__(self):
        print('Audio connection destructor called.........')

    def __accept_wrapper(self,sock, mode):
        self.outSock, addr = sock.accept()
        print (f'Accepted connection from: {addr}, mode: {mode}')
        self.outSock.setblocking(False)
        events = selectors.EVENT_READ
        self.sel.register(self.outSock, events, data = mode)

    def __service_connection (self, key, mask):
        sock = key.fileobj
        mode = key.data
        try:
            if mode == 'audioin':
                self.outFile = sock.makefile('wb')
                self.create_audio_in_stream()
            elif mode == 'audioout':
                self.inFile = sock.makefile('rb')
                self.create_audio_out_stream()
        except:
            print ('Error, closing connection...')
            self.sel.unregister(sock)
            sock.close()

    def __listen(self, mode = 'audioin'):
        # Listen for new connection
        if not self.lsock:
            try:
                self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.lsock.bind((self.host,self.port))
                self.lsock.listen()
                print('listening audio connection on, ', (self.host,self.port))

                self.lsock.setblocking(False)
                self.sel.register(self.lsock, selectors.EVENT_READ, data = None)

                while True:
                    events = self.sel.select(timeout = None) #this blocks
                    print ('event')
                    for key, mask in events:
                        if key.data is None:
                            self.__accept_wrapper(key.fileobj, mode)
                        else:
                            self.__service_connection(key, mask)

            except Exception as e:
                print (e)
                self.close_connection()

        else:
            print ('listening socket already exist...')

    def listen_thread(self, mode):
        # Starting the listen thread
        if not self.t_listen.is_alive():
            self.t_listen = Thread(target = partial(self.__listen, mode))
            self.t_listen.start()
            print ('socket thread is alive')
        else:
            print ('t_listen is alive')


    def close_connection(self):
        if self.lsock:
            print ('closing lsock')
            self.sel.unregister(self.lsock)
            self.lsock.close()
            self.lsock = None
        if self.inSock:
            print ('closing inSock')
            self.sel.unregister(self.inSock)
            self.inSock.close()
            self.inSock = None
        if self.outSock:
            print ('closing outSock')
            self.sel.unregister(self.outSock)
            self.outSock.close()
            self.outSock = None
        if self.audioOutStream:
            with self.condition:
                print ('notify all')
                self.condition.notify_all()
            self.audioOutStream = None

    def audioOutStream_callback(self, outdata, nsample, time, status):
        if self.inFile:
            try:
                print ('OK')
                sockData = self.inFile.read(4096)
                temp = np.frombuffer(sockData, dtype=np.float32)
                temp = np.reshape(temp, (1024,1))
                outdata[:1024] = temp
            except Exception as e:
                print (f'error at callback {e}')
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
                print ('OK')
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
