#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.0.1'

import logging
from logging import NullHandler

from .unity_editor import UnityEditor
from .unity_project import UnityProject
from .funity_editor import FUnityEditor

logging.getLogger(__name__).addHandler(NullHandler())
