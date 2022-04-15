import io
from functools import partial
from threading import Thread
import numpy as np
import cv2 as cv
from camera import Camera

camera = Camera()
frame_size = (320, 240)
frame_rate = 10

class StreamingOutput(object):
    # Streaming output object
    
    def __init__(self):
        self.buffer = io.BytesIO()
        self.qrDetector = cv.QRCodeDetector()
        self.bufferReady = True

    def write(self, buf):
        if self.bufferReady:
            if buf.startswith(b'\xff\xd8'):
                # New frame
                self.buffer.truncate()
                # Reading QR
                frame = self.buffer.getvalue()
                t_read_qr = Thread(target = partial(self.read_qr, frame))
                t_read_qr.start()
                print ('ok')
                # Reset buffer pointer
                self.buffer.seek(0)
            return self.buffer.write(buf)

    def read_qr(self, frame):
        self.bufferReady = False
        npFrame = np.asarray(bytearray(frame))
        if npFrame.any():
            try:
                img = cv.imdecode(npFrame, 1)
                data, _, __ = self.qrDetector.detectAndDecode(img)
                if data:
                    print (data)                     
            except Exception as e:
                print (f'Qr detection error {e}')
        self.bufferReady = True

# Initialize streaming output object
output = StreamingOutput()

camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
camera.wait_recording(60)
camera.stop_camera()