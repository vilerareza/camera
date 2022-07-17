import time
from functools import partial
from threading import Thread
from adafruit_servokit import ServoKit

class Servo():
    # Servo parameter
    moveThread = None
    pwm = None
    posMin = 0
    posMax = 180
    currentPos = 0
    centerPos = 90
    maxMove = 30
    kit = ServoKit(channels = 16)
    stepDegree = 0.5
    delayS = 0.005

    def __init__(self, center_position = 90) -> None:
        self.currentPos = center_position
        self.kit.servo[0].angle = self.currentPos
        time.sleep(0.3)
        print ('servo init ok')

    def start_move_left(self, distance):
        def move_left(distance):
            # Target position calculation
            if self.currentPos < self.posMax:
                if (self.currentPos + distance) >= self.posMax:
                    targetPos = self.posMax
                else:
                    targetPos = self.currentPos + distance
                # Move servo
                while True:
                    self.currentPos += self.stepDegree
                    if self.currentPos <= targetPos:
                        self.kit.servo[0].angle = self.currentPos
                        print (self.currentPos)
                        time.sleep(self.delayS)
                    else:
                        self.currentPos = targetPos
                        self.kit.servo[0].angle = self.currentPos
                        break
                self.moveThread = None
            else:
                # Dont move, already at max position
                self.moveThread = None
        # Start the move thread
        if not self.moveThread:
            self.moveThread = Thread(target = partial(move_left, distance))
            self.moveThread.start()

    def start_move_right(self, distance):
        def move_right(distance):
            # Target position calculation
            if self.currentPos > self.posMin:
                if (self.currentPos - distance) <= self.posMin:
                    targetPos = self.posMin
                else:
                    targetPos = self.currentPos - distance
                # Move servo
                while True:
                    self.currentPos -= self.stepDegree
                    if self.currentPos >= targetPos:
                        self.kit.servo[0].angle = self.currentPos
                        print (self.currentPos)
                        time.sleep(self.delayS)
                    else:
                        self.currentPos = targetPos
                        self.kit.servo[0].angle = self.currentPos
                        break
                self.moveThread = None
            else:
                # Dont move, already at min position
                self.moveThread = None
        # Start the move thread
        if not self.moveThread:
            self.moveThread = Thread(target = partial(move_right, distance))
            self.moveThread.start()
