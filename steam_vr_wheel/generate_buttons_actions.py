import json
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


actions.append(
    {
          "name": "/actions/configurator/in/move_resize_wheel",
          "requirement": "optional",
          "type": "boolean"
        })


print(json.dumps(actions, indent=6))


