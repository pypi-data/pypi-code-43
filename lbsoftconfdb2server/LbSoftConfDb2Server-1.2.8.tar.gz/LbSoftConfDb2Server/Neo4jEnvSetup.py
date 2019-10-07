#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""
Setup script for local instance of a Neo4j database. Development and testing
only
"""

from __future__ import division, absolute_import, print_function,\
    unicode_literals

import sys
import os
import tempfile
import time
import shutil
import subprocess
import tarfile
import re
import json
import logging

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse


class Neo4jEnvSetup:

    def __init__(self, neo4j_path, db_path='graph.db',
                 port='7687'):
        """
        :param neo4j_path: the path where the server should be installed
        :param db_path: the database path
        :param port: the port for the neo4j server to listen on
        """
        self.neo4j_path = neo4j_path
        self.db_path = db_path
        self.port = port
        self.logger = logging.getLogger()

    def start(self):
        """
        Start function for the neo4j server to listen
        """
        try:
            with open('%s/running.pid' % self.neo4j_path, 'r') as f:
                conf = json.load(f)
                running_pid = conf.get('LOCALNEO4JPID', None)
                if running_pid and self.isProcessRunning(int(running_pid)):
                    db_path = conf.get('LOCALNEO4JDBPATH', None)
                    port = conf.get('LOCALNEO4JPORT', None)
                    if db_path == self.db_path and port == self.port:
                        logging.info("Configuration already running...")
                        return
        except Exception as f:
            logging.error(f)
        self.setup()

    def setup(self):
        """
        Setup function for the neo4j server
        """
        # Check if already installed
        if not os.path.exists(self.neo4j_path):
            self._download_and_init()

        self.neo4j_exec = os.path.join(self.neo4j_path,
                                       'neo4j-community-3.4.6',
                                       'bin', 'neo4j')
        self.neo4j_conf = os.path.join(self.neo4j_path,
                                       'neo4j-community-3.4.6',
                                       'conf', 'neo4j.conf')
        # stop existing server
        p = subprocess.Popen([self.neo4j_exec, "stop"],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        if err is None:
            err = ''
        logging.info("Stopping server: %s%s" % (out, err))

        # set new db path, listen address and port
        with open(self.neo4j_conf, 'r') as f:
            lines = f.readlines()
        with open(self.neo4j_conf, 'w') as f:
            for line in lines:
                if 'dbms.connector.bolt.listen_address' in line:
                    line = 'dbms.connector.bolt.listen_address=:%s\n' % (
                        self.port)
                if 'dbms.active_database' in line:
                    line = 'dbms.active_database=%s\n' % self.db_path
                f.write(line)

        # start new server
        p = subprocess.Popen([self.neo4j_exec, "start"],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        pid = None
        if err is None:
            err = ''
            out = out.decode('utf-8')
            pid = re.search('pid ([0-9]*)', out).group(1)
        logging.info("Starting server: %s%s" % (out, err))
        if pid:
            with open('%s/running.pid' % self.neo4j_path, 'w') as f:
                conf = {}
                conf['LOCALNEO4JPID'] = str(pid)
                conf['LOCALNEO4JPORT'] = self.port
                conf['LOCALNEO4JDBPATH'] = self.db_path
                json.dump(conf, f)

    def _download_file(self, url, dest=None):
        """
        Download and save a file specified by url to dest directory,
        :param url: the url of the file to be downloaded
        :param dest: the destination where the file should be saved
        :return: the filename where the file was saved to
        """
        u = urllib2.urlopen(url)

        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        filename = os.path.basename(path)
        if not filename:
            filename = 'downloaded.file'
        if dest:
            filename = os.path.join(dest, filename)

        with open(filename, 'wb') as f:
            meta = u.info()
            meta_func = meta.getheaders if hasattr(
                meta, 'getheaders') else meta.get_all
            meta_length = meta_func("Content-Length")
            file_size = None
            if meta_length:
                file_size = int(meta_length[0])
            logging.info("Downloading: {0} Bytes: {1}".format(url, file_size))

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)

                status = "{0:16}".format(file_size_dl)
                if file_size:
                    status += "   [{0:6.2f}%]".format(
                        file_size_dl * 100 / file_size)
                status += chr(13)
                print(status, end="")
        return filename

    def _download_and_init(self):
        """
        Download the neo4j archive and init the configuration
        """
        # Download
        url = 'http://lhcb-rpm.web.cern.ch/lhcb-rpm/neo4j.tar.gz'
        tmp_folder = tempfile.mkdtemp()
        filename = self._download_file(url, dest=tmp_folder)
        tar = tarfile.open(filename)
        tar.extractall(self.neo4j_path)
        shutil.rmtree(tmp_folder)

        self.neo4j_admin = os.path.join(self.neo4j_path,
                                        'neo4j-community-3.4.6',
                                        'bin', 'neo4j-admin')
        # set default password

        p = subprocess.Popen([self.neo4j_admin,
                              "set-initial-password", "lbneo4j"],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        if err is None:
            err = ''
        logging.info("Init server: %s\n%s" % (out, err))

        # set the credentials
        if not os.path.exists(os.path.expandvars("$HOME/private/")):
            os.mkdir(os.path.expandvars("$HOME/private/"))
        with open(os.path.expandvars("$HOME/private/neo4j.txt"), 'w') as f:
            f.write(str('neo4j/lbneo4j'))

    def isProcessRunning(self, pid):
        """
        Check For the existence of a unix pid.
        :param pid: the pid of the process
        :return: True if the process is running, False otherwise
        """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True
