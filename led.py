import time
import RPi.GPIO as GPIO

ledPin = 11

def led_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ledPin, GPIO.OUT)

def led_on():
    GPIO.output(ledPin,1)

def led_off():
    GPIO.output(ledPin,0)

def led_cleanup():
    GPIO.cleanup()

led_init()

while True:
    try:
        led_on()
        time.sleep(20)
        led_off()
        time.sleep(20)
    except:
        led_off()
        led_cleanup()
        print('break')
        break