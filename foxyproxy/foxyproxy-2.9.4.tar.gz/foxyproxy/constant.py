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
 Written by Dan Cvrcek <support@keychest.net>, 2019
"""
import datetime

__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@keychest.net'
__status__ = 'Development'


class Constant(object):
    """
    Global constants
    """
    CMD_APDU = "APDU"
    CMD_RESET = "RESET"  # requests smartcard reset
    CMD_SIGN = "SIGN"  # requests eIDAS signature
    CMD_CHAIN = "CHAIN"  # requests certificate chain from a given smart card
    CMD_ALIAS = "ALIASES"  # requests all names from certificates
    CMD_ENUM = "ENUM"  # requests a list of readers with valid certificates
    CMD_CLIENT = "PERSONALIZE"  # identifies the application / client - used to prioritize list of cards sent back
    CMD_LIST = "READERS"  # requests all readers

    CMD_SEPARATOR = ":"
    CMD_LINE_SEPARATOR = "|"
    CMD_RESPONSE_END = "\n@@"

    CMD_NO_CARD = "C080"  # no card - from upstream
    CMD_RESPONSE_FAIL = "C081"
    CMD_VAGUE_NAME = "C082"
    CMD_READER_NOT_FOUND = "C083"
    CMD_READER_WRONG_DATA = "C084"
    CMD_READER_WRONG_PIN = "C085"
    CMD_UPSTREAM_ERROR = "C086"
    CMD_INTERNAL_ERROR = "C090"
    CMD_OK = "9000"

    @staticmethod
    def unix_time(dt):
        """
        Get a unix_time regardless of the timezone
        :param dt:
        :return:
        """
        if dt is None:
            return None
        cur = datetime.datetime.utcfromtimestamp(0)
        if dt.tzinfo is not None:
            cur.replace(tzinfo=dt.tzinfo)
        else:
            cur.replace(tzinfo=None)
        # noinspection PyBroadException
        try:
            return (dt - cur).total_seconds()
        except Exception:
            pass
