import time
import RPi.GPIO as GPIO

ledPin = 11

def led_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ledPin, GPIO.OUT)

def led_on():
    GPIO.output(ledPin,1)

def led_cleanup():
    GPIO.cleanup()

led_on()