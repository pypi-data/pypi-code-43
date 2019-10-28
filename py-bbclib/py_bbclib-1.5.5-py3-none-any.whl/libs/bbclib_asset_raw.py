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


class BBcAssetRaw:
    """AssetRaw part in a transaction

    In this object, asset_id should be given externally, meaning that this object does not care about how to calculate the digest.
    """
    def __init__(self, asset_id=None, asset_body=None, id_length=None):
        self.idlen_conf = id_length_conf.copy()
        if id_length is not None:
            if isinstance(id_length, int):
                for k in self.idlen_conf.keys():
                    self.idlen_conf[k] = id_length
            elif isinstance(id_length, dict):
                for k in id_length.keys():
                    self.idlen_conf[k] = id_length[k]
        self.asset_id = None
        self.asset_body_size = 0
        self.asset_body = None
        self.add(asset_id=asset_id, asset_body=asset_body)

    def __str__(self):
        ret =  "  AssetRaw:\n"
        ret += "     asset_id: %s\n" % bbclib_utils.str_binary(self.asset_id)
        ret += "     body_size: %d\n" % self.asset_body_size
        ret += "     body: %s\n" % self.asset_body
        return ret

    def add(self, asset_id=None, asset_body=None):
        """Add parts in this object"""
        if asset_id is not None:
            self.asset_id = asset_id[:self.idlen_conf["asset_id"]]
        if asset_body is not None:
            self.asset_body = asset_body
            if isinstance(asset_body, str):
                self.asset_body = asset_body.encode()
            self.asset_body_size = len(asset_body)

    def digest(self):
        """Return digest

        The digest corresponds to the asset_id of this object.
        The asset_id is given externally, so bbclib does not care about how to calculate the digest of the asset_body.

        Returns:
            bytes: asset_id
        """
        return self.asset_id

    def pack(self):
        """Pack this object

        Returns:
            bytes: packed binary data
        """
        dat = bytearray()
        dat.extend(bbclib_utils.to_bigint(self.asset_id, size=self.idlen_conf["asset_id"]))
        dat.extend(bbclib_utils.to_2byte(self.asset_body_size))
        if self.asset_body_size > 0:
            dat.extend(self.asset_body)
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
            ptr, self.asset_id = bbclib_utils.get_bigint(ptr, data)
            self.idlen_conf["asset_id"] = len(self.asset_id)
            ptr, self.asset_body_size = bbclib_utils.get_n_byte_int(ptr, 2, data)
            if self.asset_body_size > 0:
                ptr, self.asset_body = bbclib_utils.get_n_bytes(ptr, self.asset_body_size, data)
        except:
            traceback.print_exc()
            return False
        return True
