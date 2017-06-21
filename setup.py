"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


# Always prefer setuptools over distutils
import glob
import sys
from setuptools import setup, find_packages
# To use a consistent encoding

if 'py2exe' in sys.argv:
    import py2exe

setup(
    name='steam_vr_wheel',


    # Choose your license
    license='MIT',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    #install_requires=['openvr==1.0.301', 'numpy'],
    install_requires=['openvr', 'numpy'],


    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    zip_safe=False,
    package_data={
        'steam_vr_wheel': ['steam_vr_wheel/pyvjoy/vJoyInterface.dll', 'steam_vr_wheel/pyvjoy/vJoyInterface.lib'],
    },

    data_files=[('.', glob.glob('*.dll')),
                ('.', glob.glob('*.pyd'))],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'vrwheel=steam_vr_wheel.wheel:main',
            'vrjoystick=steam_vr_wheel.joystick:main_j',
            'vrpad=steam_vr_wheel.pad:main_p',
        ],
    },
)
