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

import six.moves.xmlrpc_client as xmlrpclib
import logging
import re
import ssl


def versionKey(v):
    """
    For a version string with numbers alternated by alphanumeric separators,
    return a tuple containing the separators and the numbers.
    :param v: the project version
    :return: a tuple containing the separators and the numbers
    """
    v = re.findall(r'[-a-zA-Z_.]+|\d+', v)
    return tuple([int(x) if x.isdigit() else x for x in v])


def sortVersions(versionlist, reverse=False):
    """
    Version sorter
    :param versionlist: the list of versions to sort
    :param reverse: if true, return the reverse sorted list
    :return: sorted list of version
    """
    return sorted(versionlist, key=versionKey, reverse=reverse)


class CustomTransportXMLRPC(xmlrpclib.SafeTransport):
    """
    Custom transport layer to include the SSO cookie in the header for XMLRPC
    """
    def __init__(self, cookie=None, *args, **kwargs):
        """
        :param cookie: The SSO Cookie
        """
        self.cookie = cookie
        xmlrpclib.SafeTransport.__init__(self, *args, **kwargs)

    def send_content(self, connection, request_body):
        """
        Custom implementation to add the SSO cookie in the header
        :param connection:
        :param request_body:
        :return:
        """
        if self.cookie:
            connection.putheader("Cookie", self.cookie)
        xmlrpclib.SafeTransport.send_content(self, connection, request_body)


class SoftConfDB():
    def __init__(self, address, cookie=None, noCertVerif=False):
        """
        :param address: The XMLRPC server address
        :param cookie: The SSO Cookie
        """
        context = ssl.create_default_context()
        if noCertVerif:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        self.mTransportLayer = CustomTransportXMLRPC(cookie=cookie,
                                                     context=context)
        self.mProxy = xmlrpclib.ServerProxy(address,
                                            transport=self.mTransportLayer,
                                            allow_none=True)

        self.mSupportedMethods = [m for m in self.mProxy.system.listMethods()
                                  if 'system.' not in m]
        self.log = logging.getLogger()



    def __getattr__(self, name):
        if name in self.mSupportedMethods:
            def wrapper(*args, **kwargs):
                m = getattr(self.mProxy, name)
                return m(*args, **kwargs)
            return wrapper
        else:
            return object.__getattr__(self, name)
