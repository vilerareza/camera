from camera import Camera
import io
import numpy as np
import cv2 as cv

camera = Camera()
frame_size = (320, 240)
frame_rate = 10

class StreamingOutput(object):
    # Streaming output object
    
    def __init__(self):
        self.buffer = io.BytesIO()
        self.qrDetector = cv.QRCodeDetector()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()
            # Reading QR
            frame = self.buffer.getvalue()
            npFrame = np.asarray(bytearray(frame))
            if npFrame.any():
                try:
                    img = cv.imdecode(npFrame, 1)
                    data, _, __ = self.qrDetector.detectAndDecode(img)
                    if data:
                        print (data)
                    print ('ok')                      
                except Exception as e:
                    print (f'Qr detection error {e}')
            print ('ok')
            # Reset buffer pointer
            self.buffer.seek(0)

        return self.buffer.write(buf)

# Initialize streaming output object
output = StreamingOutput()

camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
camera.wait_recording(20)
camera.stop_camera()