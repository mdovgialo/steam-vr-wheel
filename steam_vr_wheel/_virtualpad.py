import sys

import openvr

from steam_vr_wheel.pyvjoy.vjoydevice import VJoyDevice, HID_USAGE_SL0, HID_USAGE_SL1, HID_USAGE_X, HID_USAGE_Y, HID_USAGE_RX, HID_USAGE_RY
from steam_vr_wheel.vrcontroller import Controller

BUTTONS = {}
BUTTONS['left'] = {openvr.k_EButton_ApplicationMenu: 3, openvr.k_EButton_Grip: 2, openvr.k_EButton_SteamVR_Touchpad: -1, # 4 5 6 7 8
                   openvr.k_EButton_SteamVR_Trigger: 1
                   }
BUTTONS['right'] = {openvr.k_EButton_ApplicationMenu: 11, openvr.k_EButton_Grip: 10, openvr.k_EButton_SteamVR_Touchpad: -2, # 12 13 14 15 16
                    openvr.k_EButton_SteamVR_Trigger: 9,
                    }

class LeftTrackpadAxisDisablerMixin:
    def set_trackpad_touch_left(self):
        self.trackpadLtouch = False

    def set_trackpad_untouch_left(self):
        self.trackpadLtouch = False

class RightTrackpadAxisDisablerMixin:
    def set_trackpad_touch_right(self):
        self.trackpadRtouch = False

    def set_trackpad_untouch_right(self):
        self.trackpadRtouch = False


class VirtualPad:
    def __init__(self):
        device = 1
        try:
            device = int(sys.argv[1])
        except:
            print('selecting default')
            pass
        self.device = VJoyDevice(device)
        self.trackpadRtouch = False
        self.trackpadLtouch = False
        self.trackpadLX = 0
        self.trackpadLY = 0
        self.trackpadRX = 0
        self.trackpadRY = 0
        self.sliderL = 0
        self.sliderR = 0

    def get_trackpad_zone(self, right=True):
        if right:
            X, Y = self.trackpadRX, self.trackpadRY
        else:
            X, Y = self.trackpadLX, self.trackpadLY
        zone = self._get_zone(X, Y) + right * 8 + 4
        print(zone)
        return zone

    def _get_zone(self, x, y):
        print(x, y)
        if (x**2 + y**2)**0.5 <0.3:
            return 0
        if x>y:
            if y>(-x):
                return 1
            else:
                return 2
        if x<y:
            if y<(-x):
                return 3
            else:
                return 4

    def pressed_left_trackpad(self):
        btn_id = self.get_trackpad_zone(right=False)
        self.device.set_button(btn_id, True)

    def unpressed_left_trackpad(self):
        for btn_id in [4, 5, 6, 7, 8]:
            try:
                self.device.set_button(btn_id, False)
            except NameError:
                pass

    def pressed_right_trackpad(self):
        btn_id = self.get_trackpad_zone(right=True)
        self.device.set_button(btn_id, True)

    def unpressed_right_trackpad(self):
        for btn_id in [12, 13, 14, 15, 16]:
            try:
                self.device.set_button(btn_id, False)
            except NameError:
                pass

    def set_button_press(self, button, hand):
        try:
            btn_id = BUTTONS[hand][button]
            if btn_id == -1:
                self.pressed_left_trackpad()
            elif btn_id == -2:
                self.pressed_right_trackpad()
            else:
                self.device.set_button(btn_id, True)
        except KeyError:
            pass

    def set_button_unpress(self, button, hand):
        try:
            btn_id = BUTTONS[hand][button]
            if btn_id == -1:
                self.unpressed_left_trackpad()
            elif btn_id == -2:
                self.unpressed_right_trackpad()
            else:
                self.device.set_button(btn_id, False)
        except KeyError:
            pass

    def set_trigger_touch_left(self):
        self.device.set_button(31, True)

    def set_trigger_touch_right(self):
        self.device.set_button(32, True)

    def set_trigger_untouch_left(self):
        self.device.set_button(31, False)

    def set_trigger_untouch_right(self):
        self.device.set_button(32, False)

    def set_trackpad_touch_left(self):
        self.trackpadLtouch = True

    def set_trackpad_touch_right(self):
        self.trackpadRtouch = True

    def set_trackpad_untouch_left(self):
        self.trackpadLtouch = False

    def set_trackpad_untouch_right(self):
        self.trackpadRtouch = False

    def update(self, left_ctr: Controller, right_ctr: Controller):
        self.device.set_axis(HID_USAGE_SL0, int(left_ctr.axis * 0x8000))
        self.device.set_axis(HID_USAGE_SL1, int(right_ctr.axis * 0x8000))
        self.trackpadLX = left_ctr.trackpadX
        self.trackpadLY = left_ctr.trackpadY
        if self.trackpadLtouch:
            self.device.set_axis(HID_USAGE_X, int((left_ctr.trackpadX+1)/2 * 0x8000))
            self.device.set_axis(HID_USAGE_Y, int(((-left_ctr.trackpadY+1)/2) * 0x8000))
        self.trackpadRX = right_ctr.trackpadX
        self.trackpadRY = right_ctr.trackpadY
        if self.trackpadRtouch:
            self.device.set_axis(HID_USAGE_RX, int((right_ctr.trackpadX + 1) / 2 * 0x8000))
            self.device.set_axis(HID_USAGE_RY, int(((-right_ctr.trackpadY + 1) / 2) * 0x8000))