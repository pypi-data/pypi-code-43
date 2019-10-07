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
import json
import logging
import shutil
import subprocess
import unittest

import os
from LbSoftConfDb2Server.Neo4jEnvSetup import Neo4jEnvSetup

from LbSoftConfDb2Server.test.MockLogger import MockLoggingHandler


class TestNeo4JEnvSetup(unittest.TestCase):
    def setUp(self):
        # Uncomment the next line if and only if you have no demon started
        # os.environ['long_test'] = 'True'
        os.environ["HOME"] = '/tmp/'
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        self.setup = Neo4jEnvSetup('/tmp/test_neo4j')

    def tearDown(self):
        # Stop any started server
        try:
            p = subprocess.Popen([self.setup.neo4j_exec, "stop"],
                                 stdout=subprocess.PIPE)
            out, err = p.communicate()
        except:
            pass
        if os.path.exists('/tmp/test_neo4j'):
            shutil.rmtree('/tmp/test_neo4j')

    def testDownload(self):
        """ Test if the file is correctly downloaded"""
        if not os.environ.get('long_test', None):
            return
        if not os.path.exists('/tmp/test_neo4j'):
            os.mkdir('/tmp/test_neo4j')
        res = self.setup._download_file(
            'http://lhcb-rpm.web.cern.ch/lhcb-rpm/neo4j.tar.gz',
            dest='/tmp/test_neo4j'
        )
        self.assertEqual(res, '/tmp/test_neo4j/neo4j.tar.gz')
        self.assertTrue(os.path.exists(res))

    def testInitialConfig(self):
        """ Test if the initial configuration is correctly setup"""
        if not os.environ.get('long_test', None):
            return
        self.setup._download_and_init()
        self.assertTrue(os.path.exists(
            '/tmp/test_neo4j/neo4j-community-3.4.6/bin/neo4j'))
        self.assertTrue(os.path.exists('/tmp/private/neo4j.txt'))
        with open(os.path.expandvars("$HOME/private/neo4j.txt"), 'r') as f:
            self.assertEqual(f.readlines()[0], 'neo4j/lbneo4j')

    def testSetup(self):
        """ Test if all the process of download, configuration and startup is
            executed correctly
        """
        if not os.environ.get('long_test', None):
            return
        self.setup.setup()
        self.assertTrue(os.path.exists(
            '/tmp/test_neo4j/running.pid'))
        self._check_if_running()

    def testInit(self):
        """ Test if everything is running correctly and we have only one
        process per configuration running
        """
        if not os.environ.get('long_test', None):
            return
        # First fire up a server
        self.setup.start()
        self.assertEqual(
            ["[Errno 2] No such file or directory: "
             "u'/tmp/test_neo4j/running.pid'"], self.handler.messages['error'])

        self._check_if_running()
        # Second fire up should result in a already running message
        self.setup.start()
        self.assertEqual(self.handler.messages['info'][-1],
                         'Configuration already running...')
        self._check_if_running()
        current_pid = self._get_current_pid()

        # Stop the sever and run again
        try:
            p = subprocess.Popen([self.setup.neo4j_exec, "stop"],
                                 stdout=subprocess.PIPE)
            p.communicate()
        except:
            self.fail("Process not running")
        self.setup.start()
        new_pid = self._get_current_pid()
        self.assertNotEqual(current_pid, new_pid)
        self._check_if_running()

    def _get_current_pid(self):
        with open('/tmp/test_neo4j/running.pid', 'r') as f:
            data = json.load(f)
            return data['LOCALNEO4JPID']

    def _check_if_running(self):
        """ Internal function to check if the demon is running"""
        pid = self._get_current_pid()
        try:
            os.kill(int(pid), 0)
        except:
            self.fail("Process neo4j not running")


if __name__ == "__main__":
    unittest.main()
