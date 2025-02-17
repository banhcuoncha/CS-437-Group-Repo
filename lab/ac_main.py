from picarx import Picarx

import time
from collections import deque

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
    
    def setup(self):
        input("Press ENTER to begin calibration\n")
        print("Calibrating...")

        self.movement.calibrate()

        input("Press ENTER to continue\n")
        print("Continuing to event loop...")

        self.state.goal = (30, 30)

    def loop(self):
        # navigation
        if not self.state.done and (not len(self.state.path) or self.state.path_steps >= self.state.MAX_STEPS):
            # reset path
            self.state.path_steps = 0
            self.state.path.clear()

            # update path
            self.obstacle_det.scan()
            self.state.path = deque([dir for dir, _ in self.obstacle_det.pathfind(self.state.goal)])

            # end current loop - wait 1 second to stabilize for object detection
            time.sleep(1)
            return
        
        objects = self.object_det.detect()

        if objects:
            print("Objects detected! Stopping.")

            # end current loop
            return
        
        if len(self.state.path):
            path_dir = self.state.path.popleft()

            if path_dir == AutonomousCarSpatialDirection.FRONT:
                self.movement.forward(1)
            elif path_dir == AutonomousCarSpatialDirection.LEFT:
                self.movement.left()
            elif path_dir == AutonomousCarSpatialDirection.RIGHT:
                self.movement.right()

            if not len(self.state.path):
                # now empty -> done
                self.state.done = True
            
            time.sleep(0.02)


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