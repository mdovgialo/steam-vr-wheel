import sys

import openvr
import time

from steam_vr_wheel.configurator import ConfiguratorApp
from steam_vr_wheel.pyvjoy.vjoydevice import VJoyDevice, HID_USAGE_SL0, HID_USAGE_SL1, HID_USAGE_X, HID_USAGE_Y, HID_USAGE_RX, HID_USAGE_RY
from steam_vr_wheel.vrcontroller import Controller
from . import PadConfig, ConfigException
import multiprocessing

BUTTONS = {}
BUTTONS['left'] = {openvr.k_EButton_ApplicationMenu: 3, openvr.k_EButton_Grip: 2, openvr.k_EButton_SteamVR_Touchpad: -1, # 4 5 6 7 8
                   openvr.k_EButton_SteamVR_Trigger: 1, openvr.k_EButton_A: 17,
                   }
BUTTONS['right'] = {openvr.k_EButton_ApplicationMenu: 11, openvr.k_EButton_Grip: 10, openvr.k_EButton_SteamVR_Touchpad: -2, # 12 13 14 15 16
                    openvr.k_EButton_SteamVR_Trigger: 9, openvr.k_EButton_A: 18
                    }

class LeftTrackpadAxisDisablerMixin:
    trackpad_left_enabled = False


class RightTrackpadAxisDisablerMixin:
    trackpad_right_enabled = False


def run_configurator():
    ConfiguratorApp().run()


class VirtualPad:
    trackpad_left_enabled = True
    trackpad_right_enabled = True
    def __init__(self):
        self.init_config()
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

        self.previous_left_zone = 0
        self.previous_right_zone = 0

    def init_config(self):
        config_loaded = False
        app_ran = False
        while not config_loaded:
            try:
                self.config = PadConfig()
                config_loaded = True
            except ConfigException as e:
                print(e)
                if not app_ran:
                    p = multiprocessing.Process(target=run_configurator)
                    p.start()
                    app_ran = True
                time.sleep(1)

    def get_trackpad_zone(self, right=True):
        if self.config.multibutton_trackpad:
            if right:
                X, Y = self.trackpadRX, self.trackpadRY
            else:
                X, Y = self.trackpadLX, self.trackpadLY
            zone = self._get_zone(X, Y) + right * 8 + 4
        else:
            zone = 0 + right * 8 + 4
        return zone

    def _get_zone(self, x, y):
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
        if button == openvr.k_EButton_SteamVR_Trigger:
            if not self.config.trigger_press_button:
                return
        try:
            btn_id = BUTTONS[hand][button]
            if btn_id is None:
                return
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
        if self.config.trigger_pre_press_button:
            self.device.set_button(31, True)

    def set_trigger_touch_right(self):
        if self.config.trigger_pre_press_button:
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

    def _check_zone_change(self, zone, prev_zone):
        # check config, return False
        if self.config.multibutton_trackpad and self.config.multibutton_trackpad_center_haptic:
            if prev_zone != zone:
                return True
        return False

    def update(self, left_ctr: Controller, right_ctr: Controller):
        self.device.set_axis(HID_USAGE_SL0, int(left_ctr.axis * 0x8000))
        self.device.set_axis(HID_USAGE_SL1, int(right_ctr.axis * 0x8000))
        self.trackpadLX = left_ctr.trackpadX
        self.trackpadLY = left_ctr.trackpadY

        haptic_pulse_strength = 1000

        left_zone = self._get_zone(self.trackpadLX, self.trackpadLY)
        crossed = self._check_zone_change(left_zone, self.previous_left_zone)
        self.previous_left_zone = left_zone
        if crossed:
            openvr.VRSystem().triggerHapticPulse(left_ctr.id, 0, haptic_pulse_strength)

        if (self.trackpadLtouch or self.config.touchpad_always_updates) and self.trackpad_left_enabled:
            self.device.set_axis(HID_USAGE_RX, int((left_ctr.trackpadX+1)/2 * 0x8000))
            self.device.set_axis(HID_USAGE_RY, int(((-left_ctr.trackpadY+1)/2) * 0x8000))
        self.trackpadRX = right_ctr.trackpadX
        self.trackpadRY = right_ctr.trackpadY

        right_zone = self._get_zone(self.trackpadRX, self.trackpadRY)
        crossed = self._check_zone_change(right_zone, self.previous_right_zone)
        self.previous_right_zone = right_zone
        if crossed:
            openvr.VRSystem().triggerHapticPulse(right_ctr.id, 0, haptic_pulse_strength)

        if (self.trackpadRtouch or self.config.touchpad_always_updates) and self.trackpad_right_enabled:
            self.device.set_axis(HID_USAGE_X, int((right_ctr.trackpadX + 1) / 2 * 0x8000))
            self.device.set_axis(HID_USAGE_Y, int(((-right_ctr.trackpadY + 1) / 2) * 0x8000))

    def edit_mode(self, left_ctr, right_ctr):
        pass