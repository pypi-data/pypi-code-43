# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.screenshots.base import ScreenshotsIndexSaver
from suanpan.state.arguments import StorageSaverArg


class Screenshots(StorageSaverArg):
    STATE_CLASS = ScreenshotsIndexSaver
    STATE_PATTERN = "{index}.png"
