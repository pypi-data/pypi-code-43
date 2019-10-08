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
Generic client that will be extended by a all LbSoftConfDb2 clients.
It is used to creat the read only and write allowed instances of SoftConfDB
(local or XMLRPC) as well as to get the SSO auth for the write instance.
"""
from LbCommon.Script import Script
import sys
import os
import subprocess
import time
import logging


class LbSoftConfDbBase(object):

    def __init__(self,
                 RO_address='https://lbsoftdb.cern.ch/read/',
                 RW_address='https://lbsoftdb.cern.ch/write/',
                 *args, **kwargs):
        """
        :param server_mode: flag to set to requests to a READ ONLY server or to
                            WRITE_ALLOWED server
        :param serverAddress: the LBSoftCondfDB2 server address
        """
        self.RO_address = RO_address
        self.RW_address = RW_address
        self.mConfDB_RW = None
        self.mConfDB_RO = None

    def getROInterface(self, noxmlrpc=False, dbConnectStr=None,
                       noCertVerif=False):
        """
        :return: the read only interface for the Neo4j DB"
        """
        if not self.mConfDB_RO:
            if noxmlrpc:
                self.mConfDB_RO = self._getNOXMLRPCInterface(
                    dbConnectStr=dbConnectStr)
            else:
                from LbSoftConfDb2Clients.SoftConfDB import SoftConfDB
                self.mConfDB_RO = SoftConfDB(self.RO_address,
                                             noCertVerif=noCertVerif)
        return self.mConfDB_RO

    def getRWInterface(self, noxmlrpc=False, dbConnectStr=None,
                       noCertVerif=False):
        """
        :return: the read write interface for the Neo4j DB"
        """
        if not self.mConfDB_RW:
            if noxmlrpc:
                self.mConfDB_RW = self._getNOXMLRPCInterface(
                    dbConnectStr=dbConnectStr)
            else:
                from LbSoftConfDb2Clients.SoftConfDB import SoftConfDB
                cookie = self._check_cookie()
                self.mConfDB_RW = SoftConfDB(self.RW_address, cookie=cookie,
                                             noCertVerif=noCertVerif)
        return self.mConfDB_RW

    def _getNOXMLRPCInterface(self, dbConnectStr=None):
        db_interface = None
        try:
            from LbSoftConfDb2Server.SoftConfDB import SoftConfDB
            # init of the write allowed SoftConfDB instance
            db_interface = SoftConfDB(dbConnectStr=dbConnectStr)
        except ImportError as e:
            raise Exception("Clinets are run on different machine that the "
                            "server address. Please use the XML RPC or "
                            "install a local instance of the server")
        return db_interface

    def _get_cookie_path(self):
        '''
        :return: The path for the server cookie on local disk
        '''
        return os.sep + os.path.join('tmp', os.environ['USER'],
                                     "ssocookie-lbsoftconfdb.txt")

    def _download_cookie(self, url, path):
        """
        Invoke cern-get-sso-cookie to save the server cookie to path
        :param url: the url for the sso cookie
        :param path: the path where to save the cookie
        """
        cmd = ["cern-get-sso-cookie", "--krb", "-u", url, "--reprocess", "-o",
               path]
        subprocess.check_call(cmd)

    def _check_cookie(self):
        """ Check whether we have a valid server cookie.
        If not, download one using the cern-get-sso-cookie command
        :return: the cookie for authentication
        """
        reload_cookie = False
        cookie_file_path = self._get_cookie_path()
        try:
            mtime = os.path.getmtime(cookie_file_path)
            if time.time() - mtime > 3600:
                reload_cookie = True
        except OSError:
            # In this case the file probably does not exist...
            reload_cookie = True

        if reload_cookie:
            url = 'https://lbsoftdb.cern.ch/write/'
            self._download_cookie(url, cookie_file_path)

        return self._get_cookie(cookie_file_path)

    def _get_cookie(self, cookie_file_path):
        """
        Gets the cookie data from the cookie_file_path
        :param cookie_file_path:  the path of cookie for authentication
        :return: the cookie data
        """
        """ A function to fetch the sso cookie for server. """
        result = ""
        if not os.path.exists(cookie_file_path):
            logging.debug(
                "No SSO cookie found for Neo4j at {0}, "
                "trying to connect to Neo4j without it.."
                .format(cookie_file_path))
            return result
        else:
            logging.debug(
                "Found SSO cookie for Neo4j at {0}".format(cookie_file_path))

        with open(cookie_file_path) as f:
            line = f.readline()
            while line:
                if line.startswith('#'):
                    line = f.readline()
                    continue
                splitted_line = line.rstrip('\n').split('\t')

                for s in splitted_line:
                    if s.startswith('_saml_idp') or s.startswith(
                            '_shibsession_'):
                        if result:
                            result += '; '
                        result += s + '=' + splitted_line[
                            splitted_line.index(s) + 1]
                        break
                line = f.readline()
        return result


class LbSoftConfDbBaseClient(Script):
    """
    Generic client for LbSoftConfDB2 clients
    """

    def __init__(self,
                 RO_address='https://lbsoftdb.cern.ch/read/',
                 RW_address='https://lbsoftdb.cern.ch/write/',
                 *args, **kwargs):
        """
        :param server_mode: flag to set to requests to a READ ONLY server or to
                            WRITE_ALLOWED server
        :param serverAddress: the LBSoftCondfDB2 server address
        """
        logging.basicConfig(level=logging.DEBUG)
        Script.__init__(self, *args, **kwargs)
        parser = self.parser
        parser.add_option("--noxmlrpc",
                          dest="noxmlrpc",
                          default=False,
                          action="store_true",
                          help="Use the direct interface to Neo4j "
                               "instead of XMLRPC")
        parser.add_option("--databaseURL",
                          dest="dbConnectStr",
                          default=None,
                          action="store",
                          help="Custom Neo4j database URL")
        parser.add_option("--nocertcheck",
                          dest="nocertcheck",
                          default=False,
                          action="store_true",
                          help="Avoid certification verification in python")
        parser.add_option("-d",
                          dest="debug",
                          action="store_true",
                          help="Display debug output")
        self.db_clinet = LbSoftConfDbBase(RO_address=RO_address,
                                          RW_address=RW_address)
        self.log = logging.getLogger()

    def getROInterface(self):
        """
        :return: the read only interface for the Neo4j DB"
        """
        return self.db_clinet.getROInterface(
            noxmlrpc=self.options.noxmlrpc,
            dbConnectStr=self.options.dbConnectStr,
            noCertVerif=True
        )

    def getRWInterface(self):
        """
        :return: the read write interface for the Neo4j DB"
        """
        return self.db_clinet.getRWInterface(
            noxmlrpc=self.options.noxmlrpc,
            dbConnectStr=self.options.dbConnectStr,
            noCertVerif=self.options.nocertcheck
        )

    def run(self, args=sys.argv[1:]):
        """
        Custom implementation of the run functions from Scripts
        :param args:
        :return:
        """
        self.parseOpts(args)
        if self.options.debug:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)
        if self.options.nocertcheck:
            self.db_clinet.noCertVerif = self.options.nocertcheck
        Script.run(self, args=args)
