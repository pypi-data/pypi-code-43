"""
  Copyright (C) 2016 Sean O'Rourke
 
  This software may be modified and distributed under the terms
  of the MIT license.  See the LICENSE file for details.
"""

__author__ = "Sean O'Rourke"

import time
from threading import Lock, Thread

from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect

from .capturearea import CaptureArea


class WinAutomation:
    def __init__(self, window_text):
        self.exit_flag = False
        self.window_text = window_text
        self.window_x_pos = None
        self.window_y_pos = None
        self.window_width = None
        self.window_height = None
        self.thread = None
        self.lock = Lock()
        self.capture: CaptureArea = None

    @staticmethod
    def get_capture(win_auto) -> CaptureArea:
        win_auto.lock.acquire()
        capture = win_auto.capture
        win_auto.release()
        return capture

    def release(self):
        self.lock.release()

    def start_capture(self):
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

    def main_loop(self):
        while self.exit_flag is False:
            self.collect_window()
            time.sleep(0.1)

    def collect_window(self):
        foreground_window = GetWindowText(GetForegroundWindow())
        self.lock.acquire()
        if foreground_window != self.window_text:
            print("Waiting for {} as active window".format(self.window_text))
            time.sleep(2)
            self.window_x_pos = None
            self.window_y_pos = None
            self.window_width = None
            self.window_height = None

        else:
            (self.window_x_pos, self.window_y_pos, self.window_width, self.window_height) = GetWindowRect(
                GetForegroundWindow())
            self.capture = CaptureArea(self, self.window_x_pos, self.window_y_pos, self.window_width,
                                       self.window_height)
        self.lock.release()


