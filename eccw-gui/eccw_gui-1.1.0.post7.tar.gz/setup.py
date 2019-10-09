#!/usr/bin/env python3
# -*-coding:utf-8 -*

from setuptools import setup, find_packages
import sys
from distutils.command.install_data import install_data
import subprocess
import os.path as osp

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
            #target = osp.join(sys.prefix, "eccw.exe")
            target = osp.join(sys.prefix, "pythonw.exe")
            # target_ico = join(sys.prefix, "eccw.ico")
            shortcut_filename = "eccw.lnk"
            description = (
                "Exact Critical Coulomb Wedge - Graphical User Interface: "
                "tools to compute and display the exact solution of any "
                "parameter of Critical Coulomb Wedge"
            )
            script_path = ""
            working_dir = ""
            # Get paths to the desktop and start menu
            desktop_path = get_special_folder_path("CSIDL_COMMON_DESKTOPDIRECTORY")
            startmenu_path = get_special_folder_path("CSIDL_COMMON_STARTMENU")
            # Create shortcuts.
            for path in [desktop_path, startmenu_path]:
                create_shortcut(
                    target,
                    description,
                    osp.join(path, shortcut_filename),
                    script_path,
                    working_dir,
                    # target_ico,
                )


CMDCLASS = {"install_data": MyInstallData}

setup(
    entry_points={"console_scripts": ["eccw=eccw_gui.main:launch"]},
    data_files=get_data_files(),
    scripts=[osp.join("scripts", "eccw")],
    cmdclass=CMDCLASS,
)
