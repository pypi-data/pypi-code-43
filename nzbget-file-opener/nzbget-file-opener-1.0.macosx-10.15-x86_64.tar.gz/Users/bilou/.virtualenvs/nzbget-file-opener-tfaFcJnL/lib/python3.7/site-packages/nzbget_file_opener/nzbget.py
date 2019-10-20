import os
import subprocess

import psutil
import platform


def is_running(process_name):
    """ Check if there is any running process that contains the given process_name """
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower():
                print(f'found: {proc.name()}')
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def launch_app(app_path):
    """ Launch the app based on current os type """
    print(platform.system())
    if not app_path or not os.path.exists(app_path):
        app_path = None
    if platform.system() == 'Darwin':
        if app_path:
            subprocess.call(["/usr/bin/open", "-a", app_path])
        else:
            os.system(f'osascript -e \'tell app "NZBGet" to open\' &>/dev/null')
    elif platform.system() == 'Windows':
        if app_path:
            r''
        else:
            raise ProcessLookupError('Cannot open app NZBGet. Please do it by yourself and retry')
    else:
        raise ProcessLookupError('Cannot open app NZBGet. Please do it by yourself and retry')


def detect_nzbget_app(hostname, app_path):
    """ Allows to detect if NZBGet is currently running, and launches it if the application path is provided """
    if (hostname == 'localhost' or hostname == '127.0.0.1') and not is_running('nzbget'):
        try:
            launch_app(app_path)
            pass
        except ProcessLookupError as e:
            print(e)
            exit(1)

