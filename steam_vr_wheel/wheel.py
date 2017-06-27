import time

import openvr

from steam_vr_wheel._double_joystick import DoubleJoystick
from steam_vr_wheel._joystick import Joystick
from steam_vr_wheel._virtualpad import VirtualPad
from steam_vr_wheel._wheel import Wheel
from steam_vr_wheel.vrcontroller import Controller

FREQUENCY = 60


def do_work(vrsystem, left_controller: Controller, right_controller: Controller, wheel: Wheel, poses):
    vrsystem.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseSeated, 0, len(poses), poses)
    left_controller.update(poses[left_controller.id.value])
    right_controller.update(poses[right_controller.id.value])
    event = openvr.VREvent_t()
    while vrsystem.pollNextEvent(event):
        hand = None
        if event.trackedDeviceIndex == left_controller.id.value:
            if event.eventType == openvr.VREvent_ButtonTouch:
                if event.data.controller.button == openvr.k_EButton_SteamVR_Touchpad:
                    wheel.set_trackpad_touch_left()
                elif  event.data.controller.button == openvr.k_EButton_SteamVR_Trigger:
                    wheel.set_trigger_touch_left()
            elif  event.eventType == openvr.VREvent_ButtonUntouch:
                if event.data.controller.button == openvr.k_EButton_SteamVR_Touchpad:
                    wheel.set_trackpad_untouch_left()
                elif  event.data.controller.button == openvr.k_EButton_SteamVR_Trigger:
                    wheel.set_trigger_untouch_left()

            hand = 'left'
        if event.trackedDeviceIndex == right_controller.id.value:

            if event.eventType == openvr.VREvent_ButtonTouch:
                if event.data.controller.button == openvr.k_EButton_SteamVR_Touchpad:
                    wheel.set_trackpad_touch_right()
                elif  event.data.controller.button == openvr.k_EButton_SteamVR_Trigger:
                    wheel.set_trigger_touch_right()
            elif  event.eventType == openvr.VREvent_ButtonUntouch:
                if event.data.controller.button == openvr.k_EButton_SteamVR_Touchpad:
                    wheel.set_trackpad_untouch_right()
                elif  event.data.controller.button == openvr.k_EButton_SteamVR_Trigger:
                    wheel.set_trigger_untouch_right()

            hand = 'right'
        if hand:
            if event.eventType == openvr.VREvent_ButtonPress:
                button = event.data.controller.button
                wheel.set_button_press(button, hand)
            if event.eventType == openvr.VREvent_ButtonUnpress:
                button = event.data.controller.button
                wheel.set_button_unpress(button, hand)
    wheel.update(left_controller, right_controller)


def get_controller_ids():
    vrsys = openvr.VRSystem()
    for i in range(openvr.k_unMaxTrackedDeviceCount):
        device_class = vrsys.getTrackedDeviceClass(i)
        if device_class == openvr.TrackedDeviceClass_Controller:
            role = vrsys.getControllerRoleForTrackedDeviceIndex(i)
            if role == openvr.TrackedControllerRole_RightHand:
                 right = i
            if role == openvr.TrackedControllerRole_LeftHand:
                 left = i
    return left, right


def main(type='wheel'):
    openvr.init(openvr.VRApplication_Background)
    vrsystem = openvr.VRSystem()
    hands_got = False
    while not hands_got:
        try:
            print('Searching for left and right hand controllers')
            left, right = get_controller_ids()
            hands_got = True
            print('left and right hands found')
        except NameError:
            pass
        time.sleep(0.1)

    left_controller = Controller(left, name='left', vrsys=vrsystem)
    right_controller = Controller(right, name='right', vrsys=vrsystem)
    if type == 'wheel':
        wheel = Wheel()
    elif type == 'joystick':
        wheel = Joystick()
    elif type == 'doublejoystick':
        wheel = DoubleJoystick()
    elif type == 'pad':
        wheel = VirtualPad()
    poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
    poses = poses_t()
    while True:
        before_work = time.time()
        do_work(vrsystem, left_controller, right_controller, wheel, poses)
        after_work = time.time()
        left = 1/FREQUENCY - (after_work - before_work)
        if left>0:
            time.sleep(left)


if __name__ == '__main__':
    main()
