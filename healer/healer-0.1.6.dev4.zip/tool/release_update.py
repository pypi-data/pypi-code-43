#!/usr/bin/env python

"""
PyPi release rotation
"""

from __future__ import annotations

from devrepo import base_dir
from pypirepo import perform_update

project_dir = base_dir()
project_name = 'healer'

perform_update(project_dir, project_name)
