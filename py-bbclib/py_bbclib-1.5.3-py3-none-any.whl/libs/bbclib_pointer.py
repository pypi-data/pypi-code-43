# -*- coding: utf-8 -*-
"""
Copyright (c) 2018 beyond-blockchain.org.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, "../.."))
from bbclib.libs import bbclib_utils
import bbclib
from bbclib import id_length_conf


class BBcPointer:
    """Pointer part in a transaction"""
    def __init__(self, transaction_id=None, asset_id=None, id_length=None):
        if id_length is not None:
            bbclib.configure_id_length_all(id_length)
        if transaction_id is not None:
            self.transaction_id = transaction_id[:id_length_conf["transaction_id"]]
        else:
            self.transaction_id = None
        if asset_id is not None:
            self.asset_id = asset_id[:id_length_conf["asset_id"]]
        else:
            self.asset_id = None

    def __str__(self):
        ret =  "     transaction_id: %s\n" % bbclib_utils.str_binary(self.transaction_id)
        ret += "     asset_id: %s\n" % bbclib_utils.str_binary(self.asset_id)
        return ret

    def add(self, transaction_id=None, asset_id=None):
        """Add parts"""
        if transaction_id is not None:
            self.transaction_id = transaction_id[:id_length_conf["transaction_id"]]
        if asset_id is not None:
            self.asset_id = asset_id[:id_length_conf["asset_id"]]

    def pack(self):
        """Pack this object

        Returns:
            bytes: packed binary data
        """
        dat = bytearray(bbclib_utils.to_bigint(self.transaction_id, size=id_length_conf["transaction_id"]))
        if self.asset_id is None:
            dat.extend(bbclib_utils.to_2byte(0))
        else:
            dat.extend(bbclib_utils.to_2byte(1))
            dat.extend(bbclib_utils.to_bigint(self.asset_id, size=id_length_conf["asset_id"]))
        return bytes(dat)

    def unpack(self, data):
        """Unpack into this object

        Args:
            data (bytes): packed binary data
        Returns:
            bool: True if successful
        """
        ptr = 0
        try:
            ptr, self.transaction_id = bbclib_utils.get_bigint(ptr, data)
            ptr, num = bbclib_utils.get_n_byte_int(ptr, 2, data)
            if num == 1:
                ptr, self.asset_id = bbclib_utils.get_bigint(ptr, data)
                id_length_conf["asset_id"] = len(self.asset_id)
            else:
                self.asset_id = None
        except:
            return False
        return True

