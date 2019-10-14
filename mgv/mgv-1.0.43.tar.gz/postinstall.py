#! python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import mangrove

DESKTOP_FOLDER = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
NAME = "Mangrove.lnk"

if sys.argv[1] == '-install':
    path = os.path.join(sys.prefix, 'python.exe')
    print('path:', path)
    create_shortcut(
        path,
        "Mangrove UI",
        NAME,
        os.path.join(os.path.dirname(mangrove.__file__), "mgvUI.py"),
        DESKTOP_FOLDER,
        os.path.join(os.path.dirname(mangrove.__file__),"icons","mgv.ico"))

    shutil.move(os.path.join(os.getcwd(), NAME), os.path.join(DESKTOP_FOLDER, NAME))
    file_created(os.path.join(DESKTOP_FOLDER, NAME))

if sys.argv[1] == '-remove':
    pass

try:
    sys.stdout.flush()
except:
    pass
