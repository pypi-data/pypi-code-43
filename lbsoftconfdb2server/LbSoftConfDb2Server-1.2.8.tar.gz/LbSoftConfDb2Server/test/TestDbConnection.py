###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Test of the database connection string in the LbSoftConfDb2 main class

@author: Stefan-Gabriel Chitic
'''
import shutil
import unittest

import os

from LbSoftConfDb2Server.SoftConfDB import get_connection, _get_pwd_from_sys


class TestDbConnection(unittest.TestCase):

    def setUp(self):
        self.home = os.environ["HOME"]
        os.environ["HOME"] = '/tmp/'
        if not os.path.exists('/tmp/private/'):
            os.mkdir('/tmp/private/')
        if 'NEO4JHOST' in os.environ.keys():
            os.environ.pop('NEO4JHOST')

    def tearDown(self):
        os.environ["HOME"] = self.home
        shutil.rmtree('/tmp/private')

    def testGetPwdFromSys(self):
        """ Test password and username configuration"""
        # No environment string, no config file should raise an exception
        self.assertRaises(Exception, _get_pwd_from_sys)

        # No environment string
        with open('/tmp/private/neo4j.txt', 'w') as f:
            f.write('admin/toto')
        user, pwd = _get_pwd_from_sys()
        self.assertEqual(user, 'admin')
        self.assertEqual(pwd, 'toto')

        # Environment string
        os.environ['NEO4JPWD'] = 'admin/fifi'
        user, pwd = _get_pwd_from_sys()
        self.assertEqual(user, 'admin')
        self.assertEqual(pwd, 'fifi')

    def testGetConnection(self):
        with open('/tmp/private/neo4j.txt', 'w') as f:
            f.write('admin/toto')
        # Test with no environmental config
        dbString = get_connection()
        self.assertEqual(
            dbString,
            "bolt://admin:toto@lbsoftdb.cern.ch:7687/db/data/")

        # Test with environmental config
        os.environ['NEO4JHOST'] = 'localhost'
        os.environ['NEO4JPORT'] = '8080'
        dbString = get_connection()
        self.assertEqual(
            dbString,
            "bolt://admin:toto@localhost:8080/db/data/")


if __name__ == "__main__":
    unittest.main()
