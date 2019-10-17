# -*- coding: utf-8 -*-

"""Top-level package for SCM Calibration."""

import os
import sys

# Order matters here. MKL_THREADING_LAYER has to be set prior to any theano calls
os.environ["MKL_THREADING_LAYER"] = "GNU"

# Disable the theano debug hook. It messes with pycharm stack traces and won't be needed by scmcallib
from theano.gof.link import __excepthook

sys.excepthook = __excepthook

from ._version import get_versions
from .finder import PointEstimateFinder, DistributionFinder
from .distributions import Normal, LogNormal, Scalar, Bound
from .parameterset import ParameterSet

__version__ = get_versions()["version"]
del get_versions
