
import glob
import os
import sys
import unittest

philes = glob.glob("tests/*py")
print(philes)
print(sys.argv[0])

suite = unittest.TestSuite()

for t in philes:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)

"""[![Build Status](https://travis-ci.org/christoph2/objutils.svg)](https://travis-ci.org/christoph2/objutils)
"""
