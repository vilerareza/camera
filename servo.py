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

    def __init__(self, center_position = 90) -> None:
        self.currentPos = center_position
        kit.servo[0].angle = self.currentPos
        time.sleep(0.3)
        print ('init ok')

    def move_left(self, distance):
        # Target position calculation
        if self.currentPos < self.posMax:
            if (self.currentPos + distance) >= self.posMax:
                targetPos = self.posMax
            else:
                targetPos = self.currentPos + distance
            # Move servo
            while True:
                if self.currentPos <= targetPos:
                    self.currentPos += 0.5
                    kit.servo[0].angle = self.currentPos
                    time.sleep(0.005)
                else:
                    break
            self.moveThread = None

        else:
            # Dont move, already at max position
            self.moveThread = None

    def start_move_left(self, distance):
        # Start the move thread
        if not self.moveThread:
            self.moveThread = Thread(target = partial(self.move_left, distance))
            self.moveThread.start()

    def move_right(self, distance):
        # Target position calculation
        if self.currentPos > self.posMin:
            if (self.currentPos - distance) <= self.posMin:
                targetPos = self.posMin
            else:
                targetPos = self.currentPos - distance
            # Move servo
            while True:
                if self.currentPos >= targetPos:
                    self.currentPos -= 0.5
                    kit.servo[0].angle = self.currentPos
                    time.sleep(0.005)
                else:
                    break
            self.moveThread = None

        else:
            # Dont move, already at min position
            self.moveThread = None

    def start_move_right(self, distance):
        # Start the move thread
        if not self.moveThread:
            self.moveThread = Thread(target = partial(self.move_right, distance))
            self.moveThread.start()
