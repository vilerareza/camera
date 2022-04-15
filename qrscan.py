from camera import Camera
import io
from threading import Condition
import numpy as np
import cv2 as cv
from cv2 import imdecode, imencode
from qr_detector import QRDetector

camera = Camera()
frame_size = (320, 240)
frame_rate = 10

class StreamingOutput(object):
    # Streaming output object
    def __init__(self):
        
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
        self.qrDetector = cv.QRCodeDetector()

    def write(self, buf):

        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                # Reading QR
                # temp = self.buffer.getvalue()
                # npFrame = np.asarray(bytearray(temp))
                # if npFrame.any():
                #     try:
                #         img = imdecode(npFrame, 1)
                #         data, points, _ = self.qrDetector.detectAndDecode(img)
                #         #img, data = QRDetector.read_qr(img)
                #         if data:
                #             print (data)
                #         # Encode the image back from numpy to bytes
                #         _, img = imencode(".jpg", img)
                #         self.frame = img.tobytes()
                #         print ('ok')                      
                #     except Exception as e:
                #         print (f'Qr detection error {e}')
                #         self.frame = temp
                # else:
                #     self.frame = self.buffer.getvalue()
                
                # The frame is ready. Notify all
                self.condition.notify_all()
                print ('ok')
            # Reset buffer pointer
            self.buffer.seek(0)

        return self.buffer.write(buf)

# Initialize streaming output object
output = StreamingOutput()

# Start camera
camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
camera.wait_recording(20)
camera.stop_camera()