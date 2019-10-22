"""
ChatterBot is a machine learning, conversational dialog engine.
default is the default path to the db learning file
indev you create a new file so you can see how it works
"""
from .chatterbot import ChatBot
import os
from distutils.sysconfig import get_python_lib as gpl
path = gpl()
default = os.path.join(path,'chatterbot','database.sqlite3')
indev = '/database.sqlite3'

__all__ = (
    'ChatBot','default','indev'
)
