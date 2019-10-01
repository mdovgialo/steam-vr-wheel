import json
from collections import defaultdict

from steam_vr_wheel.pyvjoy.vjoydevice import HID_USAGE_X, HID_USAGE_Y, HID_USAGE_Z , HID_USAGE_RX, HID_USAGE_RY, HID_USAGE_RZ, HID_USAGE_SL0, HID_USAGE_SL1


actions = []
types = ["/actions/joystick",
         "/actions/wheel",
         "/actions/double_joystick",
         "/actions/gamepad",
        ]
axis = ["x",
        'y',
        'z'
        'rx',
        'ry',
        'rz',
        'slider0',
        'slider1',
        ]
axis_vjoy = [HID_USAGE_X, HID_USAGE_Y, HID_USAGE_Z , HID_USAGE_RX, HID_USAGE_RY, HID_USAGE_RZ, HID_USAGE_SL0, HID_USAGE_SL1]
axis_to_vjoy = {i: j for i, j in zip(axis, axis_vjoy)}

axis_pairs = ['x_y',
              'rx_ry',
              'z_rz',
              'slider0_slider1']
axis_pairs_to_vjoy = {
    'x_y': [HID_USAGE_X, HID_USAGE_Y],
    'rx_ry': [HID_USAGE_RX, HID_USAGE_RY],
    'z_rz': [HID_USAGE_Z, HID_USAGE_RZ],
    'slider0_slider1': [HID_USAGE_SL0, HID_USAGE_SL1]
}

for type in types:
    for i in range(1, 129):
        entry = {
          "name": "{}/in/button_{}".format(type, i),
          "requirement": "optional",
          "type": "boolean"
        }
        actions.append(entry)

    for ax in axis:
        entry = {
          "name": "{}/in/axis_{}".format(type, ax),
          "requirement": "optional",
          "type": "vector1"
        }
        actions.append(entry)

    for ax in axis_pairs:
        entry = {
          "name": "{}/in/axis_{}".format(type, ax),
          "requirement": "optional",
          "type": "vector2"
        }
        actions.append(entry)


actions.append(
    {
          "name": "/actions/default/in/move_resize_wheel",
          "requirement": "optional",
          "type": "boolean"
        })

actions.append(
    {
      "name": "/actions/default/in/Pose",
      "type": "pose"
    },
)
actions.append({
    "name": "/actions/default/out/Haptic",
    "type": "vibration"
}
)



types_short = ["/actions/joystick",
         "/actions/wheel",
         "/actions/double_joystick",
        ]

for type in types_short:
    actions.extend(
        [
            {
              "name": "{}/in/grab_left".format(type),
              "requirement": "optional",
              "type": "boolean"
            },

            {
                "name": "{}/in/grab_right".format(type),
                "requirement": "optional",
                "type": "boolean"
            }
        ]
    )

action_per_action_sets_boolean = defaultdict(list)
action_per_action_sets_vector1 = defaultdict(list)
action_per_action_sets_vector2 = defaultdict(list)

for act in actions:
    for aset in types + ['/actions/default']:
        if act['name'].split('/')[3] == 'in':
            if act['name'].startswith(aset):
                if act['type'] == 'boolean':
                    basename = act['name'].split('/')[-1]
                    if basename.startswith('button'):
                        act['vjoy_btn_nr'] = int(basename.split('_')[-1])
                    action_per_action_sets_boolean[aset].append(act)
                if act['type'] == 'vector1':
                    if basename.startswith('axis'):
                        axis_name = basename.split('_')[-1]
                        act['vjoy_axis'] = axis_to_vjoy[axis_name]
                    action_per_action_sets_vector1[aset].append(act)
                if act['type'] == 'vector2':
                    if basename.startswith('axis'):
                        axis_name = basename.split('_')[-1]
                        act['vjoy_axis_pair'] = axis_pairs_to_vjoy[axis_name]
                    action_per_action_sets_vector2[aset].append(act)


def get_action_sets_for_type(type):
    fulltype = '/actions/{}'.format(type)
    return (action_per_action_sets_boolean.get(fulltype, []),
            action_per_action_sets_vector1.get(fulltype, []),
            action_per_action_sets_vector2.get(fulltype, []),)

if __name__ == '__main__':
    print(json.dumps(actions, indent=6))


