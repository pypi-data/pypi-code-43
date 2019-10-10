# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys
from os import path

tlib = path.join(path.dirname(path.dirname(__file__)), 'tlib')
sys.path.insert(0, tlib)

from _sadmtest.conf import *
