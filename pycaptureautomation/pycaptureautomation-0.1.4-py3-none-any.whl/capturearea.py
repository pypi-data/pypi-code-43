"""
  Copyright (C) 2016 Sean O'Rourke

  This software may be modified and distributed under the terms
  of the MIT license.  See the LICENSE file for details.
"""

__author__ = "Sean O'Rourke"

from PIL import ImageGrab
import numpy as np
import cv2


class CaptureArea:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        capture_area: (int, int, int, int) = (x, y, width, height)
        screen_capture = ImageGrab.grab(capture_area)
        self.img_np = np.array(screen_capture)
        self.img_color = cv2.cvtColor(self.img_np, cv2.COLOR_BGR2RGB)

    def resize(self, width, height):
        self.img_np = cv2.resize(self.img_np, (width, height), interpolation=cv2.INTER_AREA)

    @property
    def image_center(self):
        return [int(self.width / 2), int(self.height / 2)]

    def get_cursor_offset(self, x, y):
        if x > self.width or y > self.height:
            raise Exception()
        return [self.x + x, self.y + y]

    def show_img(self):
        resized_img = cv2.resize(self.img_color, (int(self.width / 2), int(self.height / 2)),
                                 interpolation=cv2.INTER_AREA)
        cv2.imshow("capture", resized_img)
        cv2.waitKey(1)
