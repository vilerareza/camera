import time
from functools import partial
from threading import Thread, Condition
from adafruit_servokit import ServoKit

class Servo():
    # Servo parameter
    moveThread = None
    posMin = float(5)
    posMax = float(175) 
    stepDegree = float(1.5)
    delayS = float(0.003)

    def __init__(self, channel = 0) -> None:
        self.kit = ServoKit(channels = 16)
        self.channel = channel
        self.condition = Condition()
        self.center()
        time.sleep(0.3)
        print ('servo init ok')

    def center(self, center_position = 90):
       self.kit.servo[self.channel].angle = center_position

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
                with self.condition:
                    while self.kit.servo[self.channel].angle <= targetPos:
                        self.kit.servo[self.channel].angle += self.stepDegree
                        print (f'targetPos: {targetPos}')
                        print (f'pos: {self.kit.servo[self.channel].angle}')
                        time.sleep(self.delayS)
                    self.condition.notify_all()
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
                with self.condition:
                    while self.kit.servo[self.channel].angle >= targetPos:
                        self.kit.servo[self.channel].angle -= self.stepDegree
                        print (f'targetPos: {targetPos}')
                        print (f'pos: {self.kit.servo[self.channel].angle}')
                        time.sleep(self.delayS)
                    self.condition.notify_all()
            else:
                # Dont move, already at min position
                pass

        # with self.condition:
        #     Thread(target = partial(move, distance, pos)).start()

def excercise():
    servoX = Servo(channel=0)
    servoY = Servo(channel=1)

    def runX():
        while True:
            try:
                print ('movex 170')
                servoX.start_move(pos = 170)
                with servoX.condition:
                    servoX.condition.wait()
                print ('movex 10')
                servoX.start_move(pos = 10)
                with servoX.condition:
                    servoX.condition.wait()
            except:
                break

    def runY():
        while True:
            try:
                print ('movey 115')
                servoY.start_move(pos = 115)
                with servoY.condition:
                    servoY.condition.wait()
                print ('movey 75')
                servoY.start_move(pos = 75)
                with servoY.condition:
                    servoY.condition.wait()
            except:
                break

    Thread(target = runX).start()
    Thread(target = runY).start()

