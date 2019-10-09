#!python
# -*-coding:utf-8 -*

import sys
from os.path import expanduser, join

target = join(sys.prefix, "eccw.exe")
#target_ico = join(sys.prefix, "eccw.ico")
shortcut_filename = "eccw.lnk"
description = (
    "Exact Critical Coulomb Wedge - Graphical User Interface: "
    "tools to compute and display the exact solution of any "
    "parameter of Critical Coulomb Wedge"
)
script_path = ""
working_dir = ""

if sys.argv[1] == '-install':
    # Log output to a file (for test)
    f = open(r"C:\test.txt",'w')
    print('Creating Shortcut', file=f)

    # Get paths to the desktop and start menu
    desktop_path = get_special_folder_path("CSIDL_COMMON_DESKTOPDIRECTORY")
    startmenu_path = get_special_folder_path("CSIDL_COMMON_STARTMENU")

    # Create shortcuts.
    for path in [desktop_path, startmenu_path]:
        create_shortcut(
            target,
            description,
            join(path, shortcut_filename),
            script_path,
            working_dir,
#            target_ico,
        )