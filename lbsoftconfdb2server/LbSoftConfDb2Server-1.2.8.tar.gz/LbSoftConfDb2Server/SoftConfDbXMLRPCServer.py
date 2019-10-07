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
The script to lunch the XML RPC server in both read only as well as write mode
"""

import logging
try:
    from SimpleXMLRPCServer import SimpleXMLRPCServer, \
        SimpleXMLRPCRequestHandler
except:
    from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from optparse import OptionParser

from LbSoftConfDb2Server.SoftConfDbPermission import getAccessType, \
    ACCESS_TYPE_READ_ONLY, ACCESS_TYPE_WRITE_ALLOWED

from LbSoftConfDb2Server.SoftConfDB import SoftConfDB
from LbSoftConfDb2Server.SoftConfDbLogger import SoftConfDbLogger


class LbSimpleXMLRPCServer(SimpleXMLRPCServer):

    def __init__(self, logger, *args, **kwargs):
        self.logger = logger
        SimpleXMLRPCServer.__init__(self, *args, **kwargs)


class LbSimpleXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):

    def do_POST(self, *args, **kwargs):
        logger = self.server.logger
        logger.setUsername(self.headers.get('ADFS_LOGIN', None))
        SimpleXMLRPCRequestHandler.do_POST(self, *args, **kwargs)


class SoftCondDbXMLRPCServer():
    """XML RPC server of SoftConfDB
    """
    def __init__(self, addr, port, readOnly=True,
                 dbConnectStr=None):
        """
        :param addr: the address on which the XMLRPC server should listen on
        :param port: the port on which the XMLRPC server should listen on
        :param readOnly: flag for the mode of the server. If true, the server
                         performs only read only requests
        :param dbConnectStr: the connection string for the Neo4j database
        """
        self.addr = addr
        self.port = int(port)
        self.log = SoftConfDbLogger()

        if dbConnectStr:
            self.mConfDB = SoftConfDB(dbConnectStr=dbConnectStr,
                                      logger=self.log)
        else:
            self.mConfDB = SoftConfDB(logger=self.log)
        self.server = LbSimpleXMLRPCServer(
            self.log, (self.addr, self.port), allow_none=True,
            requestHandler=LbSimpleXMLRPCRequestHandler)

        methods = []
        # Define the server type
        if readOnly:
            max_allowed_type = ACCESS_TYPE_READ_ONLY
        else:
            max_allowed_type = ACCESS_TYPE_WRITE_ALLOWED

        # Declaration of the exposed methods in XML RPC Server based on the
        # server mode
        for method_name in dir(self.mConfDB):
            method = getattr(self.mConfDB, method_name)
            access_type = getAccessType(method)
            if access_type <= max_allowed_type:
                methods.append(method)
        for method in methods:
            logging.info("Registering method: %s..." % method.__name__)
            self.server.register_function(method, method.__name__)

        self.server.register_introspection_functions()

    def run(self):
        self.server.serve_forever()


def main():
    """Main function to lunch the script"""
    parser = OptionParser(usage="%prog [options]",
                          description="This script manages a simple XML-RPC "
                                      "server which serves queries to the "
                                      "LbSoftConfDB2.")

    parser.add_option("--databaseURI", type="string",
                      help="An URI of the LBSoftConfDB2 Neo4j DB."
                      )
    parser.add_option("--listen", type="string",
                      help="An URI of the XMLRPC Server"
                      )
    parser.add_option("--writeAllowed", action="store_true",
                      help="Flags the server to allow write methods"
                      )
    parser.add_option("--debug", action="store_true",
                      help="Increase verbosity."
                      )
    parser.set_default("databaseURI", None)
    parser.set_default("listen", "localhost:8080")

    # parse command line
    options, args = parser.parse_args()
    logging.basicConfig(format="%(levelname)-8s: %(message)s")

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    addr, port = tuple(options.listen.split(':'))
    dbConnectStr = options.databaseURI
    read_only = True
    if options.writeAllowed:
        read_only = False
    if read_only:
        mode = "read only"
    else:
        mode = "write allowed"
    logging.info("Starting XML-RPC server for the LbSoftConfgDB2 "
                 "in %s mode ..." % mode)
    server = SoftCondDbXMLRPCServer(addr, port, readOnly=read_only,
                                    dbConnectStr=dbConnectStr,)
    logging.info("Listening for '%s' on port '%s'..." % (addr, port))

    try:
        server.run()
    except KeyboardInterrupt:
        logging.info("RPC server stopped by user.")


if __name__ == '__main__':
    main()
