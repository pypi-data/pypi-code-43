#!/usr/bin/env python3
# -*-coding:utf-8 -*

from setuptools import setup, find_packages
import sys
from distutils.command.install_data import install_data
import subprocess
import os

def get_data_files():
    """Return data_files in a platform dependent manner"""
    if sys.platform.startswith("linux"):
        data_files = [
            ("share/applications", ["scripts/eccw.desktop"]),
            ("share/pixmaps", ["eccw_gui/images/icon_eccw.svg"]),
            ("share/metainfo", ["scripts/eccw.appdata.xml"]),
        ]
    else:
        data_files = []
    return data_files

# Make Linux detect ECCW desktop file
class MyInstallData(install_data):
    def run(self):
        install_data.run(self)
        if sys.platform.startswith("linux"):
            try:
                subprocess.call(["update-desktop-database"])
            except:
                print("ERROR: unable to update desktop database", file=sys.stderr)
        if sys.platform.startswith("win"):

            app_name = "eccw"
            datadir = os.path.join(get_special_folder_path("CSIDL_APPDATA"), app_name)

            desktop = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
            print("Desktop path: %s" % repr(desktop))
            # Create data directory if not already exist.
            if not os.path.exists(datadir):
                os.makedirs(datadir)
                dir_created(datadir)

            shortcut = os.path.join(desktop, app_name + ".lnk")
            # Remove existing shortcut if any.
            if os.path.exists(shortcut):
                os.unlink(shortcut)

            target = os.path.join(sys.prefix, "pythonw.exe")

            # Creating shortcut.
            create_shortcut(
                target,
                "MyModuleScript",
                shortcut, 
                "",
                datadir)
            file_created(shortcut)

            ##target = os.path.join(sys.prefix, "eccw.exe")
            #target = os.path.join(sys.prefix, "pythonw.exe")
            ## target_ico = join(sys.prefix, "eccw.ico")
            #shortcut_filename = "eccw.lnk"
            #description = (
            #    "Exact Critical Coulomb Wedge - Graphical User Interface: "
            #    "tools to compute and display the exact solution of any "
            #    "parameter of Critical Coulomb Wedge"
            #)
            #script_path = ""
            #working_dir = ""
            ## Get paths to the desktop and start menu
            #desktop_path = get_special_folder_path("CSIDL_COMMON_DESKTOPDIRECTORY")
            #startmenu_path = get_special_folder_path("CSIDL_COMMON_STARTMENU")
            ## Create shortcuts.
            #for path in [desktop_path, startmenu_path]:
            #    create_shortcut(
            #        target,
            #        description,
            #        os.path.join(path, shortcut_filename),
            #        script_path,
            #        working_dir,
            #        # target_ico,
            #    )


CMDCLASS = {"install_data": MyInstallData}

setup(
    entry_points={"console_scripts": ["eccw=eccw_gui.main:launch"]},
    data_files=get_data_files(),
    scripts=[os.path.join("scripts", "eccw")],
    cmdclass=CMDCLASS,
)
