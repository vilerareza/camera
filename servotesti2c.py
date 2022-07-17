from servo import Servo
import time

servo_x = Servo()

while True:
    servo_x.start_move_left(10)
    time.sleep(5)
    servo_x.start_move_right(170)
