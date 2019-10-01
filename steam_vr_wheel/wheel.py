import json
import os
import random
import threading
import time
from tempfile import TemporaryFile, NamedTemporaryFile

import openvr
import sys

from steam_vr_wheel._double_joystick import DoubleJoystick
from steam_vr_wheel._joystick import Joystick
from steam_vr_wheel._virtualpad import VirtualPad
from steam_vr_wheel._wheel import Wheel
from steam_vr_wheel.utils import find_hands, get_controller_ids
from steam_vr_wheel.vrcontroller import Controller
from steam_vr_wheel.configurator import run

FREQUENCY = 60

if 'DEBUG' in sys.argv:
    DEBUG = True
    FREQUENCY = 1
else:
    DEBUG = False


class ControllersLostException(Exception):
    pass


def do_work(vrsystem, left_controller: Controller, right_controller: Controller, wheel: Wheel, poses):
    vrsystem.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseSeated, 0, poses)
    left_controller.update(poses[left_controller.id.value])
    right_controller.update(poses[right_controller.id.value])
    event = openvr.VREvent_t()

    while vrsystem.pollNextEvent(event):
        if event.eventType == openvr.VREvent_TrackedDeviceActivated or event.eventType == openvr.VREvent_TrackedDeviceDeactivated:
            raise ControllersLostException

    if wheel.config.edit_mode:
        wheel.edit_mode(left_controller, right_controller)
    else:
        wheel.update(left_controller, right_controller)


def main(type='wheel'):
    manifest_dir = os.path.dirname(os.path.abspath(__file__))

    openvr.init(openvr.VRApplication_Overlay)
    vrsystem = openvr.VRSystem()
    input = openvr.VRInput()
    vr_apps = openvr.VRApplications()

    vr_apps.addApplicationManifest(os.path.join(manifest_dir, 'manifest.vrmanifest'), temporary=True)
    vr_apps.identifyApplication(os.getpid(), "mdovgialo.steamvrwheel")

    input.setActionManifestPath(os.path.join(manifest_dir, 'actions.json'))

    left_controller, right_controller = find_hands(vrsystem)

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
        before_work = time.monotonic()
        try:
            do_work(vrsystem, left_controller, right_controller, wheel, poses)
        except ControllersLostException:
            left_controller, right_controller = find_hands(vrsystem)
        after_work = time.monotonic()
        left = 1/FREQUENCY - (after_work - before_work)
        print(left)
        if left > 0:
            time.sleep(left)


if __name__ == '__main__':
    main('pad')
