#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains a clickbot"""

import functools
import time
import random
import datetime
import pynput
from .logger import Logger, error_catcher
from .events import sleep, Move, Scroll, Click, Keys

__author__ = "Justin Furuness"
__credits__ = ["Justin Furuness"]
__Lisence__ = "MIT"
__Version__ = "0.1.0"
__maintainer__ = "Justin Furuness"
__email__ = "jfuruness@gmail.com"
__status__ = "Development"


class Clickbot:
    """This class creats a clickbot"""

    __slots__ = ['logger', 'events', 'last_scrolled_x', 'last_scrolled_y',
                 'box', 'mouse', 'keys', 'keyboard']

    @error_catcher()
    def __init__(self, args={}):
        """Initializes variables"""

        self.logger = Logger(args).logger
        self.events = []
        self.mouse = pynput.mouse.Controller()
        self.keyboard = pynput.keyboard.Controller()
        self.logger.info("Initialized Clickbot at {}".format(
            datetime.datetime.now()))

    def configure(self):
        """Configures all click events that you want"""

        event_type = input("type click, scroll, move, keyboard, or none")
        while event_type in ["click", "scroll", "move", "keyboard"]:
            if event_type == "click":
                self._add_click()
            elif event_type == "scroll":
                self._add_scroll()
            elif event_type == "move":
                self._add_move()
            elif event_type == "keyboard":
                self._add_keys()
            event_type = input("type click, scroll, move, or none")

    def run(self):
        """Runs clickbot"""

        counter = 0
        while(True):
            for event in self.events:
                event.do_stuff(self.mouse, self.keyboard)
            counter += 1
            self.logger.info("Ran {} times in a row".format(counter))

    def _change_timeout(self):
        """Changes the default timeouts for events"""

        self.events[-1].start = float(input("input time until start of event"))
        self.events[-1].end = float(input("input end time of event"))

    def _add_keys(self):
        """Adds keyboard events"""

        self.logger.info("type keys to add to events, then escape")
        self.keys = []
        with pynput.keyboard.Listener(on_press=self._on_press,
                                      on_release=self._on_release) as listener:
            listener.join()
        self.events.append(Keys(self.logger, self.keys))
        self._change_timeout()

    def _on_press(self, key):
        """Press event listener"""

        try:
            self.logger.info("Pressed {}".format(key.char))
            self.keys.append(key.char)
        except AttributeError:
            if key != pynput.keyboard.Key.esc:
                self.logger.info("Pressed {}".format(key))
                self.keys.append(key)

    def _on_release(self, key):
        """Release event listener"""

        if key == pynput.keyboard.Key.esc:
            return False

    def _add_move(self):
        """Adds a move mouse event"""

        self.logger.info("Click top left and bottom right to move")
        self.box = []
        with pynput.mouse.Listener(on_click=self._on_move) as listener:
            listener.join()
        self.events.append(Move(self.logger, self.box[0], self.box[1]))
        self._change_timeout()

    def _add_click(self):
        """Adds a click mouse event"""

        self.logger.info("Click to click")
        with pynput.mouse.Listener(on_click=self._on_click) as listener:
            listener.join()
        self._change_timeout()

    def _add_scroll(self):
        """Adds a scroll mouse event"""

        self.logger.info("scroll then right click to scroll")
        self.last_scrolled_x = None
        self.last_scrolled_y = None
        with pynput.mouse.Listener(on_click=self._on_scroll_click,
                                   on_scroll=self._on_scroll) as listener:
            listener.join()
        self.events.append(Scroll(self.logger,
                                  self.last_scrolled_x,
                                  self.last_scrolled_y))
        self._change_timeout()

    def _on_scroll_click(self, x, y, button, pressed):
        """Click event after a scroll"""

        self.logger.info("Scrolled to {},{}".format(self.last_scrolled_x,
                                                    self.last_scrolled_y))
        if button == pynput.mouse.Button.right:
            return False

    def _on_move(self, x, y, Button, pressed):
        """Move event listener"""

        self.logger.info("Moved to {}, {}".format(x, y))
        if len(self.box) <= 1:
            if len(self.box) > 0:
                if self.box[-1] != self.mouse.position:
                    self.box.append(self.mouse.position)
            else:
                self.box.append(self.mouse.position)
        else:
            return False

    def _on_click(self, x, y, button, pressed):
        """Click event listener"""

        self.logger.info("Button {} Pressed at {}, {}".format(button, x, y))
        self.events.append(Click(self.logger, button))
        return False

    def _on_scroll(self, x, y, dx, dy):
        """Scroll event listener"""
        self.logger.info("Scrolled to {}, {}".format(x, y))
        self.last_scrolled_x = x
        self.last_scrolled_y = y
