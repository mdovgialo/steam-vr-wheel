import sys

from steam_vr_wheel.pyvjoy.vjoydevice import HID_USAGE_X, HID_USAGE_Y, HID_USAGE_Z, HID_USAGE_RX, HID_USAGE_RY, HID_USAGE_RZ
from steam_vr_wheel._virtualpad import VirtualPad, RightTrackpadAxisDisablerMixin, LeftTrackpadAxisDisablerMixin


class DoubleJoystick(RightTrackpadAxisDisablerMixin, LeftTrackpadAxisDisablerMixin, VirtualPad):
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
        axisZ = (-right_ctr.pitch+90)/180


        axisRX = (-left_ctr.yaw + 90) / 180
        if left_ctr.roll>=0:
            axisRY = 90 - left_ctr.roll
        else:
            axisRY = -(90 + left_ctr.roll)
        axisRY = -(axisRY + 90)/180 + 1
        axisRZ = (-left_ctr.pitch+90)/180

        self.device.set_axis(HID_USAGE_X, int(axisX * 0x8000))
        self.device.set_axis(HID_USAGE_Y, int(axisY * 0x8000))
        self.device.set_axis(HID_USAGE_Z, int(axisZ * 0x8000))

        self.device.set_axis(HID_USAGE_RX, int(axisRX * 0x8000))
        self.device.set_axis(HID_USAGE_RY, int(axisRY * 0x8000))
        self.device.set_axis(HID_USAGE_RZ, int(axisRZ * 0x8000))
