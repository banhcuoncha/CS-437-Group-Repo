from typing import Deque

from collections import deque
import time

from picarx import Picarx

from ac_state_spatial import AutonomousCarSpatialDirection, AutonomousCarSpatialPosition

class AutonomousCarState:
    def __init__(self, px: Picarx):
        self.px = px

        self.MAX_STEPS = 15

        self.pos: AutonomousCarSpatialPosition = (0, 0)
        self.dir: AutonomousCarSpatialDirection = AutonomousCarSpatialDirection.FRONT

        self.goal: AutonomousCarSpatialPosition

        self.path: Deque[AutonomousCarSpatialDirection] = deque()
        self.path_steps = 0

        self.done = False
    
    def update_dir(self, ccw=False):
        if not ccw:
            self.dir = self.dir.cw()
        else:
            self.dir = self.dir.ccw()

    def update_pos_delta(self, backward=False):
        x, y = self.pos
        dx, dy = self.dir.vec()

        if backward:
                dx *= -1; dy *= -1

        self.pos = (x + dx, y + dy)

        print(f"Position is now {self.pos}")

    def ultrasonic_read(self, n):
        return sum([self._ultrasonic_read_one() for _ in range(n)]) / n

    def _ultrasonic_read_one(self):
        time.sleep(0.01)
        return self.px.ultrasonic.read()