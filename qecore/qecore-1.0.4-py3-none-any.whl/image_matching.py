#!/usr/bin/env python3
import sys
from os import path
from time import sleep
from dogtail.rawinput import click
from behave import step
from qecore import run

try:
    import cv2
except ModuleNotFoundError:
    print("You need to install an 'opencv-python' via pip or 'python3-opencv' via yum/dnf.")
    sys.exit(1)

HELP_MESSAGE = """
You are encouraged to build your own step function according to your needs.
Two steps that you see bellow are:
    * General step that just compares and asserts the result.
    * General step that just compares and clicks on the found result.

What is needed for image match:
    * You need to capture an image in which we look for the element you want to find.
        * Provided by capture_image method in Matcher class.
        * This option is True by default.
        * If you have your own, set capture=False and provide self.screen_path in the Matcher class.

    * You need to match the two images, you are looking for a 'needle'.
      So you provide it in function or in step call (.feature file).
        * Provided by match which will return True or False. Lets user react on False return value.
        * Provided by assert_match which will assert the result and terminate the test on False.

    * (Optional) You can draw the result for attachment or
            your own confirmation that matching works.
        * Provided by draw method on Matcher instance to get an image with highlighted needle.
          Highlight is a red rectangle exactly in a place of a match, surrounding provided needle.

    * (Optional) You can click on your found result.
        * Provided by click method in Matcher instance.
        * Requirements are of course success of a match/assert_match.

    * (Optional) You can embed result to test report.
        * For this option the method draw is required.
        * Use method provided in TestSandbox class:
            attach_image_to_report(context, image=image_location, caption="DefaultCaption")
        * Or embed it on your own:
            context.embed("image/png", open(image_location, "rb").read(), caption="DefaultCaption")
        * Remember that result is saved in Matcher instance as
            self.diff_path which equals "/tmp/diff.png"
"""

@step('Image "{needle}" is shown on screen')
@step('Image "{needle}" is shown on screen with threshold "{threshold:d}"')
def image_match(context, needle, threshold=0.8):
    image_match_instance = Matcher()
    image_match_instance.assert_match(needle, threshold)
    image_match_instance.draw()


@step('Locate and click "{needle}"')
def locate_and_click(context, needle):
    image_match_instance = Matcher()
    image_match_instance.assert_match(needle)
    image_match_instance.click()


class Matcher:
    def __init__(self):
        self.screen_path = "/tmp/pic.png"
        self.diff_path = "/tmp/diff.png"
        self.capture_image_cmd = f"gnome-screenshot -f {self.screen_path}"
        self.needle_width = 0
        self.needle_height = 0
        self.matched_value = 0.0
        self.matched_loc = (0, 0)

        self.ori_img = None
        self.ori_img_gray = None
        self.needle = None
        self.needle_size = None

    def capture_image(self):
        run(self.capture_image_cmd)


    def assert_match(self, needle, threshold=0.8, capture=True):
        assert self.match(needle, threshold, capture), \
            f"Image match value: {self.matched_value}"


    def match(self, needle, threshold=0.8, capture=True):
        if capture:
            self.capture_image()

        self.ori_img = cv2.imread(self.screen_path)
        self.ori_img_gray = cv2.cvtColor(self.ori_img, cv2.COLOR_BGR2GRAY)
        self.needle = cv2.imread(path.abspath(needle), 0)
        self.needle_width, self.needle_height = self.needle.shape[::-1]

        match = cv2.matchTemplate(self.ori_img_gray, self.needle, cv2.TM_CCOEFF_NORMED)
        _, self.matched_value, _, self.matched_loc = cv2.minMaxLoc(match)

        return self.matched_value > threshold


    def draw(self):
        self.needle_size = (self.matched_loc[0] + self.needle_width, \
                            self.matched_loc[1] + self.needle_height)
        cv2.rectangle(self.ori_img, self.matched_loc, self.needle_size, (0, 0, 255), 2)
        cv2.imwrite(self.diff_path, self.ori_img)


    def click(self):
        match_center_x = self.matched_loc[0] + int(self.needle_width / 2)
        match_center_y = self.matched_loc[1] + int(self.needle_height / 2)
        click(match_center_x, match_center_y)
        sleep(1)
