#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains events"""

import functools
import time
import random
import datetime
import pynput
from .logger import Logger, error_catcher

__author__ = "Justin Furuness"
__credits__ = ["Justin Furuness"]
__Lisence__ = "MIT"
__maintainer__ = "Justin Furuness"
__email__ = "jfuruness@gmail.com"
__status__ = "Development"

def sleep():
    """Decorator wraps all funcs with self arg to fail gracefully"""
    def my_decorator(func):
        @functools.wraps(func)
        def function_that_runs_func(self, *args, **kwargs):
            """Sleeps for a random amount of time"""

            if self.start == self.end:
                time.sleep(self.start)
            else:
                time.sleep(random.uniform(self.start, self.end))
            return func(self, *args, **kwargs)
        return function_that_runs_func
    return my_decorator


class Move:
    """Move event"""

    def __init__(self, logger, top_left, bottom_right, start=1, end=10):
        """inits vars"""

        self.logger = logger
        self.top_left_x = top_left[0]
        self.top_left_y = top_left[1]
        self.bottom_right_x = bottom_right[0]
        self.bottom_right_y = bottom_right[1]
        self.start = start
        self.end = end

    @sleep()
    def do_stuff(self, mouse, _):
        """Performs event action"""

        # Gets a random place of x within box dimensions
        x = random.uniform(self.top_left_x, self.bottom_right_x)
        # Gets a random place of y within box dimensions
        y = random.uniform(self.bottom_right_y, self.top_left_y)
        mouse.position = (x, y)
        self.logger.info("Moved mouse to {}, {}".format(x, y))

class Scroll:
    """Scroll event"""

    def __init__(self, logger, x, y, start=1, end=10):
        """inits vars"""

        self.logger = logger
        self.x = x
        self.y = y
        self.start = start
        self.end = end

    @sleep()
    def do_stuff(self, mouse, _):
        """Performs event action"""

        mouse.scroll(self.x, self.y)
        self.logger.info("Scrolled to {}, {}".format(self.x, self.y))


class Click:
    """Click event"""

    def __init__(self, logger, button, start=1, end=10):
        """inits vars"""

        self.logger = logger
        self.button = button
        self.start = start
        self.end = end

    @sleep()
    def do_stuff(self, mouse, _):
        """Performs event action"""

        mouse.click(self.button, 1)
        self.logger.info("Clicked")


class Keys:
    """Keyboard event"""

    def __init__(self, logger, keys, start=1, end=2):
        """Inits keys"""

        self.logger = logger
        self.keys = keys
        self.start = start
        self.end = end

    @sleep()
    def do_stuff(self, _, keyboard):
        """Types stuff"""

        for key in self.keys:
            self._press_key(keyboard, key)

    @sleep()
    def _press_key(self, keyboard, key):
        keyboard.press(key)
        keyboard.release(key)
        self.logger.info("Pressed {}".format(key))
