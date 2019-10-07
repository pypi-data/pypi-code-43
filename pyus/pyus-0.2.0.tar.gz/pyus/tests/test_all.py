"""
Test suite for the pyus package.
"""

import unittest

from pyus.tests import test_signal_convolution_direct
from pyus.tests import test_signal_hilbert_fir
from pyus.tests import test_prefilter

suites = []
suites.append(test_signal_convolution_direct.suite)
suites.append(test_signal_hilbert_fir.suite)
suites.append(test_prefilter.suite)
suite = unittest.TestSuite(suites)

def run():
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    run()
