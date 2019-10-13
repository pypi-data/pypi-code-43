#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
***
Module:
***
"""

# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018

__author__ = "Petr Svenda, Smart Arcs"
__copyright__ = 'Enigma Bridge Ltd, Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Beta'

# Based on Simple socket upstream using threads by Silver Moon
# (https://www.binarytides.com/python-socket-server-code-example/)
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)
# fh = logging.FileHandler('foxyproxy.log')
# fh.setLevel(logging.INFO)
# logger.addHandler(fh)

# logging.basicConfig(level=logging.DEBUG)


class BaseUpstream(object):
    """
    Abstract class for upstream signers
    """
    def __init__(self, server_config):
        """
        :type server_config: type(BaseUpstreamConfig)
        """
        self.server = server_config  # Type[BaseUpstreamConfig]
        pass

    def init(self):
        """
        An additional init of instances - at any time later
        :return:
        """
        pass

    def getupstreamconnection(self):
        """
        Returns an upstream TCP/HTTP connection, or None
        :return:
        """
        return NotImplementedError("Please implement 'getupstreamconnection'")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def closeupstreamconnection(self, session):
        """
        Closes a session / upstream connection
        :param session:
        :return:
        """
        return NotImplementedError("Please implement 'closeupstreamconnection' in your upstream server class")

    def cmd(self, session, command, terminal, reset=0):
        """
        :param session:
        :type session: None|requests.Session
        :param command:
        :type command: str|list|None
        :param terminal: the identification of the token
        :type terminal: str
        :param reset: a flag wither the token should be reset before the command execution
        :type reset: int
        :return:
        :rtype list
        """
        return NotImplementedError("Please implement 'cmd'")

    def set_uptime(self):
        """
        Flags the server as refreshed
        :return:
        """
        if self.server:
            self.server.stale = False

    def is_up(self):
        """
        Returns True if the upstream server is available. It can be down or being updated.
        :return:
        """
        return not self.server.stale

    def is_down(self, session):
        """
        If the upstream server can be down, this method needs to be implemented in its handler class
        :type session: None|requests.Session
        :return:
        """
        return False

    def downtime(self, session):
        """
        Checks if the signer has been reset since the last time
        :type session: requests.Session
        :return:
        """
        return NotImplementedError("Please implement 'downtime'")

    def inventory(self, session):
        """
        Returns a list of available signers

        :type session: None|requests.Session
        :return:
        """
        return NotImplementedError("Please implement 'inventory'")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def refresh(self, session):
        """
        Request a refresh of all available signers
        :type session: None|requests.Session
        :return:
        """
        return NotImplementedError("Please implement 'refresh'")


class BaseUpstreamConfig(object):
    """
    Abstract class for upstream signer configuration
    """
    def __init__(self):
        """
        An object to hide all relevant configuration parameters.
        """

        # a flag showing, whether the configuration of the upstream server / crypto providers needs to be updated
        self.stale = True
        pass
