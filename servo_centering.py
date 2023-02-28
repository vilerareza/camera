import time
from functools import partial
from threading import Thread, Condition
from adafruit_servokit import ServoKit

class Servo():
    # Servo parameter
    moveThread = None
    posMin = 5
    posMax = 175
    stepDegree = 2
    delayS = float(0.002)

    def __init__(self, channel = 0) -> None:
        self.kit = ServoKit(channels = 16)
        self.channel = channel
        self.condition = Condition()
        time.sleep(0.3)
        print ('servo init ok')

    def center(self, center_position = 90):
        self.kit.servo[self.channel].angle = center_position
        print(self.kit.servo[self.channel].angle)
        self.start_move(pos = center_position)


servoX = Servo(channel=0)
servoY = Servo(channel=1)

servoX.center()
servoY.center()