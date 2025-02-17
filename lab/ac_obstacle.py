from typing import Tuple

import time
import math

import numpy as np
import matplotlib.pyplot as plt

from picarx import Picarx

from ac_state import AutonomousCarState
from ac_state_spatial import AutonomousCarSpatialPosition
from ac_obstacle_pathfind import AutonomousCarPathfinding

class AutonomousCarObstacleDetector:
    def __init__(self, state: AutonomousCarState):
        self.state = state

        self.MAP_SIZE = 500

        self.SERVO_RANGE = (-90, 90) # Servo movement range
        self.SERVO_STEP = 1  # Angle step size for scanning
        self.SAMPLES = 2

        self.SAFE_DISTANCE = 100  # Threshold for marking an obstacle (cm)
        self.OBSTACLE_RADIUS = 5

        self.env = np.zeros((self.MAP_SIZE, self.MAP_SIZE))  # 0 = free space, 1 = obstacle
        self.x = self.MAP_SIZE // 2 # Start at the bottom center
        self.y = 0
    
    @property
    def px(self) -> Picarx:
        return self.state.px

    def scan(self) -> None:
        self.env = np.zeros_like(self.env)

        for angle in range(self.SERVO_RANGE[0], self.SERVO_RANGE[1] + 1, self.SERVO_STEP):
            self.px.set_cam_pan_angle(angle)

            # time to stabilise servo
            time.sleep(0.1)

            distance = self.state.ultrasonic_read(self.SAMPLES)

            obstacle_coords = self._polar_to_cartesian(angle, distance)
            if obstacle_coords:
                x, y = obstacle_coords

                self.env[x, y] = 1  # Mark obstacle

                x_min = max(0, x - self.OBSTACLE_RADIUS)
                x_max = min(self.env.shape[0], x + self.OBSTACLE_RADIUS + 1)
                y_min = max(0, y - self.OBSTACLE_RADIUS)
                y_max = min(self.env.shape[1], y + self.OBSTACLE_RADIUS + 1)

                for i in range(x_min, x_max):
                    for j in range(y_min, y_max):
                        if np.sqrt((i - x)**2 + (j - y)**2) <= self.OBSTACLE_RADIUS and not self.env[i, j]:
                            self.env[i, j] = 2

        self.px.set_cam_pan_angle(0)

        self._plot()

    def pathfind(self, dest: AutonomousCarSpatialPosition):
        # dest is in world coordinates - convert to relative
        dest_w_x, dest_w_y = dest
        pos_w_x, pos_w_y = self.state.pos
        
        # rel_w is the relative offset from car, in world coordinates
        rel_w = (dest_w_x - pos_w_x, dest_w_y - pos_w_y)

        # rel_l is the relative offset from car, in local coordinates (matches rotation)
        rel_l_x, rel_l_y = self.state.dir.transform(rel_w)

        # rel_m is the local coordinates in numpy
        rel_m = (int(rel_l_x + self.x), int(rel_l_y + self.y))

        pf = AutonomousCarPathfinding()
        return pf.pathfind(self.env, (self.x, self.y), rel_m)

    def _plot(self):
        plt.imshow(self.env.T, cmap="gray_r", origin="lower")
        plt.scatter(self.x, self.y, c="red", marker="x")

        plt.xticks(np.arange(0, self.env.shape[0] + 1, 10))
        plt.yticks(np.arange(0, self.env.shape[1] + 1, 10))

        plt.title("PicarX Environment Map")
        plt.savefig("environment_map.png")


    def _polar_to_cartesian(self, angle, distance) -> Tuple[int, int]:
        if distance > self.SAFE_DISTANCE or distance <= 0:
            return None  # Ignore invalid or far readings

        angle_rad = math.radians(angle)

        x = int(self.x + (distance * math.sin(angle_rad)))
        y = int(self.y + (distance * math.cos(angle_rad)))

        if 0 <= x < self.env.shape[0] and 0 <= y < self.env.shape[1]:
            return x, y

        return None