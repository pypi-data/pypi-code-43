# -*- coding: utf-8 -*-
#
# Copyright © 2019 Stephan Seitz <stephan.seitz@fau.de>
#
# Distributed under terms of the GPLv3 license.

"""
Provides a disk_cache to cache results of compute-intensive
function calls (e.g. calculation of phantoms)
"""

import os

from appdirs import user_cache_dir
from joblib import Memory

# 5_000_000_000 is not supported in Python 3.5
CACHE_LIMIT = 5000000000  # in bytes

if 'PYCONRAD_CACHE_DIR' in os.environ:
    cache_dir = os.environ['PYCONRAD_CACHE_DIR']
else:
    cache_dir = user_cache_dir('pyconrad')
disk_cache = Memory(cache_dir, verbose=False, bytes_limit=CACHE_LIMIT).cache
