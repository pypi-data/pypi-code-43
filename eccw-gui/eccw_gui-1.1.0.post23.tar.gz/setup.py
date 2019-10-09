#!/usr/bin/env python3
# -*-coding:utf-8 -*

from setuptools import setup, find_packages
import sys
from distutils.command.install_data import install_data

#from distutils.command.install_scripts import install_scripts
#from distutils.command.install import install as _install

import subprocess
import os

def get_data_files():
    """Return data_files in a platform dependent manner"""
    if sys.platform.startswith("linux"):
        data_files = [
            ("share/applications", ["scripts/eccw.desktop"]),
            ("share/pixmaps", [
                "eccw_gui/images/icon_eccw.svg",
                "eccw_gui/images/icon_eccw_512x512.png"
            ]),
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


#class MyInstallScripts(install_scripts):
#    def run(self):
#        install_scripts.run(self)
#        from pprint import pprint
#        pprint(self.__dict__)
#        self.execute(_post_install, (self.install_dir,),
#                     msg="Running post install task")


#def _post_install(dir):
#    subprocess.call(
#        [
#            sys.executable,
#            'eccw_win_post_install.py', 
#            '-install'
#        ], 
#        cwd=os.path.join(dir, '')
#    )

#class MyInstall(_install):
#    def run(self):
#        _install.run(self)
#        from pprint import pprint
#        pprint(self.__dict__)
#        self.execute(_post_install, (self.install_scripts,),
#                     msg="Running post install task")


CMDCLASS = {
    "install_data": MyInstallData,
#    "install_scripts": MyInstallScripts,
#    "install": MyInstall,
}

#SCRIPTS = ["eccw_win_post_install.py", "eccw"]
#SCRIPTS = ["eccw"]
#if sys.platform.startswith('linux'):
#    SCRIPTS.append("eccw")

setup(
    entry_points={"console_scripts": ["eccw=eccw_gui.main:launch"]},
    scripts=[os.path.join("scripts", "eccw")],
    #scripts=[os.path.join('scripts', fname) for fname in SCRIPTS],
    data_files=get_data_files(),
    cmdclass=CMDCLASS,
)
