from collections import deque
from math import pi, atan2

import numpy as np

from steam_vr_wheel._virtualpad import VirtualPad
from steam_vr_wheel.pyvjoy import HID_USAGE_Z



FULLTURN = 4


class Wheel(VirtualPad):
    def __init__(self):
        super().__init__()
        self.x = 0  # -1 0 1
        self._wheel_angles = deque(maxlen=10)
        self._wheel_angles.append(0)

    def get_unwrapped(self):
        period = 2 * pi
        angle = np.array(self._wheel_angles)
        diff = np.diff(np.array(angle))
        diff_to_correct = (diff + period / 2.) % period - period / 2.
        increment = np.cumsum(diff_to_correct - diff)
        angle[1:] += increment
        return angle[-1]

    def _vertical_wheel_update(self, left_ctr, right_ctr):
        init = left_ctr.x, left_ctr.y
        a = right_ctr.x, right_ctr.y
        deltaY = a[0] - init[0]
        deltaX = a[1] - init[1]
        angle = (atan2(deltaY, deltaX) + pi / 2)
        self._wheel_angles.append(angle)

    def _horizontal_wheel_update(self, left_ctr, right_ctr):
        init = left_ctr.x, left_ctr.z
        a = right_ctr.x, right_ctr.z
        deltaY = a[0] - init[0]
        deltaZ = a[1] - init[1]
        angle = (atan2(deltaY, deltaZ) + pi / 2)
        self._wheel_angles.append(-angle)

    def update(self, left_ctr, right_ctr):
        super().update(left_ctr, right_ctr)
        if self.config.vertical_wheel:
            self._vertical_wheel_update(left_ctr, right_ctr)
        else:
            self._horizontal_wheel_update(left_ctr, right_ctr)

        wheel_angle = self.get_unwrapped()
        self._wheel_angles[-1] = wheel_angle
        wheel_turn = wheel_angle/(2*pi)
        axisX = int((wheel_turn/FULLTURN+0.5)*0x8000)
        self.device.set_axis(HID_USAGE_Z, axisX)
