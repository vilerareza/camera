import cv2 as cv
from cv2 import rectangle

cap = cv.VideoCapture(0)
detector = cv.QRCodeDetector()

class QRDetector():

    @staticmethod
    def read_qr(img):
        data, points, _ = detector.detectAndDecode(img)

        if points is not None:
            a, b, c, d = points[0]
            a_ = a.tolist()
            c_ = c.tolist()
            a_ = [int(a_[0]), int(a_[1])]
            c_ = [int(c_[0]), int(c_[1])]
            rectangle(img, a_, c_, color = (0,0,255), thickness = 2)

        return img, data