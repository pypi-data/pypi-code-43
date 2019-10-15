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
from foxyproxy.csp.base_csp import BaseCryptoService

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'


class CryptoTestSmartcard(BaseCryptoService):
    """
    A test class for smartcards
    """
    def init(self, session, config=None):
        """
        As defined in the abstract class
        :param session:
        :param config:
        """
        pass

    def sign(self, session, alias, fingerprint, password=None, hash_alg=None, sign_alg=None):
        """
        As defined in the abstract class

        :param session:
        :param alias:
        :param fingerprint:
        :param password:
        :param hash_alg:
        :param sign_alg:
        """
        pass

    def aliases(self):
        """
        As defined in the abstract class

        """
        pass

    def chain(self, alias, sign_alg=0):
        """
        As defined in the abstract class

        :param alias:
        :param sign_alg:
        """
        pass

    def reset(self, session, token):
        """
        As defined in the abstract class

        :param session:
        :param token:
        :return:
        """
        # test response, send instead of the CloudFoxy
        response_data = "621A82013883023F008404524F4F5485030079AD8A0105A1038B01019000"
        return response_data

    def apdu(self, session, token, command):
        """
        As defined in the abstract class

        :param session:
        :param token:
        :param command:
        :return:
        """
        response_data = "102030409000"

        return response_data
