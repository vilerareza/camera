from concurrent.futures import process
import io
from threading import Condition
import subprocess
import numpy as np
import cv2 as cv
from camera import Camera
from pyzbar.pyzbar import decode, ZBarSymbol
import json

hostNameFile = '/etc/hostname'

camera = Camera()
frame_size = (640, 480)
frame_rate = 10

class StreamingOutput(object):
    # Streaming output object
    def __init__(self):
        self.buffer = io.BytesIO()
        self.qrValid = Condition()
        self.qrData = {}

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
                    self.qrData = data
                    print(self.qrData)
                    # Stopping camera
                    with self.qrValid:
                        self.qrValid.notify_all()                     
            except Exception as e:
                print (f'Qr detection error {e}')

def qr_process(qr_data):
    change_host(host_name = qr_data['host'], host_name_loc = hostNameFile)

def change_host(host_name, host_name_loc):
    with open ('temp', 'w') as file:
        file.write(host_name)
        print ('Setting host name')
        subprocess.run(['sudo', 'mv', 'temp', host_name_loc])
        print ('Rebooting')
        subprocess.run(['sudo', 'reboot', 'now'])

# Initialize streaming output object
output = StreamingOutput()

with output.qrValid:
    camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
    output.qrValid.wait(timeout=60) # timeout
    camera.stop_camera()
    qr_process(output.qrData)