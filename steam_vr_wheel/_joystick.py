import sys

from steam_vr_wheel.pyvjoy.vjoydevice import HID_USAGE_X, HID_USAGE_Y, HID_USAGE_Z
from steam_vr_wheel._virtualpad import VirtualPad, LeftTrackpadAxisDisablerMixin


class Joystick(LeftTrackpadAxisDisablerMixin, VirtualPad):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0

    def update(self, left_ctr, right_ctr):
        super().update(left_ctr, right_ctr)
        axisX = (-right_ctr.yaw + 90)/180
        if right_ctr.roll>=0:
            axisY = 90 - right_ctr.roll
        else:
            axisY = -(90 + right_ctr.roll)
        axisY = -(axisY + 90)/180 + 1
        axisZ = (-right_ctr.pitch+90)/180
        self.device.set_axis(HID_USAGE_X, int(axisX * 0x8000))
        self.device.set_axis(HID_USAGE_Y, int(axisY * 0x8000))
        self.device.set_axis(HID_USAGE_Z, int(axisZ * 0x8000))
