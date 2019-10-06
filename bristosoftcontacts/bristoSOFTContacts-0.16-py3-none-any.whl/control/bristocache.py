#!/usr/bin/python3
#
# Copyright 2018 Kirk A Jackson DBA bristoSOFT all rights reserved.  All methods,
# techniques, algorithms are confidential trade secrets under Ohio and U.S.
# Federal law owned by bristoSOFT.
#
# Kirk A Jackson dba bristoSOFT
# 4100 Executive Park Drive
# Suite 11
# Cincinnati, OH  45241
# Phone (513) 401-9114
# email jacksonkirka@bristosoft.com
#
# The trade name bristoSOFT is a registered trade name with the State of Ohio
# document No. 201607803210.
#
'''
bristoSOFT cache module that implements a comprehensive cache system based on time
other factors.
'''
__author__ = "Kirk A Jackson"
__copyright__ = "Copyright 2018 bristoSOFT all rights reserved."
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Kirk A Jackson"
__email__ = "jacksonkirka@gmail.com"
__status__ = "Development"

import datetime

class bristoCache(dict, object):

    def __init__(self, _size,  parent=None):
        '''
        Constructor for class.
        '''
        self.max_cache_size = _size


    def update(self, key):
        '''
        update adds a Python object to the cache using a key identifier.
        '''
        pass


