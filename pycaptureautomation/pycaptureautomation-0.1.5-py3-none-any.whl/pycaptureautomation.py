"""
  Copyright (C) 2016 Sean O'Rourke
 
  This software may be modified and distributed under the terms
  of the MIT license.  See the LICENSE file for details.
"""

__author__ = "Sean O'Rourke"

import time
from threading import Lock, Thread
from typing import Callable

from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect

from .capturearea import CaptureArea


class WinAutomation:
    def __init__(self, window_text=None):
        self.exit_flag = False
        self.window_text = window_text
        self.window_x_pos = None
        self.window_y_pos = None
        self.window_width = None
        self.window_height = None
        self.thread = None
        self.lock = Lock()
        self.binding: Callable[[CaptureArea, str], CaptureArea] = None

    def set_window_text(self, window_text):
        self.window_text = window_text

    def start_capture(self):
        self.exit_flag = False
        self.thread = Thread(target=self._main_loop)
        self.thread.start()

    def exit(self):
        self.exit_flag = True

    def _main_loop(self):
        while self.exit_flag is False:
            self.collect_window()
            time.sleep(0.1)

    def bind(self, on_screen_capture: Callable[[CaptureArea], CaptureArea]):
        self.binding = on_screen_capture

    def collect_window(self):
        foreground_window = GetWindowText(GetForegroundWindow())
        self.lock.acquire()
        if foreground_window != self.window_text:
            if self.binding is not None:
                self.binding(None, "{} not found in active window, current: {}".format(self.window_text, foreground_window))
            time.sleep(2)
            self.window_x_pos = None
            self.window_y_pos = None
            self.window_width = None
            self.window_height = None

        else:
            (self.window_x_pos, self.window_y_pos, self.window_width, self.window_height) = GetWindowRect(
                GetForegroundWindow())
            capture_area = CaptureArea(self.window_x_pos, self.window_y_pos, self.window_width, self.window_height)
            if self.binding is not None:
                self.binding(capture_area, None)
        self.lock.release()


