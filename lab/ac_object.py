import asyncio
import time

from vilib import Vilib

from ac_state import AutonomousCarState

class AutonomousCarObjectDetector:
    def __init__(self, state: AutonomousCarState):
        self.state = state

        Vilib.camera_start(vflip=False, hflip=False)
        Vilib.show_fps()
        Vilib.display(local=False, web=True)
        Vilib.face_detect_switch(True)
        Vilib.traffic_detect_switch(True)

        # measured in seconds
        self.OBSTACLE_TIMEOUT = 3

        self.has_obstacle = False

        self.last_obstacle = 0

    def detect(self) -> bool:
        ctime = time.time()

        if self._identify_object():
            self.has_obstacle = True
            self.last_obstacle = ctime
        elif ctime - self.last_obstacle > self.OBSTACLE_TIMEOUT:
            self.has_obstacle = False
        
        return self.has_obstacle
    
    def _identify_object(self) -> bool:
        # Face detection, from vilib/example/face_detection.py
        flag_face = Vilib.face_obj_parameter['n']
        flag_traffic = Vilib.traffic_sign_obj_parameter['t']

        return flag_face > 0 or flag_traffic != 'none'