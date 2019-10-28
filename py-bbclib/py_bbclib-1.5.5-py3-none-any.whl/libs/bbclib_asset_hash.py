# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 beyond-blockchain.org.

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
import os
import sys

import hashlib
import traceback

current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, "../.."))

from bbclib.libs import bbclib_utils
from bbclib import id_length_conf


class BBcAssetHash:
    """AssetHash part in a transaction
    """
    def __init__(self, asset_ids=None, id_length=None):
        self.idlen_conf = id_length_conf.copy()
        if id_length is not None:
            if isinstance(id_length, int):
                for k in self.idlen_conf.keys():
                    self.idlen_conf[k] = id_length
            elif isinstance(id_length, dict):
                for k in id_length.keys():
                    self.idlen_conf[k] = id_length[k]
        self.asset_ids = []
        if asset_ids is not None:
            self.add(asset_ids=asset_ids)

    def __str__(self):
        ret =  "  AssetHash:\n"
        ret += "     num of hashes: %s\n" % len(self.asset_ids)
        for h in self.asset_ids:
            ret += "     asset_id(hash): %s\n" % bbclib_utils.str_binary(h)
        return ret

    def add(self, asset_ids=None):
        """Add parts in this object"""
        if asset_ids is not None and isinstance(asset_ids, list):
            for h in asset_ids:
                self.asset_ids.append(h[:self.idlen_conf["asset_id"]])

    def digest(self):
        """Return digest

        The digest is the first entry of asset_ids

        Returns:
            bytes: asset_id
        """
        return self.asset_ids[0]

    def pack(self):
        """Pack this object

        Returns:
            bytes: packed binary data
        """
        dat = bytearray()
        dat.extend(bbclib_utils.to_2byte(len(self.asset_ids)))
        for h in self.asset_ids:
            dat.extend(bbclib_utils.to_bigint(h, size=self.idlen_conf["asset_id"]))
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
            ptr, num_ids = bbclib_utils.get_n_byte_int(ptr, 2, data)
            for i in range(num_ids):
                ptr, asset_id = bbclib_utils.get_bigint(ptr, data)
                self.asset_ids.append(asset_id)
                self.idlen_conf["asset_id"] = len(asset_id)
        except:
            traceback.print_exc()
            return False
        return True
