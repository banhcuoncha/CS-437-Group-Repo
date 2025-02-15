from picarx import Picarx
import time
import random

'''
What you need to do: Write a program that uses the ultrasonic sensor to 
detect obstacles that come within several centimeters of your car's front
bumper. When your car gets within that obstacle, it should stop, choose 
another random direction, back up and turn, and then move forward in the new direction.
'''

''' 
This code is based on Sunfounder's original "avoiding_obstacles.py"
'''

POWER = 40
#SafeDistance = 40   # > 40 safe
DangerDistance = 30 # > 20 && < 40 turn, 
                    # < 20 backward

def main():
    try:
        px = Picarx()
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
       
        while True:
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ",distance)
            # if no obstacles
            if distance >= DangerDistance:
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            # #if the distance is of concern
            # elif distance >= DangerDistance:
            #     px.set_dir_servo_angle(30)
            #     px.forward(POWER)
            #     time.sleep(0.1)
            ## if less than danger distance
            else:
                px.stop()
                time.sleep(0.5)
                back_angle = random.choice([-30, 30])
                px.set_dir_servo_angle(back_angle)
                px.backward(POWER-20)
                time.sleep(0.5)

    finally:
        px.forward(0)


if __name__ == "__main__":
    main()