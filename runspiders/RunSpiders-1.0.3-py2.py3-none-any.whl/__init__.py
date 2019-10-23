# -*- coding: utf-8 -*-
# @Time     : 2019/5/16 16:49
# @Author   : Run
# @File     : __init__.py
# @Software : PyCharm

"""
todo:
    1. 探索`gevent`。`monkey.patch_all()`总是导致运行`from RunSpiders import *`时出现错误
        `RuntimeError: cannot release un-acquired lock`
"""


from RunSpiders.utils import *
from RunSpiders.book.web_fiction import WebFictionSpider, check_calibre_installed
# from RunSpiders.video.m3u8 import M3U8Spider, check_ffmpeg_installed
# from RunSpiders.video.jav import JAVSpider
# from RunSpiders.video.vk import VK
from RunSpiders.others.for_github import *
