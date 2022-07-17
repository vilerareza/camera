import time
from functools import partial
from threading import Thread
from adafruit_servokit import ServoKit

class Servo():
    # Servo parameter
    moveThread = None
    #posParam = {'posXMin':0, 'posXMax':180, 'posYMin':0, 'posYMax': 180, 'stepDegree':0.5, 'delayS':0.005}
    posXMin = float(5)
    posXMax = float(175) 
    posYMin = float(5)
    posYMax =  float(175) 
    stepDegree = float(1.5)
    delayS = float(0.003)

    def __init__(self) -> None:
        self.kit = ServoKit(channels = 16)
        self.center()
        time.sleep(0.3)
        print ('servo init ok')

    def center(self, center_position = 90):
       self.kit.servo[0].angle = center_position
       self.kit.servo[1].angle = center_position

    def start_move_x(self, distance):
        def move_x(distance):
            if distance > 0:
                # Positive direction
                if self.kit.servo[0].angle < self.posXMax:
                    # Still within x movement range
                    # Calculate target position
                    if (self.kit.servo[0].angle + distance) >= self.posXMax:
                        # Limit the movement to max limit.
                        targetPos = self.posXMax
                    else:
                        targetPos = self.kit.servo[0].angle + distance
                    # Move X
                    while self.kit.servo[0].angle <= targetPos:
                        self.kit.servo[0].angle += self.stepDegree
                        print (f'targetPos: {targetPos}')
                        print (f'posX: {self.kit.servo[0].angle}')
                        time.sleep(self.delayS)

                        self.moveThread = None
                else:
                    # Dont move, already at max position
                    self.moveThread = None

            elif distance < 0:
                # Negative direction
                if self.kit.servo[0].angle > self.posXMin:
                    # Still within x movement range
                    # Calculate target position
                    if (self.kit.servo[0].angle + distance) <= self.posXMin:
                        # Limit the movement to max limit.
                        targetPos = self.posXMin
                    else:
                        targetPos = self.kit.servo[0].angle + distance
                    # Move X
                    while self.kit.servo[0].angle >= targetPos:
                        self.kit.servo[0].angle -= self.stepDegree
                        print (f'targetPos: {targetPos}')
                        print (f'posX: {self.kit.servo[0].angle}')
                        time.sleep(self.delayS)

                    self.moveThread = None
                else:
                    # Dont move, already at max position
                    self.moveThread = None
        # Start the move thread
        # if not self.moveThread:
        #     self.moveThread = Thread(target = partial(move_x, distance))
        #     self.moveThread.start()
        Thread(target = partial(move_x, distance)).start()

    def start_move_y(self, distance):
        def move_y(distance):
            if distance > 0:
                # Positive direction
                if self.kit.servo[1].angle < self.posXMax:
                    # Still within x movement range
                    # Calculate target position
                    if (self.kit.servo[1].angle + distance) >= self.posXMax:
                        # Limit the movement to max limit.
                        targetPos = self.posXMax
                    else:
                        targetPos = self.kit.servo[1].angle + distance
                    # Move X
                    while self.kit.servo[1].angle <= targetPos:
                        self.kit.servo[1].angle += self.stepDegree
                        print (f'targetPos: {targetPos}')
                        print (f'posX: {self.kit.servo[1].angle}')
                        time.sleep(self.delayS)

                        self.moveThread = None
                else:
                    # Dont move, already at max position
                    self.moveThread = None

            elif distance < 0:
                # Negative direction
                if self.kit.servo[1].angle > self.posXMin:
                    # Still within x movement range
                    # Calculate target position
                    if (self.kit.servo[1].angle + distance) <= self.posXMin:
                        # Limit the movement to max limit.
                        targetPos = self.posXMin
                    else:
                        targetPos = self.kit.servo[1].angle + distance
                    # Move X
                    while self.kit.servo[1].angle >= targetPos:
                        self.kit.servo[1].angle -= self.stepDegree
                        print (f'targetPos: {targetPos}')
                        print (f'posX: {self.kit.servo[1].angle}')
                        time.sleep(self.delayS)

                    self.moveThread = None
                else:
                    # Dont move, already at max position
                    self.moveThread = None
        # Start the move thread
        # if not self.moveThread:
        #     self.moveThread = Thread(target = partial(move_y, distance))
        #     self.moveThread.start()
        Thread(target = partial(move_y, distance)).start()

    def excercise(self):
        #while True:
        self.start_move_x(85)
        self.start_move_y(30)

