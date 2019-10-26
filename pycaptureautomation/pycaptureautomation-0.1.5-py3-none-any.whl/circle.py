"""
  Copyright (C) 2016 Sean O'Rourke

  This software may be modified and distributed under the terms
  of the MIT license.  See the LICENSE file for details.
"""

__author__ = "Sean O'Rourke"

import cv2
import pyautogui

from .color import Color
from .capturearea import CaptureArea


class Circle:
    def __init__(self, cp_area: CaptureArea, x, y, radius, color: Color = Color.BLACK, line_width=2):
        self.cp_area = cp_area
        self.np_image = cp_area.img_color
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.line_width = line_width

    def draw(self):
        cv2.circle(self.np_image, (self.image_center[0], self.image_center[1]), self.radius, self.color, self.line_width)

    @property
    def image_center(self):
        return [self.x, self.y]

    def get_cursor_offset(self, x, y):
        if x > self.x + self.radius or y > self.y + self.radius:
            raise Exception()
        cp_offset = self.cp_area.get_cursor_offset(self.x, self.y)
        return [cp_offset[0] + x, cp_offset[1] + y]

    def move_cursor_to_center(self):
        [x, y] = self.image_center
        pyautogui.moveTo(x, y, 0.3)
