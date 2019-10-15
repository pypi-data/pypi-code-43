#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs Ltd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Smart Arcs <support@smartarchitects.co.uk>, May 2018
"""
__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

import os
import logging

from foxyproxy.upstream.globalplatform import GlobalPlatformPro, GlobalPlatformProConfig
from foxyproxy.upstream.cloudfoxy import CloudFoxyConfig, CloudFoxy
from foxyproxy.upstream.linuxshell import LinuxShellConfig, LinuxShell
from foxyproxy.upstream.pythoncard import PythonCard, PythonCardConfig

logger = logging.getLogger(__name__)


class RegisterUpstream(object):
    """
    Add a description
    """

    @staticmethod
    def get_service(upstream, token=None, signer=None):
        """

        :param upstream: value stored in cmd_params['upstream']
        :type upstream: str
        :param token: value stored in cmd_params['token']
        :type token: str
        :param signer:
        :type signer:
        :return:
        """
        upstream_address = upstream.split('://')
        if (len(upstream_address) < 2) and (upstream_address[0] != 'python'):
            logging.error("Upstream signer is not in the correct format")
            return None

        if upstream_address[0].lower() == "file":
            # it's a file - let's see if it's a GPPro or a shell script or something else
            filename, file_extension = os.path.splitext(upstream_address[1])

            # GPPro - or similar - it's a jar file -> server config adds java to the command string
            if file_extension.lower() == 'jar':
                if token is None:
                    server_config = GlobalPlatformProConfig(upstream_address[1])
                else:
                    logging.info('GPPro signer doesn\'t support authorization tokens')
                    server_config = GlobalPlatformProConfig(upstream_address[1])

                server = GlobalPlatformPro(server_config)

            # anything else is assumed to be a shell command - without need for any interpreter
            else:
                if token is None:
                    server_config = LinuxShellConfig(upstream_address[1])
                else:
                    logging.info('Linux shell script doesn\'t support authorization tokens')
                    server_config = LinuxShellConfig(upstream_address[1], token)
                server = LinuxShell(server_config)
        elif upstream_address[0].lower() == 'python':
            server_config = PythonCardConfig(upstream, signer)
            server = PythonCard(server_config)
        else:
            if token is None:
                server_config = CloudFoxyConfig(upstream)
            else:
                server_config = CloudFoxyConfig(upstream, token)
            server = CloudFoxy(server_config)

        return server
