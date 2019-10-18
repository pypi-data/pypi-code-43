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


class Rectangle:
    def __init__(self, cp_area: CaptureArea, x, y, width, height, color: Color = Color.BLACK, line_width=2):
        self.cp_area = cp_area
        self.np_image = cp_area.img_color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.line_width = line_width

    def draw(self):
        rec_start_pos = (self.x, self.y)
        rec_end_pos = (self.x + self.width, self.y + self.height)
        cv2.rectangle(self.np_image, rec_start_pos, rec_end_pos, self.color, self.line_width)

    @property
    def image_center(self):
        return [int(self.width / 2), int(self.height / 2)]

    def get_cursor_offset(self, x, y):
        if x > self.width or y > self.height:
            raise Exception()
        cp_offset = self.cp_area.get_cursor_offset(self.x, self.y)
        return [cp_offset[0] + x, cp_offset[1] + y]

    def move_cursor_to_center(self):
        [x, y] = self.image_center
        [offset_x, offset_y] = self.get_cursor_offset(x, y)
        pyautogui.moveTo(offset_x, offset_y, 0.3)
