import io
from threading import Condition
import numpy as np
import cv2 as cv
from camera import Camera
from pyzbar.pyzbar import decode, ZBarSymbol
import json

camera = Camera()
frame_size = (320, 240)
frame_rate = 10

class StreamingOutput(object):
    # Streaming output object
    def __init__(self, camera):
        self.buffer = io.BytesIO()
        self.camera = camera
        self.qrValid = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()
            # Reading QR
            frame = self.buffer.getvalue()
            self.read_qr(frame)
            print ('ok')
            # Reset buffer pointer
            self.buffer.seek(0)
        return self.buffer.write(buf)

    def read_qr(self, frame):
        npFrame = np.asarray(bytearray(frame))
        if npFrame.any():
            try:
                img = cv.imdecode(npFrame, 1)
                qr = decode(img, symbols = [ZBarSymbol.QRCODE])
                if len (qr) > 0:
                    data = (qr[0].data).decode()
                    data = json.loads(data)
                    print(data)
                    # Stopping camera
                    with self.qrValid:
                        self.qrValid.notify_all()                     
            except Exception as e:
                print (f'Qr detection error {e}')

# Initialize streaming output object
output = StreamingOutput(camera)

with output.qrValid:
    camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
    output.qrValid.wait(timeout=60) # timeout
    camera.stop_camera()