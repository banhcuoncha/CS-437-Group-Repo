import asyncio
from typing import Deque

from collections import deque
import time

from picarx import Picarx
from vilib import Vilib

from ac_state_spatial import AutonomousCarSpatialDirection, AutonomousCarSpatialPosition

class AutonomousCarState:
    def __init__(self, px: Picarx):
        self.loop = asyncio.new_event_loop()

        self.px = px

        self.MAX_STEPS = 60

        self.pos: AutonomousCarSpatialPosition = (0, 0)
        self.dir: AutonomousCarSpatialDirection = AutonomousCarSpatialDirection.FRONT

        self.forward: bool = False
        self.camera_angle: float = 0

        self.goal: AutonomousCarSpatialPosition

        self.path: Deque[AutonomousCarSpatialDirection] = deque()
        self.path_steps = 0

        self.done = False

    def update_control(self, vert_dir, horiz_dir, pan_dir):
        fwd_speed = vert_dir * 30
        hrz_angle = horiz_dir * 15
        pan_del = pan_dir * 30

        self.camera_angle = min(max(self.camera_angle + pan_del, -90), 90)

        self.px.forward(fwd_speed)
        self.px.set_dir_servo_angle(hrz_angle)
        self.px.set_cam_pan_angle(self.camera_angle)

        self.forward = fwd_speed != 0
    
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

    def build_telemetry(self):
        return {
            'car_dir': self.px.dir_current_angle,
            'camera_dir': self.camera_angle,
            'forward': self.forward
        }

    def video_read(self):
        return Vilib.img
