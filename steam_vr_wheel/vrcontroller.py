import math

import openvr
import sys

if 'DEBUG' in sys.argv:
    DEBUG = True
else:
    DEBUG = False

class Controller:
    def __init__(self, id, name='', vrsys = None):

        self.id = openvr.TrackedDeviceIndex_t(id)

        self.axis = 0
        self.x, self.y, self.z = 0, 0, 0
        self.pitch, self.yaw, self.roll = 0, 0 ,0
        self.name = name
        self.trackpadX = 0
        self.trackpadY = 0

    def update(self, pose):
        vrsys = openvr.VRSystem()
        result, pControllerState = vrsys.getControllerState(self.id)

        self.x = pose.mDeviceToAbsoluteTracking[0][3]
        self.y = pose.mDeviceToAbsoluteTracking[1][3]
        self.z = pose.mDeviceToAbsoluteTracking[2][3]

        pose_mat = pose.mDeviceToAbsoluteTracking
        try:
            self.yaw = 180 / math.pi * math.atan(pose_mat[1][0] / pose_mat[0][0])
        except ZeroDivisionError:
            self.yaw = 0
        try:
            self.pitch = 180 / math.pi * math.atan(
                -1 * pose_mat[2][0] / math.sqrt(pow(pose_mat[2][1], 2) + math.pow(pose_mat[2][2], 2)))
        except ZeroDivisionError:
            self.pitch = 0

        try:
            self.roll = 180 / math.pi * math.atan(pose_mat[2][1] / pose_mat[2][2])
        except ZeroDivisionError:
            self.roll = 0
        self.axis = pControllerState.rAxis[1].x
        self.trackpadX = pControllerState.rAxis[0].x
        self.trackpadY = pControllerState.rAxis[0].y
        self.valid = pose.bPoseIsValid
        if DEBUG:
            print(self.name, "controller axis:")
            for n, i in enumerate(pControllerState.rAxis):
                print("AXIS", n, "x:", i.x, "y:", i.y)

    def __repr__(self):
        return '<{} {} Controller position x={}, y={}, z={}, axis={} valid={}>'.format(self.name,
                                                                                       self.id,
                                                                                       self.x,
                                                                                       self.y,
                                                                                       self.z,
                                                                                       self.axis,
                                                                                       self.valid)