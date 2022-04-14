from threading import Condition, Thread
import time
import RPi.GPIO as GPIO
from functools import partial

class Servo():
    # Servo parameter
    moveThread = None
    pwm = None
    posMin = 3
    posMax = 11
    servo_center_pos = 7
    pos = servo_center_pos  # Current position of the servo, initialized to center
    nStep = 50
    step = (posMax-posMin) / nStep
    servo_max_move = 1.7

    def __init__(self, gpio = 11) -> None:
        self.gpio = gpio
        
    def servo_start(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.gpio, GPIO.OUT)
        self.pwm = GPIO.PWM(self.gpio,50)
        self.pwm.start(0)
        time.sleep(0.1)
        
    def servo_close(self):
        # Servo cleanup
        self.pwm.stop()
        GPIO.cleanup()
        self.pwm = None

    def servo_init(self):
        self.servo_start()
        self.pwm.ChangeDutyCycle(self.servo_center_pos)
        time.sleep(0.3)
        self.pwm.ChangeDutyCycle(0)
        time.sleep(0.3)
        print ('init ok')
        self.servo_close()

    def move_left(self, distance):
        # Start servo
        self.servo_start()
        # Move servo
        if self.pos < self.posMax:
            if (self.pos + distance) >= self.posMax:
                self.pos = self.posMax
            else:
                self.pos += distance
            #print (f'pos: {pos}, step: {step}')
            self.pwm.ChangeDutyCycle(pos)
            time.sleep(0.1)
            self.pwm.ChangeDutyCycle(0)
            time.sleep(0.1)
        self.moveThread = None
        # Stop servo
        self.servo_close()

    def start_move_left(self, distance):
        # Start the move thread
        if not self.moveThread:
            self.moveThread = Thread(target = partial(self.move_left, distance))
            self.moveThread.start()

    def move_right(self, distance):
        # Start servo
        self.servo_start()
        # Move servo
        if self.pos > self.posMin:
            if (self.pos - distance) <= self.posMin:
                self.pos = self.posMin
            else:
                self.pos -= distance
            #print (f'pos: {pos}, step: {step}')
            self.pwm.ChangeDutyCycle(self.pos)
            time.sleep(0.1)
            self.pwm.ChangeDutyCycle(0)
            time.sleep(0.1)
        self.moveThread = None
        # Stop servo
        self.servo_close()

    def start_move_right(self, distance):
        # Start the move thread
        if not self.moveThread:
            self.moveThread = Thread(target = partial(self.move_right, distance))
            self.moveThread.start()
