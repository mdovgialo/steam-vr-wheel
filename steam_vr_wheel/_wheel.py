from collections import deque
from math import pi, atan2, sin, cos

import numpy as np
import openvr
import os
import copy

from steam_vr_wheel._virtualpad import VirtualPad, RightTrackpadAxisDisablerMixin
from steam_vr_wheel.pyvjoy import HID_USAGE_X


def check_result(result):
    if result:
        error_name = openvr.VROverlay().getOverlayErrorNameFromEnum(result)
        raise Exception("OpenVR Error:", error_name)

def print_matrix(matrix):
    l = []
    for i in range(3):
        ll = []
        for j in range(4):
            ll.append(matrix[j])
        l.append(ll)
    print(l)


def initRotationMatrix(axis, angle, matrix=None):
    # angle in radians
    if matrix is None:
        matrix = openvr.HmdMatrix34_t()
    if axis==0:
        matrix.m[0][0] = 1.0
        matrix.m[0][1] = 0.0
        matrix.m[0][2] = 0.0
        matrix.m[0][3] = 0.0
        matrix.m[1][0] = 0.0
        matrix.m[1][1] = cos(angle)
        matrix.m[1][2] = -sin(angle)
        matrix.m[1][3] = 0.0
        matrix.m[2][0] = 0.0
        matrix.m[2][1] = sin(angle)
        matrix.m[2][2] = cos(angle)
        matrix.m[2][3] = 0.0
    elif axis==1:
        matrix.m[0][0] = cos(angle)
        matrix.m[0][1] = 0.0
        matrix.m[0][2] = sin(angle)
        matrix.m[0][3] = 0.0
        matrix.m[1][0] = 0.0
        matrix.m[1][1] = 1.0
        matrix.m[1][2] = 0.0
        matrix.m[1][3] = 0.0
        matrix.m[2][0] = -sin(angle)
        matrix.m[2][1] = 0.0
        matrix.m[2][2] = cos(angle)
        matrix.m[2][3] = 0.0
    elif axis == 2:
        matrix.m[0][0] = cos(angle)
        matrix.m[0][1] = -sin(angle)
        matrix.m[0][2] = 0.0
        matrix.m[0][3] = 0.0
        matrix.m[1][0] = sin(angle)
        matrix.m[1][1] = cos(angle)
        matrix.m[1][2] = 0.0
        matrix.m[1][3] = 0.0
        matrix.m[2][0] = 0.0
        matrix.m[2][1] = 0.0
        matrix.m[2][2] = 1.0
        matrix.m[2][3] = 0.0
    return matrix


def matMul33(a, b, result=None):
    if result is None:
        result = openvr.HmdMatrix34_t()
    for i in range(3):
        for j in range(3):
            result.m[i][j] = 0.0
            for k in range(3):
                result.m[i][j] += a.m[i][k] * b.m[k][j]
    result[0][3] = b[0][3]
    result[1][3] = b[1][3]
    result[2][3] = b[2][3]
    return result


class HandsImage:
    def __init__(self, left_ctr, right_ctr):
        self._handl_closed = False
        self._handr_closed = False
        self.left_ctr = left_ctr
        self.right_ctr = right_ctr
        hand_size = 0.15

        self.vrsys = openvr.VRSystem()
        self.vroverlay = openvr.IVROverlay()

        result, self.l_ovr = self.vroverlay.createOverlay('left_hand'.encode(), 'left_hand'.encode())
        result, self.r_ovr = self.vroverlay.createOverlay('right_hand'.encode(), 'right_hand'.encode())

        check_result(self.vroverlay.setOverlayColor(self.l_ovr, 1, 1, 1))
        check_result(self.vroverlay.setOverlayColor(self.r_ovr, 1, 1, 1))
        check_result(self.vroverlay.setOverlayAlpha(self.l_ovr, 1))
        check_result(self.vroverlay.setOverlayAlpha(self.r_ovr, 1))
        check_result(self.vroverlay.setOverlayWidthInMeters(self.l_ovr, hand_size))
        check_result(self.vroverlay.setOverlayWidthInMeters(self.r_ovr, hand_size))

        this_dir = os.path.abspath(os.path.dirname(__file__))

        self.l_open_png = os.path.join(this_dir, 'media', 'hand_open_l.png')
        self.r_open_png = os.path.join(this_dir, 'media', 'hand_open_r.png')
        self.l_close_png = os.path.join(this_dir, 'media', 'hand_closed_l.png')
        self.r_close_png = os.path.join(this_dir, 'media', 'hand_closed_r.png')

        check_result(self.vroverlay.setOverlayFromFile(self.l_ovr, self.l_open_png.encode()))
        check_result(self.vroverlay.setOverlayFromFile(self.r_ovr, self.r_open_png.encode()))



        result, transform = self.vroverlay.setOverlayTransformTrackedDeviceRelative(self.l_ovr, self.left_ctr.id)
        result, transform = self.vroverlay.setOverlayTransformTrackedDeviceRelative(self.r_ovr, self.right_ctr.id)

        transform[0][0] = 1.0
        transform[0][1] = 0.0
        transform[0][2] = 0.0
        transform[0][3] = 0

        transform[1][0] = 0.0
        transform[1][1] = 1.0
        transform[1][2] = 0.0
        transform[1][3] = 0

        transform[2][0] = 0.0
        transform[2][1] = 0.0
        transform[2][2] = 1.0
        transform[2][3] = 0

        self.transform = transform

        rotate = initRotationMatrix(0, -pi / 2)
        self.transform = matMul33(rotate, self.transform)

        fn = self.vroverlay.function_table.setOverlayTransformTrackedDeviceRelative
        result = fn(self.l_ovr, self.left_ctr.id, openvr.byref(self.transform))
        result = fn(self.r_ovr, self.right_ctr.id, openvr.byref(self.transform))

        check_result(result)
        check_result(self.vroverlay.showOverlay(self.l_ovr))
        check_result(self.vroverlay.showOverlay(self.r_ovr))

    def left_grab(self):
        if not self._handl_closed:
            self.vroverlay.setOverlayFromFile(self.l_ovr, self.l_close_png.encode())
            self._handl_closed = True

    def left_ungrab(self):
        if self._handl_closed:
            self.vroverlay.setOverlayFromFile(self.l_ovr, self.l_open_png.encode())
            self._handl_closed = False

    def right_grab(self):
        if not self._handr_closed:
            self.vroverlay.setOverlayFromFile(self.r_ovr, self.r_close_png.encode())
            self._handr_closed = True

    def right_ungrab(self):
        if self._handr_closed:
            self.vroverlay.setOverlayFromFile(self.r_ovr, self.r_open_png.encode())
            self._handr_closed = False

    def hide(self):
        check_result(self.vroverlay.hideOverlay(self.l_ovr))
        check_result(self.vroverlay.hideOverlay(self.r_ovr))

    def show(self):
        check_result(self.vroverlay.showOverlay(self.l_ovr))
        check_result(self.vroverlay.showOverlay(self.r_ovr))


class SteeringWheelImage:
    def __init__(self, x=0, y=-0.4, z=-0.35, size=0.55):
        self.vrsys = openvr.VRSystem()
        self.vroverlay = openvr.IVROverlay()
        result, self.wheel = self.vroverlay.createOverlay('keyiiii'.encode(), 'keyiiii'.encode())
        check_result(result)

        check_result(self.vroverlay.setOverlayColor(self.wheel, 1, 1, 1))
        check_result(self.vroverlay.setOverlayAlpha(self.wheel, 1))
        check_result(self.vroverlay.setOverlayWidthInMeters(self.wheel, size))

        this_dir = os.path.abspath(os.path.dirname(__file__))
        wheel_img = os.path.join(this_dir, 'media', 'steering_wheel.png')

        check_result(self.vroverlay.setOverlayFromFile(self.wheel, wheel_img.encode()))


        result, transform = self.vroverlay.setOverlayTransformAbsolute(self.wheel, openvr.TrackingUniverseSeated)

        transform[0][0] = 1.0
        transform[0][1] = 0.0
        transform[0][2] = 0.0
        transform[0][3] = x

        transform[1][0] = 0.0
        transform[1][1] = 1.0
        transform[1][2] = 0.0
        transform[1][3] = y

        transform[2][0] = 0.0
        transform[2][1] = 0.0
        transform[2][2] = 1.0
        transform[2][3] = z

        self.transform = transform
        self.size = size

        fn = self.vroverlay.function_table.setOverlayTransformAbsolute
        pmatTrackingOriginToOverlayTransform = transform
        result = fn(self.wheel, openvr.TrackingUniverseSeated, openvr.byref(pmatTrackingOriginToOverlayTransform))

        check_result(result)
        check_result(self.vroverlay.showOverlay(self.wheel))

    def move(self, point, size):
        self.transform[0][3] = point.x
        self.transform[1][3] = point.y
        self.transform[2][3] = point.z
        print(point.x, point.y, point.z)
        self.size = size
        fn = self.vroverlay.function_table.setOverlayTransformAbsolute
        fn(self.wheel, openvr.TrackingUniverseSeated, openvr.byref(self.transform))
        check_result(self.vroverlay.setOverlayWidthInMeters(self.wheel, size))

    def rotate(self, angles, axis=[2,]):
        try:
            self.rotation_matrix
        except AttributeError:
            self.rotation_matrix = openvr.HmdMatrix34_t()
        if not isinstance(angles, list):
            angles = [angles, ]

        if not isinstance(axis, list):
            axis = [axis, ]

        result = copy.copy(self.transform)
        for angle, ax in zip(angles, axis):
            initRotationMatrix(ax, -angle, self.rotation_matrix)
            result = matMul33(self.rotation_matrix, result)

        fn = self.vroverlay.function_table.setOverlayTransformAbsolute
        fn(self.wheel, openvr.TrackingUniverseSeated, openvr.byref(result))

    def hide(self):
        check_result(self.vroverlay.hideOverlay(self.wheel))

    def show(self):
        check_result(self.vroverlay.showOverlay(self.wheel))



class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class GrabControllerPoint(Point):
    def __init__(self, x, y, z, id=0):
        super().__init__(x, y, z)
        self.id = id


class Wheel(RightTrackpadAxisDisablerMixin, VirtualPad):
    def __init__(self, inertia=0.95, center_speed=pi/180):
        super().__init__()
        self.vrsys = openvr.VRSystem()
        self.hands_overlay = None
        x, y, z = self.config.wheel_center
        size = self.config.wheel_size
        self._inertia = inertia
        self._center_speed = center_speed  # radians per frame, force which returns wheel to center when not grabbed
        self._center_speed_coeff = 1  # might be calculated later using game telemetry
        self.x = 0  # -1 0 1
        self._wheel_angles = deque(maxlen=10)
        self._wheel_angles.append(0)
        self._wheel_angles.append(0)
        self._snapped = False

        # radians per frame last turn speed when wheel was being held, gradually decreases after wheel is released
        self._turn_speed = 0

        self.wheel_image = SteeringWheelImage(x=x, y=y, z=z, size=size)
        self.center = Point(x, y, z)
        self.size = size
        self._grab_started_point = None
        self._wheel_grab_offset = 0

        # for manual grab:
        self._left_controller_grabbed = False
        self._right_controller_grabbed = False

    def point_in_holding_bounds(self, point):
        width = 0.10
        a = self.size/2 + width
        b = self.size/2 - width
        if self.config.vertical_wheel:
            x = point.x - self.center.x
            y = point.y - self.center.y
            z = point.z - self.center.z
        else:
            z = point.y - self.center.y
            y = point.x - self.center.x
            x = point.z - self.center.z

        if abs(z) < width:
            distance = (x**2+y**2)**0.5
            if distance < b:
                return False
            if distance < a:
                return True
        else:
            return False


    def unwrap_wheel_angles(self):
        period = 2 * pi
        angle = np.array(self._wheel_angles, dtype=float)
        diff = np.diff(angle)
        diff_to_correct = (diff + period / 2.) % period - period / 2.
        increment = np.cumsum(diff_to_correct - diff)
        angle[1:] += increment
        self._wheel_angles[-1] = angle[-1]

    def wheel_raw_angle(self, point):
        if self.config.vertical_wheel:
            a = float(point.y) - self.center.y
            b = float(point.x) - self.center.x
        else:
            a = float(point.x) - self.center.x
            b = float(point.z) - self.center.z
        angle = atan2(a, b)
        return angle

    def wheel_double_raw_angle(self, left_ctr, right_ctr):
        if self.config.vertical_wheel:
            a = left_ctr.y - right_ctr.y
            b = left_ctr.x - right_ctr.x
        else:
            a = left_ctr.x - right_ctr.x
            b = left_ctr.z - right_ctr.z
        return atan2(a, b)

    def ready_to_unsnap(self, l, r):
        d = (l.x - r.x)**2 + (l.y - r.y)**2 + (l.z - r.z)**2

        if d > self.size**2:
            return True

        dc = ((self.center.x - (l.x+r.x)/2)**2
              + (self.center.y - (l.y+r.y)/2)**2
              + (self.center.z - (l.z+r.z)/2)**2
              )
        if dc > self.size**2:
            return True

        return False

    def set_button_unpress(self, button, hand):
        super().set_button_unpress(button, hand)
        if self.config.wheel_grabbed_by_grip_toggle:
            if button == openvr.k_EButton_Grip and hand == 'left':
                self._left_controller_grabbed = False

            if button == openvr.k_EButton_Grip and hand == 'right':
                self._right_controller_grabbed = False

            if self._right_controller_grabbed and self._left_controller_grabbed:
                pass
            else:
                self._snapped = False

    def set_button_press(self, button, hand):
        super().set_button_press(button, hand)
        if button == openvr.k_EButton_Grip and hand == 'left':
            if self.config.wheel_grabbed_by_grip_toggle:
                self._left_controller_grabbed = True
            else:
                self._left_controller_grabbed = not self._left_controller_grabbed

        if button == openvr.k_EButton_Grip and hand == 'right':
            if self.config.wheel_grabbed_by_grip_toggle:
                self._right_controller_grabbed = True
            else:
                self._right_controller_grabbed = not self._right_controller_grabbed

        if self._right_controller_grabbed and self._left_controller_grabbed:
            pass
        else:
            self._snapped = False

    def _wheel_update(self, left_ctr, right_ctr):
        if self.config.wheel_grabbed_by_grip:
            left_bound, right_bound = self._left_controller_grabbed, self._right_controller_grabbed
        else: # automatic gripping
            right_bound = self.point_in_holding_bounds(right_ctr)
            left_bound = self.point_in_holding_bounds(left_ctr)
            if self.ready_to_unsnap(left_ctr, right_ctr):
                self._snapped = False

        if right_bound and left_bound and not self._snapped:
            self.is_held([left_ctr, right_ctr])

        if self._snapped:
            angle = self.wheel_double_raw_angle(left_ctr, right_ctr) + self._wheel_grab_offset
            return angle

        if right_bound:
            controller = right_ctr
            self.is_held(controller)
        elif left_bound:
            controller = left_ctr
            self.is_held(controller)
        else:
            self.is_not_held()
            return None
        angle = self.wheel_raw_angle(controller) + self._wheel_grab_offset
        return angle

    def calculate_grab_offset(self, raw_angle=None):
        if raw_angle is None:
            raw_angle = self.wheel_raw_angle(self._grab_started_point)
        self._wheel_grab_offset = self._wheel_angles[-1] - raw_angle

    def is_held(self, controller):

        if isinstance(controller, list):
            self._snapped = True
            angle = self.wheel_double_raw_angle(controller[0], controller[1])
            self.calculate_grab_offset(angle)
            self._grab_started_point = None
            return

        if self._grab_started_point is None or self._grab_started_point.id != controller.id:
            self._grab_started_point = GrabControllerPoint(controller.x, controller.y, controller.z, controller.id)
            self.calculate_grab_offset()

    def is_not_held(self):
        self._grab_started_point = None

    def inertia(self):
        if self._grab_started_point:
            self._turn_speed = self._wheel_angles[-1] - self._wheel_angles[-2]
        else:
            self._wheel_angles.append(self._wheel_angles[-1] + self._turn_speed)
            self._turn_speed *= self._inertia

    def center_force(self):
        angle = self._wheel_angles[-1]
        sign = 1
        if angle < 0:
            sign = -1
        if abs(angle) < self._center_speed * self.config.wheel_centerforce:
            self._wheel_angles[-1] = 0
            return
        self._wheel_angles[-1] -= self._center_speed * self.config.wheel_centerforce * sign

    def send_to_vjoy(self):
        wheel_turn = self._wheel_angles[-1] / (2 * pi)
        axisX = int((-wheel_turn / (self.config.wheel_degrees / 360) + 0.5) * 0x8000)
        self.device.set_axis(HID_USAGE_X, axisX)

    def render(self):
        wheel_angle = self._wheel_angles[-1]
        if self.config.vertical_wheel:
            self.wheel_image.rotate(-wheel_angle)
        else:
            self.wheel_image.rotate([-wheel_angle, np.pi / 2], [2, 0])

    def limiter(self, left_ctr, right_ctr):
        if abs(self._wheel_angles[-1])/(2*pi)>(self.config.wheel_degrees / 360)/2:
            self._wheel_angles[-1] = self._wheel_angles[-2]
            openvr.VRSystem().triggerHapticPulse(left_ctr.id, 0, 3000)
            openvr.VRSystem().triggerHapticPulse(right_ctr
                                                    .id, 0, 3000)


    def render_hands(self):
        if self._snapped:
            self.hands_overlay.left_grab()
            self.hands_overlay.right_grab()
            return
        if self._grab_started_point is None:
            self.hands_overlay.left_ungrab()
            self.hands_overlay.right_ungrab()
            return
        grab_hand_role = self.vrsys.getControllerRoleForTrackedDeviceIndex(self._grab_started_point.id)
        if  grab_hand_role == openvr.TrackedControllerRole_RightHand:
            self.hands_overlay.right_grab()
            self.hands_overlay.left_ungrab()
            return
        if grab_hand_role == openvr.TrackedControllerRole_LeftHand:
            self.hands_overlay.left_grab()
            self.hands_overlay.right_ungrab()
            return


    def _wheel_update_common(self, angle, left_ctr, right_ctr):
        if angle:
            self._wheel_angles.append(angle)

        self.unwrap_wheel_angles()

        self.inertia()
        if (not self._left_controller_grabbed) and (not self._right_controller_grabbed):
            self.center_force()
        self.limiter(left_ctr, right_ctr)
        self.send_to_vjoy()


    def update(self, left_ctr, right_ctr):
        if self.hands_overlay is None:
            self.hands_overlay = HandsImage(left_ctr, right_ctr)
        super().update(left_ctr, right_ctr)

        angle = self._wheel_update(left_ctr, right_ctr)

        self._wheel_update_common(angle, left_ctr, right_ctr)
        if self.config.wheel_show_wheel:
            self.wheel_image.show()
            self.render()
        else:
            self.wheel_image.hide()

        if self.config.wheel_show_hands:
            self.hands_overlay.show()
            self.render_hands()
        else:
            self.hands_overlay.hide()

    def move_wheel(self, right_ctr, left_ctr):
        self.center = Point(right_ctr.x, right_ctr.y, right_ctr.z)
        self.config.wheel_center = [self.center.x, self.center.y, self.center.z]
        size = ((right_ctr.x-left_ctr.x)**2 +(right_ctr.y-left_ctr.y)**2 + (right_ctr.z-left_ctr.z)**2 )**0.5*2
        self.config.wheel_size = size
        self.size = size
        self.wheel_image.move(self.center, size)



    def edit_mode(self, left_ctr, right_ctr):
        result, state_r = openvr.VRSystem().getControllerState(right_ctr.id)
        if self.hands_overlay != None:
            self.hands_overlay.show()
        if self.wheel_image != None:
            self.wheel_image.show()
        if state_r.ulButtonPressed:
            if list(reversed(bin(state_r.ulButtonPressed)[2:])).index('1') == openvr.k_EButton_SteamVR_Trigger:
                 self.move_wheel(right_ctr, left_ctr)
        super().edit_mode(left_ctr, right_ctr)
