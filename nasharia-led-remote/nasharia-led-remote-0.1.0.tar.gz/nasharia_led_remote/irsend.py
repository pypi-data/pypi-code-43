"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of nasharia-led-remote.

nasharia-led-remote is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

nasharia-led-remote is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with nasharia-led-remote.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import time
from subprocess import Popen
from nasharia_led_remote.commands import command_map


def send_command(command: str, duration: int = 0):
    """
    Sends a command using irsend
    The command should have an entry in
    :param command: The command to send
    :param duration: The duration for which to send the signal.
    :return: None
    """
    key_command = command_map.get(command, "")
    if key_command == "":
        print("Invalid command")
        return

    irsend_command = ["irsend", "", "NASHARIA", "KEY_" + key_command]

    try:
        if duration <= 0:
            irsend_command[1] = "send_once"
            resp = Popen(irsend_command).wait()

        else:
            irsend_command[1] = "send_start"
            resp = Popen(irsend_command).wait()
            time.sleep(duration)
            irsend_command[1] = "send_stop"
            resp += Popen(irsend_command).wait()
    except FileNotFoundError:
        print("irsend not installed!")
        resp = 1

    if resp != 0:
        print("Something went wrong. Is lirc configured correctly?")
