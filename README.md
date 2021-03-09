# steam-vr-wheel
Wheel emulation using steamVR
=============================



News
=============================
I've got a wheel and hotas recently, and haven't had much time to work on this anyway. It will continue to work thanks to SteamVR good backward compatability, but don't expect any further updates. If anyone wants to fork and keep developing maintaining this app, they are free to do so under MIT licence.


If you just want to use this go to:
===================================
https://github.com/mdovgialo/steam-vr-wheel/releases


For developers:
================

Requires pyopenvr, wxpython (codename phoenix), and vjoy ( http://vjoystick.sourceforge.net/site/ Public domain )

Uses pyvjoy binding from https://github.com/tidzo/pyvjoy

Demos:
======

Wheel mode:
https://www.youtube.com/watch?v=lb0zGBVwN4Y

Joystick mode:
https://www.youtube.com/watch?v=jjb92HQ0M74






Instalation from sources (for developers):
========================================
install python 3.5+

install vjoy

with admin level cmd go to folder where is steam_vr_wheel

write:

pip install .




To run:
=======
open cmd, write:

vrwheel

or 

vrjoystick

or 

vrpad

For configurator - write

vrpadconfig

press ctrl+c to stop

To uninstall:

pip uninstall steam_vr_wheel

