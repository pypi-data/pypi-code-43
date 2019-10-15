# -*- coding: utf-8 -*-

# Run the build process by running the command 'python cx_frz_create_exe.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'includes': ['atexit'],
        'packages': ['modbus_tk'],
        'zip_include_packages': ['PyQt5']
    }
}

executables = [
    Executable('pyModSlave.py', base=base)
]

setup(name='pyModSlave',
      version='0.4.3',
      description='pyModSlave - Modbus RTU-TCP slave',
      options=options,
      executables=executables
      )
