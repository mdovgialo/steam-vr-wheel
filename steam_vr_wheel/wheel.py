from math import pi, atan2

import openvr
from .pyvjoy.vjoydevice import VJoyDevice, HID_USAGE_X, HID_USAGE_RX, HID_USAGE_RY
import time


FREQUENCY = 60
BUTTONS = {}
BUTTONS['left'] = {openvr.k_EButton_ApplicationMenu: 1, openvr.k_EButton_Grip: 2, openvr.k_EButton_SteamVR_Touchpad: 3,
                   }
BUTTONS['right'] = {openvr.k_EButton_ApplicationMenu: 5, openvr.k_EButton_Grip: 6, openvr.k_EButton_SteamVR_Touchpad: 7,
                   }


class Wheel:
    def __init__(self):
        self.device = VJoyDevice(1)
        self.x = 0  # -1 0 1
        self.brake = 0 # 0 1
        self.throttle = 0 # 0 1

    def update(self, left_ctr, right_ctr):
        init = left_ctr.x, left_ctr.y
        a = right_ctr.x, right_ctr.y
        deltaY = a[0] - init[0]
        deltaX = a[1] - init[1]
        angle = (atan2(deltaY, deltaX)+pi/2)/pi
        axisX = int((angle/2+0.5)*0x8000)
        self.device.set_axis(HID_USAGE_X, axisX)
        self.device.set_axis(HID_USAGE_RX, int(left_ctr.axis*0x8000))
        self.device.set_axis(HID_USAGE_RY, int(right_ctr.axis*0x8000))

    def set_button_press(self, button, hand):
        try:
            btn_id = BUTTONS[hand][button]
            self.device.set_button(btn_id, True)
        except KeyError:
            pass

    def set_button_unpress(self, button, hand):
        try:
            btn_id = BUTTONS[hand][button]
            self.device.set_button(btn_id, False)
        except KeyError:
            pass
class Controller:
    def __init__(self, id, name='', vrsys = None):

        self.id = openvr.TrackedDeviceIndex_t(id)
        if vrsys is None:
            vrsys = openvr.IVRSystem()
        self._vrsys = vrsys
        self.axis = 0
        self.x, self.y, self.z = 0, 0 , 0
        self.name = name
        self.update()

    def update(self, event=None, pose=None):

        if event:
            if event.eventType == openvr.VREvent_ButtonPress:
                print(event.data)
                #self.axis = event.data.k_EButton_Axis0
        else:
            result, pControllerState, pTrackedDevicePose = self._vrsys.getControllerStateWithPose(self.id,
                                                                                                  openvr.TrackingUniverseSeated
                                                                                                  )
            self.x = pTrackedDevicePose.mDeviceToAbsoluteTracking[0][3]
            self.y = pTrackedDevicePose.mDeviceToAbsoluteTracking[1][3]
            self.z = pTrackedDevicePose.mDeviceToAbsoluteTracking[2][3]
            self.axis = pControllerState.rAxis[0].x
            self.valid = pTrackedDevicePose.bPoseIsValid

    def __repr__(self):
        return '<{} {} Controller position x={}, y={}, z={}, axis={} valid={}>'.format(self.name,
                                                                                       self.id,
                                                                            self.x,
                                                                            self.y,
                                                                            self.z,
                                                                            self.axis,
                                                                            self.valid)

def do_work(vrsystem, left_controller: Controller, right_controller: Controller, wheel: Wheel, poses):
    vrsystem.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0, len(poses), poses)
    left_controller.update(pose=poses[left_controller.id.value])
    right_controller.update(pose=poses[right_controller.id.value])
    print(left_controller)
    print(right_controller)
    wheel.update(left_controller, right_controller)
    event = openvr.VREvent_t()
    while vrsystem.pollNextEvent(event):
        #print(vrsystem.getEventTypeNameFromEnum(event.eventType))
        dix = openvr.TrackedDeviceIndex_t(event.trackedDeviceIndex)
        role = vrsystem.getControllerRoleForTrackedDeviceIndex(event.trackedDeviceIndex)
        hand = None
        if role == openvr.TrackedControllerRole_RightHand:
            hand = 'right'
        if role == openvr.TrackedControllerRole_LeftHand:
            hand = 'left'
        if event.eventType == openvr.VREvent_ButtonPress:
            button = event.data.controller.button
            wheel.set_button_press(button, hand)
        if event.eventType == openvr.VREvent_ButtonUnpress:
            button = event.data.controller.button
            wheel.set_button_unpress(button, hand)
   # print(left_controller)
    #print(right_controller)



def get_controller_ids(poses):
    vrsys = openvr.IVRSystem()
    for i in range(len(poses)):
        device_class = vrsys.getTrackedDeviceClass(i)
        print(device_class)
        if device_class == openvr.TrackedDeviceClass_Controller:
            role = openvr.IVRSystem().getControllerRoleForTrackedDeviceIndex(i)
            if role == openvr.TrackedControllerRole_RightHand:
                 right = i
            if role == openvr.TrackedControllerRole_LeftHand:
                 left = i
    return left, right


def main():
    openvr.init(openvr.VRApplication_Background)
    poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
    poses = poses_t()
    vrsystem = openvr.VRSystem()
    vrsystem.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseSeated, 0, len(poses), poses)
    left, right = get_controller_ids(poses)
    left_controller = Controller(left, name='left', vrsys=vrsystem)
    right_controller = Controller(right, name='right', vrsys=vrsystem)
    wheel = Wheel()
    while True:
        before_work = time.time()
        do_work(vrsystem, left_controller, right_controller, wheel, poses)
        after_work = time.time()
        left = 1/FREQUENCY - (after_work - before_work)
        if left>0:
            time.sleep(left)


if __name__ == '__main__':
    main()
