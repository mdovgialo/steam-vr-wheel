import openvr

openvr.init(openvr.VRApplication_Background)

while True:
    print()
    for c in range(16):
        result, pControllerState, pTrackedDevicePose = openvr.VRSystem().getControllerStateWithPose(c,
                                                                                              openvr.TrackingUniverseSeated,
                                                                                       )
        print(pControllerState.rAxis[0], dir(pControllerState.rAxis[0]))
        for i in pControllerState.rAxis:
            print(i.x, i.y)

