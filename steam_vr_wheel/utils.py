import time

import openvr

from steam_vr_wheel.vrcontroller import Controller


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

def find_hands(vrsystem):
    hands_got = False
    while not hands_got:
        try:
            print('Searching for left and right hand controllers')
            left, right = get_controller_ids()
            hands_got = True
            for i in range(4):
                openvr.VRSystem().triggerHapticPulse(right, 0, 3000)
                time.sleep(0.2)
            print('left and right hands found')
        except NameError:
            pass
        time.sleep(0.1)

    left_controller = Controller(left, name='left', vrsys=vrsystem)
    right_controller = Controller(right, name='right', vrsys=vrsystem)
    return left_controller, right_controller