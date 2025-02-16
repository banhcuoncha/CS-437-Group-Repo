from ac_state import AutonomousCarState

import time

class AutonomousCarMovement:
    def __init__(self, state: AutonomousCarState):
        self.state = state

        self.CALIBRATE_SAMPLES = 5
        self.CALIBRATE_STEPS = 5
        self.CALIBRATE_PAUSE = 0.1

        self.SPEED = 1

        self.CM_TIME = 0.065 # Time to travel 1cm at 1% speed
        self.BW_MULT = 35

    @property
    def px(self):
        return self.state.px

    def calibrate(self):
        # initial read
        dist_t0 = self.state.ultrasonic_read(self.CALIBRATE_SAMPLES)

        # move forward
        [self.forward(1) for _ in range(self.CALIBRATE_STEPS)]
        time.sleep(self.CALIBRATE_PAUSE)

        # middle read
        dist_t1 = self.state.ultrasonic_read(self.CALIBRATE_SAMPLES)


        calibrate_time = self.CALIBRATE_STEPS * self.CM_TIME

        init_cm_time = self.CM_TIME
        measured_cm_time = calibrate_time / (dist_t0 - dist_t1)

        # self.CM_TIME = (init_cm_time + measured_cm_time) / 2

        print(f"Calibration results. Previous: {init_cm_time}, Now: {self.CM_TIME}")

        # move backward
        [self.backward(1) for _ in range(self.CALIBRATE_STEPS)]
        time.sleep(self.CALIBRATE_PAUSE)

    def forward(self, steps):
        for i in range(steps):
            self._forward()
            self.state.update_pos_delta()

            time.sleep(0.05)
    
    def backward(self, steps):
        for i in range(steps):
            self._backward()
            self.state.update_pos_delta(True)

            time.sleep(0.05)

    def right(self):
        self._backward(10)

        self.px.set_dir_servo_angle(35)
        self._forward(25)

        self.px.set_dir_servo_angle(-35)
        self._backward(8)

        self.px.set_dir_servo_angle(0)
        self._backward(5)

        self.state.update_dir()

    def left(self):
        self._backward(8)

        self.px.set_dir_servo_angle(-35)
        self._forward(26)

        self.px.set_dir_servo_angle(35)
        self._backward(9)

        self.px.set_dir_servo_angle(0)
        self._backward(8)

        self.state.update_dir(True)
    
    def _forward(self, steps=1):
        self.px.forward(self.SPEED)
        time.sleep(abs(steps) * self.CM_TIME)
        self.px.forward(0)
    
    def _backward(self, steps=1):
        self.px.backward(self.SPEED * self.BW_MULT)
        time.sleep(abs(steps) * self.CM_TIME)
        self.px.backward(0)