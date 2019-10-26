import os
import sys
import subprocess
__all__ = [
        'text_image',
        'notify',
        ]

text_image = """
   _____            _       ____
  / ___/____ ___  _| |     / / /_  ___  ____
  \__ \/ __ `/ / / / | /| / / __ \/ _ \/ __ \\
 ___/ / /_/ / /_/ /| |/ |/ / / / /  __/ / / /
/____/\__,_/\__, / |__/|__/_/ /_/\___/_/ /_/
           /____/
                                   :-=+*
                               +#%@@@@@%
                              #@@@@@@@@%
                          :-+*@@@@@@@@@%
                     :##@@@@@%%@@@@@@@@%
                     ***+-:    -+#%%#*+=
           :---------#---
           %:        *  *
          :%         *  *
          +#         *  +:
          #+=++++++++#=++=
          +*#@@@@@@@@@@%+-
           =+*%@@@@@@%++=
            :+=******+=:
                :-+
                 :+
                 :+
                 :+
                 :+
            =+**###***+=
"""

g_audio_names = {
        True: '80921__justinbw__buttonchime02up.wav',
        False: '142608__autistic-lucario__error.wav'
        }

def get_audio_names():
    return g_audio_names

def get_audio_path(status, audio_names):
    return os.path.join(os.path.dirname(__file__), 'audio', audio_names[status])

def play_audio(player_cmd, audio_path):
    subprocess.check_call("{} {}".format(player_cmd, audio_path),
                          shell=True,
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL,
                          )

def send_audio_notification(status):
    audio = get_audio_path(status, get_audio_names())
    if sys.platform == 'darwin':
        player_cmd = "afplay"
    elif sys.platform == 'linux':
        player_cmd = "aplay"
    else:
        raise NotImplementedError
    play_audio(player_cmd, audio)

def _send_desktop_notification(title, content):
    if sys.platform == 'darwin':
        cmd_str = "osascript -e \"display notification \\\"{}\\\" with title \\\"{}\\\"\"".format(content, title)
    elif sys.platform == 'linux':
        cmd_str = "notify-send '{}' '{}'".format(title, content)
    else:
        raise NotImplementedError
    subprocess.check_call(cmd_str, shell=True)

def send_desktop_notification(status, time_elapsed, command_str, cwd):
    if status:
        text_prefix = "✔️ Job Finished with"
    else:
        text_prefix = "✖ Job Failed after"
    if time_elapsed < 60:
        time_elapsed = "{:.2f}s".format(time_elapsed)
    else:
        minutes = int(time_elapsed // 60)
        seconds = time_elapsed % 60
        time_elapsed = "{}m{:.2f}s".format(minutes, seconds)
    title = "{} {}".format(text_prefix, time_elapsed)
    content = "CMD: {}\\nCWD: {}".format(command_str, cwd)
    _send_desktop_notification(title, content)

def notify(status, time_elapsed, command_str, cwd):
    send_desktop_notification(status, time_elapsed, command_str, cwd)
    send_audio_notification(status)
