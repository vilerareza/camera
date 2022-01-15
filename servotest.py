import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)

servo1 = GPIO.PWM(11,50)

# Initialization
servo1.start(0)
print ('Waiting for 2 seconds')
time.sleep(2)

#swing = 180
dutyMin = 3
dutyMax = 11
nStep = 50

duty = dutyMin

i = 0

while (duty <= dutyMax):
    duty = dutyMin + ((dutyMax-dutyMin) / nStep)*i
    servo1.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo1.ChangeDutyCycle(0)
    time.sleep(0.1)
    i += 1

# Resolution degree
#resDegree = 2

#nSteps = swing/resDegree
#dutyStep = (dutyMax - dutyMin) / nSteps

#servo1.ChangeDutyCycle(2+(dutyMax-dutyMin)/2)
#time.sleep(0.25)
#servo1.ChangeDutyCycle(0)
#time.sleep(0.25)

#for i in range(int(nSteps)):
#    servo1.ChangeDutyCycle(dutyMin + i*dutyStep)
#    time.sleep(0.25)
#    servo1.ChangeDutyCycle(0)
#    time.sleep(0.25)

servo1.ChangeDutyCycle(dutyMin)
time.sleep(0.25)

servo1.stop()
GPIO.cleanup()

