#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 12:00:00 2019
        
COTOHA API for Python3.8
@author: Nicolas Toba Nozomi
@id: 278mt
"""
    
class CotohapPyError(Exception):
    """CotohapPy exception"""

    def __init__(self, reason: str):

        self.reason = reason
        super(CotohapPyError, self).__init__(reason)


    def __str__(self):

        return self.reason

