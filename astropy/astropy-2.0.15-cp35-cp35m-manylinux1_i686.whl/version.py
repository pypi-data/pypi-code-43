# Autogenerated by Astropy's setup.py on 2019-10-07 04:20:22 UTC
from __future__ import unicode_literals
import datetime

version = "2.0.15"
githash = "6c76e90136f960dd25f185511d4eaf092e90dbc4"


major = 2
minor = 0
bugfix = 15

release = True
timestamp = datetime.datetime(2019, 10, 7, 4, 20, 22)
debug = False

astropy_helpers_version = "2.0.10.dev860"

try:
    from ._compiler import compiler
except ImportError:
    compiler = "unknown"

try:
    from .cython_version import cython_version
except ImportError:
    cython_version = "unknown"
