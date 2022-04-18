import io
from threading import Condition
import numpy as np
import cv2 as cv
from cv2 import imdecode, imencode, rectangle
from pyzbar.pyzbar import decode, ZBarSymbol
import json

class StreamingOutput(object):
    '''
    Streaming output object
    '''
    def __init__(self, frame_size, servo_x, servo_y, mode = 'normal', detector = None):
        
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
        self.mode = mode
        self.detector = detector
        self.frameSize = frame_size
        self.servo_x = servo_x
        self.servo_y = servo_y
        self.qrDetector = cv.QRCodeDetector()

    def write(self, buf):

        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()
            with self.condition:

                if self.mode == 'normal':
                    self.frame = self.buffer.getvalue()

                elif self.mode == 'tracking':
                    # Object tracking enabled. Perform detection
                    temp = self.buffer.getvalue()
                    npFrame = np.asarray(bytearray(temp))
                    if npFrame.any():
                        try:
                            img = imdecode(npFrame, 1)
                            bboxes = self.detector.detectMultiScale(img)
                            if len(bboxes)>0:   # Face detected, proceed to recognition
                                img = self.draw_box(img, bboxes)
                                print ('face detected. draw OK')
                                # Movement, take bboxes[0] only?
                                distance_x = self.calculate_move_x(center_x = self.frameSize[0]/2, bbox_x = bboxes[0][0])
                                if distance_x > 0.1:
                                # bbox is at left area
                                    self.servo_x.start_move_left(abs(distance_x))
                                elif distance_x < -0.1:
                                # bbox is at right area
                                    self.servo_x.start_move_right(abs(distance_x))
                            # Encode the image back from numpy to bytes
                            _, img = imencode(".jpg", img)
                            self.frame = img.tobytes()
                        except Exception as e:
                            print (f'Object detection or tracking error {e}')
                            self.frame = temp
                    else:
                        self.frame = self.buffer.getvalue()
                
                elif self.mode == 'qr':
                    # Reading QR
                    temp = self.buffer.getvalue()
                    npFrame = np.asarray(bytearray(temp))
                    if npFrame.any():
                        try:
                            img = imdecode(npFrame, 1)
                            qr = decode(img, symbols = [ZBarSymbol.QRCODE])
                            if len (qr) > 0:
                                data = (qr[0].data).decode()
                                data = json.loads(data)
                                print(data)
                            # Encode the image back from numpy to bytes
                            _, img = imencode(".jpg", img)
                            self.frame = img.tobytes()
                            print ('ok')                      
                        except Exception as e:
                            print (f'Qr detection error {e}')
                            self.frame = temp
                    else:
                        self.frame = self.buffer.getvalue()
                
                # The frame is ready. Notify all
                self.condition.notify_all()

            self.buffer.seek(0)
        return self.buffer.write(buf)

    def enable_tracking(self, detector):
        self.enableTracking = True
        self.detector = detector

    def disable_tracking(self):
        self.enableTracking = False
        self.detector = None

    def draw_box(self, img, boxes):
        if boxes.any():
            for box in boxes:
                xb, yb, widthb, heightb = box
                rectangle(img, (xb, yb), (xb+widthb, yb+heightb), color = (232,164,0), thickness = 3)
        return img

    def calculate_move_x(self, center_x, bbox_x):
        distance = (((center_x) - bbox_x)/(center_x)) * self.servo_x.maxMove
        #print (f'move distance: {distance}, bbox_x: {bbox_x}')
        return distance
