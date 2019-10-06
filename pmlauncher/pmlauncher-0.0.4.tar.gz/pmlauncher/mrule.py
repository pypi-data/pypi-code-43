import platform
import os

checkOSRules = True

is64bit = platform.machine().endswith('64')
if is64bit:
    arch = "64"
else:
    arch = "32"

osversion = platform.release()
osname = ""
sysname = platform.system()
if sysname == "Linux":
    osname = "linux"
elif sysname == "Darwin":
    osname = "osx"
else:
    osname = "windows"
#osname = "windows"  # fake os to debug


def checkAllowOS(arr):
    for job in arr:
        action = True  # allow / disallow
        containCurrentOS = True

        for key, value in job.items():

            if key == "action":
                if value == "allow":
                    action = True
                else:
                    action = False

            elif key == "os":
                containCurrentOS = check_os_contains(value.items())

            elif key == "features":
                return False

        if not action and containCurrentOS:
            return False
        elif action and containCurrentOS:
            return True
        elif action and not containCurrentOS:
            return False


def check_os_contains(arr):
    for osKey, osValue in arr:
        if osKey == "name" and osValue == osname:
            return True
    return False
