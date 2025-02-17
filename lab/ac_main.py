from picarx import Picarx

import time

POWER = 50
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around, 
                    # < 20 backward


from ac_state import AutonomousCarState
from ac_state_spatial import AutonomousCarSpatialDirection
from ac_movement import AutonomousCarMovement
from ac_object import AutonomousCarObjectDetector
from ac_obstacle import AutonomousCarObstacleDetector

class AutonomousCar:
    def __init__(self, px: Picarx):
        self.state: AutonomousCarState = AutonomousCarState(px)

        self.movement: AutonomousCarMovement = AutonomousCarMovement(self.state)
        self.object_det: AutonomousCarObjectDetector = AutonomousCarObjectDetector(self.state)
        self.obstacle_det: AutonomousCarObstacleDetector = AutonomousCarObstacleDetector(self.state)

        self.prev_objects = False
    
    def setup(self):
        input("Press ENTER to begin calibration\n")

        self.movement.calibrate()

        input("Press ENTER to continue\n")

        self.obstacle_det.scan()

        for path_dir, path_pos in self.obstacle_det.pathfind((30, 30)):
            if path_dir == AutonomousCarSpatialDirection.FRONT:
                self.movement.forward(1)
            elif path_dir == AutonomousCarSpatialDirection.LEFT:
                self.movement.left()
            elif path_dir == AutonomousCarSpatialDirection.RIGHT:
                self.movement.right()

        # self.movement.right()

        # self.movement.forward(30)

        # self.movement.right()
        
        # self.movement.forward(30)

        # self.movement.forward(1)
        # self.movement.forward(1)
        # self.movement.forward(1)

        # time.sleep(1)

        # self.movement.backward(1)

        # self.obstacle_det.scan()

        # # find a path to (5cm right, 5cm up)
        # # returns [(relative direction 0=x, 1=y, number of cm to move), ...]
        # self.obstacle_det.pathfind(5, 5)

        # # takes 2 steps (2 * GRID_SIZE) cm forward = 10 cm
        # # the motor does not accelerate linearly so stepping in increments of 5 improves consistency
        # self.movement.forward(2)

        # TODO: in movement, write logic to turn left in place (angle 35, fwd, angle -35, bwd, angle 0, fwd)
        
        # TODO: loop: scan, follow one straight path from pathfind, then repeat loop
        # NOTE: the pathfind directions are relative to current car direction, not absolute

        pass

    def loop(self):
        objects = self.object_det.detect()

        if objects != self.prev_objects:
            print(objects)
            self.prev_objects = objects

        time.sleep(0.01)
    
    def move(self, speed):
        pass


def main():
    try:
        px = Picarx()
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
    except Exception as e:
        print('Failed to initialize PiCar')
        raise e
    
    if not px:
        return

    car = AutonomousCar(px)

    car.setup()

    while True:
        car.loop()


if __name__ == "__main__":
    main()