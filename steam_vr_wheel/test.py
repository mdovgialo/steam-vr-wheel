import openvr

openvr.init(openvr.VRApplication_Background)

while True:
    print()
    for c in range(16):
        result, pControllerState = openvr.VRSystem().getControllerState(c)
        for i in pControllerState.rAxis:
            if i.x != 0 or i.y != 0:
                print(i.x, i.y)

