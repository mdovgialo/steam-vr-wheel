from math import atan2

from steam_vr_wheel._virtualpad import VirtualPad, LeftTrackpadAxisDisablerMixin
from steam_vr_wheel._wheel import Wheel


class TouchWheel(LeftTrackpadAxisDisablerMixin, Wheel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wheel_image.hide()

    def _get_touch_angle(self, ctr):
        self.trackpadLX = ctr.trackpadX
        self.trackpadLY = ctr.trackpadY
        if self.trackpadLtouch:
            a = float(ctr.trackpadY)
            b = float( ctr.trackpadX)
            angle = atan2(a, b)
            return angle
        else:
            return None

    def update(self, left_ctr, right_ctr):
        VirtualPad.update(self, left_ctr, right_ctr)
        angle = self._get_touch_angle(left_ctr)
        self._wheel_update_common(angle, left_ctr, right_ctr)