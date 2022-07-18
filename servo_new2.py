import time
from functools import partial
from threading import Thread
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
        self.center()
        time.sleep(0.3)
        print ('servo init ok')

    def center(self, center_position = 90):
       self.kit.servo[self.channel].angle = center_position

    def start_move(self, distance, pos=None):
        def move(distance, pos):

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
                        print (f'targetPos: {targetPos}')
                        print (f'pos: {self.kit.servo[self.channel].angle}')
                        time.sleep(self.delayS)
                        self.moveThread = None
                else:
                    # Dont move, already at max position
                    self.moveThread = None

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
                        print (f'targetPos: {targetPos}')
                        print (f'pos: {self.kit.servo[self.channel].angle}')
                        time.sleep(self.delayS)
                    self.moveThread = None
                else:
                    # Dont move, already at max position
                    self.moveThread = None
        # Start the move thread
        # if not self.moveThread:
        #     self.moveThread = Thread(target = partial(move_x, distance))
        #     self.moveThread.start()
        Thread(target = partial(move, distance, pos)).start()

 
def excercise():
    servoX = Servo(channel=0)
    servoY = Servo(channel=1)

    #while True:
    print ('movex')
    servoX.start_move(170)
    servoX.start_move(10)
    print ('movey')
    servoY.start_move(75)
    servoY.start_move(115)

