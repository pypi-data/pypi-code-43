#!/usr/bin/env python

import unittest
import sys
import os
#sys.path.append(os.path.realpath(__file__) + '/tests')

suite = unittest.TestLoader().discover('tests')
results = unittest.TextTestRunner(verbosity=2).run(suite)
if len(results.errors) > 0 or len(results.failures) > 0:
    sys.exit(1)
sys.exit()
