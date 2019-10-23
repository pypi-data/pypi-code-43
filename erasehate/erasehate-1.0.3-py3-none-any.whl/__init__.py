# Tweepy
# Copyright 2009-2019 Joshua Roesslein
# See LICENSE for details.

"""
Erase Hate API Library
"""
__version__ = '1.0.3'
__author__ = ' oblockton '
__license__ = 'MIT'

from twitter import twit_API
from classifier import classifier
from reclass import reclassboiler_HTML,parse_reclass_form
from reclass import sumbit_reclassed

#
# def debug(enable=True, level=1):
#     from six.moves.http_client import HTTPConnection
#     HTTPConnection.debuglevel = level
