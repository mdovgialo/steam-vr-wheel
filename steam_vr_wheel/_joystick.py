import sys

import openvr

from steam_vr_wheel.pyvjoy.vjoydevice import HID_USAGE_X, HID_USAGE_Y, HID_USAGE_Z, HID_USAGE_RX, HID_USAGE_RY, HID_USAGE_RZ
from steam_vr_wheel._virtualpad import VirtualPad, RightTrackpadAxisDisablerMixin, LeftTrackpadAxisDisablerMixin

class Throttle():

    def __init__(self, size=0.3, inverted = False):
        self.throttle_z = 0
        self.throttle_real_world_z = 0
        self.throttle_at_real_world_z = 0
        self.throttle_relative_zeroed = False
        self.throttle_grabbed = False
        self.invertion = -1 if inverted else 1
        self.size = size

    @property
    def x(self):
        return self.throttle_z/self.size

    def grabbed(self):
        self.throttle_grabbed = True

    def ungrabbed(self):
        self.throttle_grabbed = False

    def update(self, value,):
        if self.throttle_grabbed:
            if not self.throttle_relative_zeroed:
                self.throttle_real_world_z = value * self.invertion
                self.throttle_at_real_world_z = self.throttle_z
                self.throttle_relative_zeroed = True
            else:
                self.throttle_z = self.invertion * value - self.throttle_real_world_z + self.throttle_at_real_world_z
                if self.throttle_z<0:
                    self.throttle_z = 0
                elif self.throttle_z>self.size:
                    self.throttle_z = self.size

        else:
            self.throttle_relative_zeroed = False

class Joystick(RightTrackpadAxisDisablerMixin, LeftTrackpadAxisDisablerMixin, VirtualPad):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.throttle_z = Throttle(size=0.3, inverted=True)
        self.throttle_y = Throttle(size=0.2)
        self.throttle_x = Throttle(size=90)

    def set_button_press(self, button, hand):
        super().set_button_press(button, hand)
        if button == openvr.k_EButton_Grip and hand == 'left':
            self.throttle_z.grabbed()
            self.throttle_x.grabbed()
            self.throttle_y.grabbed()

    def set_button_unpress(self, button, hand):
        super().set_button_unpress(button, hand)
        if button == openvr.k_EButton_Grip and hand == 'left':
            self.throttle_z.ungrabbed()
            self.throttle_x.ungrabbed()
            self.throttle_y.ungrabbed()


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

        self.throttle_z.update(left_ctr.z)
        self.throttle_y.update(left_ctr.y)
        self.throttle_x.update(left_ctr.yaw)

        self.device.set_axis(HID_USAGE_RZ, int(self.throttle_z.x * 0x8000))
        self.device.set_axis(HID_USAGE_RY, int(self.throttle_y.x  * 0x8000))
        self.device.set_axis(HID_USAGE_RX, int(self.throttle_x.x  * 0x8000))
