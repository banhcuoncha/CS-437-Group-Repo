import asyncio
from picarx import Picarx

from ac_web import AutonomousCarWeb

POWER = 50
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around, 
                    # < 20 backward


from ac_state import AutonomousCarState
from ac_state_spatial import AutonomousCarSpatialDirection
# from ac_movement import AutonomousCarMovement
from ac_video import AutonomousCarVideo
from ac_obstacle import AutonomousCarObstacleDetector

class AutonomousCar:
    def __init__(self, px: Picarx):
        self.state: AutonomousCarState = AutonomousCarState(px)

        # self.movement: AutonomousCarMovement = AutonomousCarMovement(self.state)
        self.video: AutonomousCarVideo = AutonomousCarVideo(self.state)
        self.obstacle_det: AutonomousCarObstacleDetector = AutonomousCarObstacleDetector(self.state)

        self.web: AutonomousCarWeb = AutonomousCarWeb(self.state)
        self.web.start()
    
    def setup(self):
        # self.state.loop.create_task(self.movement.calibrate())

        # 90, 30
        # 60, 45
        # self.state.goal = (90, 30)
        pass

    def start_loop(self):
        self.state.loop.create_task(self._loop())

        self.state.loop.run_forever()

    async def _loop(self):
        while True:
            self._loop_one()

    def _loop_one(self):
        pass
        # # navigation
        # if not self.state.done and (not len(self.state.path) or self.state.path_steps >= self.state.MAX_STEPS):
        #     # reset path
        #     self.state.path_steps = 0
        #     self.state.path.clear()

        #     # update path
        #     self.obstacle_det.scan()
        #     self.state.path = deque([dir for dir, _ in self.obstacle_det.pathfind(self.state.goal)])

        #     # end current loop - wait 1 second to stabilize for object detection
        #     time.sleep(1)
        #     return
        
        # objects = self.video.detect()

        # if objects:
        #     print("Objects detected! Stopping.")

        #     # end current loop
        #     return
        
        # if len(self.state.path):
        #     path_dir = self.state.path.popleft()

        #     if path_dir == AutonomousCarSpatialDirection.FRONT:
        #         self.movement.forward(1)
        #     elif path_dir == AutonomousCarSpatialDirection.LEFT:
        #         self.movement.left()
        #     elif path_dir == AutonomousCarSpatialDirection.RIGHT:
        #         self.movement.right()

        #     self.state.path_steps += 1

        #     if not len(self.state.path):
        #         # now empty -> done
        #         self.state.done = True
            
        #     time.sleep(0.02)


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
    car.start_loop()


if __name__ == "__main__":
    main()