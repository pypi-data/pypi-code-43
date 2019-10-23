from __future__ import absolute_import
import os
from .version import __VERSION__ as __version__
from .population_params_absracts import *
from .rateDistributions import *
from .pop_dists import *


here = __file__
basedir = os.path.split(here)[0]
example_data = os.path.join(basedir, 'example_data')
