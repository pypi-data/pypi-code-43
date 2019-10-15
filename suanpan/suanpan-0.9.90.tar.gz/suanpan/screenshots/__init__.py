# coding=utf-8
from __future__ import absolute_import, print_function

import os

from suanpan.proxy import Proxy

TYPE = os.environ.get("SP_SCREENSHOTS_TYPE", "index")
PATTERN = os.environ.get("SP_SCREENSHOTS_PATTERN")
STORAGE_KEY = os.environ.get("SP_SCREENSHOTS_STORAGE_KEY")
THUMBNAIL_STORAGE_KEY = os.environ.get("SP_SCREENSHOTS_THUMBNAIL_STORAGE_KEY")


class Screenshots(Proxy):
    MAPPING = {
        "index": "suanpan.screenshots.base.ScreenshotsIndexSaver",
        "time": "suanpan.screenshots.base.ScreenshotsTimeSaver",
    }
    DEFAULT_PATTERN_MAPPING = {"index": "{index}.png", "time": "{time}.png"}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(self.TYPE_KEY, TYPE)
        kwargs.setdefault("name", STORAGE_KEY)
        kwargs.setdefault("thumbnail", THUMBNAIL_STORAGE_KEY)
        kwargs.setdefault(
            "pattern", PATTERN or self.DEFAULT_PATTERN_MAPPING.get(kwargs["type"])
        )
        super(Screenshots, self).__init__(*args, **kwargs)


screenshots = Screenshots()
