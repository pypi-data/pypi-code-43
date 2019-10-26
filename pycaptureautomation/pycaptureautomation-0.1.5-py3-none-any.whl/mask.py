"""
  Copyright (C) 2016 Sean O'Rourke

  This software may be modified and distributed under the terms
  of the MIT license.  See the LICENSE file for details.
"""

__author__ = "Sean O'Rourke"

import cv2
import pyautogui
import numpy as np

from .capturearea import CaptureArea


class Mask:
    def __init__(self, cp_area: CaptureArea, x, y, width, height, lower_bound_color, upper_bound_color):
        self.cp_area = cp_area
        self.np_image = cp_area.img_color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        frame_hsv = cv2.cvtColor(cp_area.img_color, cv2.COLOR_BGR2HSV)
        h_min = np.array(lower_bound_color, np.uint8)
        h_max = np.array(upper_bound_color, np.uint8)

        mask = cv2.inRange(frame_hsv, h_min, h_max)
        self.mask = mask[y:y+height, x:x+width]

    def get_moments(self):
        moments = cv2.moments(self.mask, 1)
        dM01 = moments['m01']
        dM10 = moments['m10']
        dArea = moments['m00']
        if dArea > 0:
            b_x = int(dM10 / dArea)
            b_y = int(dM01 / dArea)
            return self.get_cursor_offset(b_x, b_y)
        return None

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
