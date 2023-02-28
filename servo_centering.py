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

    def start_move(self, distance = 0, pos=None):
        #def move(distance, pos):
        if pos:
            distance = pos - self.kit.servo[self.channel].angle
        if distance > 0:
            # Positive direction
            if self.kit.servo[self.channel].angle < self.posMax:
                # Still within x movement range
                # Calculate target position
                if (self.kit.servo[self.channel].angle + distance) >= self.posMax:
                    # Limit the movement to max limit.
                    targetPos = self.posMax
                else:
                    targetPos = self.kit.servo[self.channel].angle + distance
                # Move
                while self.kit.servo[self.channel].angle <= targetPos:
                    self.kit.servo[self.channel].angle += self.stepDegree
                    #print (f'targetPos: {targetPos}')
                    #print (f'pos: {self.kit.servo[self.channel].angle}')
                    time.sleep(self.delayS)
            else:
                # Dont move, already at max position
                pass

        elif distance < 0:
            # Negative direction
            if self.kit.servo[self.channel].angle > self.posMin:
                # Still within x movement range
                # Calculate target position
                if (self.kit.servo[self.channel].angle + distance) <= self.posMin:
                    # Limit the movement to min limit.
                    targetPos = self.posMin
                else:
                    targetPos = self.kit.servo[self.channel].angle + distance
                # Move
                while self.kit.servo[self.channel].angle >= targetPos:
                    self.kit.servo[self.channel].angle -= self.stepDegree
                    #print (f'targetPos: {targetPos}')
                    #print (f'pos: {self.kit.servo[self.channel].angle}')
                    time.sleep(self.delayS)
            else:
                # Dont move, already at min position
                pass


servoX = Servo(channel=0)
servoY = Servo(channel=1)

servoX.center()
servoY.center()