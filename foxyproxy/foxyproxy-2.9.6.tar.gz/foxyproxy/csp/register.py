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

from foxyproxy.csp.ica import CryptoICA
from foxyproxy.csp.pgp import CryptoPGP
from foxyproxy.csp.postsignum import CryptoPostSignum
import logging

logger = logging.getLogger(__name__)


class Register(object):
    """
    Selection of the CSP
    """

    @staticmethod
    def get_service(cmd_params=None):
        """
        Based on cmd line / config parameters, a correct CSP class is loaded
        :param cmd_params:
        :return:
        :rtype: csp.BaseCryptoService
        """
        if cmd_params['signer'].lower() == 'ica':
            return CryptoICA(cmd_params)
        elif cmd_params['signer'].lower() == 'pgp':
            return CryptoPGP(cmd_params)
        elif cmd_params['signer'].lower() == 'postsignum':
            return CryptoPostSignum(cmd_params)
        else:
            logging.error("Unknown signing service requested: %s" % cmd_params['signer'])
            exit(3)
