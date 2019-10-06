# Copyright 2016 Kirk A Jackson DBA bristoSOFT all rights reserved.  All methods,
# techniques, algorithms are confidential trade secrets under Ohio and U.S. 
# Federal law owned by bristoSOFT.
#
# Kirk A Jackson dba bristoSOFT
# 4100 Executive Park Drive
# Suite 11
# Cincinnati, OH  45241
# Phone (513) 401-9114
# email jacksonkirka@bristosoft.com
# 
# The trade name bristoSOFT is a registered trade name with the State of Ohio
# document No. 201607803210. 
#
# Note: Testing can be done using perhaps unittest and other test that do not
# require database connection.

"""
This test_controller module is the testing module for bristoSOFT Contacts v. 0.1
controller module in the control package.
"""

__author__ = "Kirk A Jackson"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2017/12/10 $"
__copyright__ = "Copyright 2017 bristoSOFT all rights reserved."

# import sys
import sip
sip.setapi('QString', 2)
import unittest
import doctest
# from PyQt4.QtGui import QApplication
# from PyQt4.QtTest import QTest
# from PyQt4.QtCore import Qt


# Set sip to version 2


# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
# from PyQt4.QtWebKit import *

from control import internet

def load_tests(loader, tests, ignore):
    '''
    load tests loads docstrings testing from original module and runs the tests.
    '''
    tests.addTests(doctest.DocTestSuite(internet))
    return tests


if __name__ == '__main__':
    unittest.main(verbosity=2)
    
