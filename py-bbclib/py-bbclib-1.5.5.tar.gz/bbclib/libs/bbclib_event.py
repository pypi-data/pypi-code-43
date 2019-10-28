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
import os
import sys

current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, "../.."))

from bbclib.libs import bbclib_utils
from bbclib.libs.bbclib_asset import BBcAsset
from bbclib import id_length_conf


class BBcEvent:
    """Event part in a transaction"""
    def __init__(self, asset_group_id=None, id_length=None):
        self.idlen_conf = id_length_conf.copy()
        if id_length is not None:
            if isinstance(id_length, int):
                for k in self.idlen_conf.keys():
                    self.idlen_conf[k] = id_length
            elif isinstance(id_length, dict):
                for k in id_length.keys():
                    self.idlen_conf[k] = id_length[k]
        if asset_group_id is not None:
            self.asset_group_id = asset_group_id[:self.idlen_conf["asset_group_id"]]
        else:
            self.asset_group_id = None
        self.reference_indices = []
        self.mandatory_approvers = []
        self.option_approver_num_numerator = 0
        self.option_approver_num_denominator = 0
        self.option_approvers = []
        self.asset = None

    def __str__(self):
        ret =  "  asset_group_id: %s\n" % bbclib_utils.str_binary(self.asset_group_id)
        ret += "  reference_indices: %s\n" % self.reference_indices
        ret += "  mandatory_approvers:\n"
        if len(self.mandatory_approvers) > 0:
            for user in self.mandatory_approvers:
                ret += "    - %s\n" % bbclib_utils.str_binary(user)
        else:
            ret += "    - None\n"
        ret += "  option_approvers:\n"
        if len(self.option_approvers) > 0:
            for user in self.option_approvers:
                ret += "    - %s\n" % bbclib_utils.str_binary(user)
        else:
            ret += "    - None\n"
        ret += "  option_approver_num_numerator: %d\n" % self.option_approver_num_numerator
        ret += "  option_approver_num_denominator: %d\n" % self.option_approver_num_denominator
        ret += str(self.asset)
        return ret

    def add(self, asset_group_id=None, reference_index=None, mandatory_approver=None,
            option_approver_num_numerator=0, option_approver_num_denominator=0, option_approver=None, asset=None):
        """Add parts"""
        if asset_group_id is not None:
            self.asset_group_id = asset_group_id[:self.idlen_conf["asset_group_id"]]
        if reference_index is not None:
            self.reference_indices.append(reference_index)
        if mandatory_approver is not None:
            self.mandatory_approvers.append(mandatory_approver[:self.idlen_conf["user_id"]])
        if option_approver_num_numerator > 0:
            self.option_approver_num_numerator = option_approver_num_numerator
        if option_approver_num_denominator > 0:
            self.option_approver_num_denominator = option_approver_num_denominator
        if option_approver is not None:
            self.option_approvers.append(option_approver[:self.idlen_conf["user_id"]])
        if asset is not None:
            self.asset = asset
        return True

    def pack(self):
        """Pack this object

        Returns:
            bytes: packed binary data
        """
        if self.asset_group_id is None:
            raise Exception("need asset_group_id in BBcEvent")
        dat = bytearray(bbclib_utils.to_bigint(self.asset_group_id, size=self.idlen_conf["asset_group_id"]))
        dat.extend(bbclib_utils.to_2byte(len(self.reference_indices)))
        for i in range(len(self.reference_indices)):
            dat.extend(bbclib_utils.to_2byte(self.reference_indices[i]))
        dat.extend(bbclib_utils.to_2byte(len(self.mandatory_approvers)))
        for i in range(len(self.mandatory_approvers)):
            dat.extend(bbclib_utils.to_bigint(self.mandatory_approvers[i], size=self.idlen_conf["user_id"]))
        dat.extend(bbclib_utils.to_2byte(self.option_approver_num_numerator))
        dat.extend(bbclib_utils.to_2byte(self.option_approver_num_denominator))
        for i in range(self.option_approver_num_denominator):
            dat.extend(bbclib_utils.to_bigint(self.option_approvers[i], size=self.idlen_conf["user_id"]))
        ast = self.asset.pack()
        dat.extend(bbclib_utils.to_4byte(len(ast)))
        dat.extend(ast)
        return bytes(dat)

    def unpack(self, data):
        """Unpack into this object

        Args:
            data (bytes): packed binary data
        Returns:
            bool: True if successful
        """
        ptr = 0
        id_length_asgid = 32
        id_length_userid = 32
        data_size = len(data)
        try:
            ptr, self.asset_group_id = bbclib_utils.get_bigint(ptr, data)
            self.idlen_conf["asset_group_id"] = len(self.asset_group_id)
            ptr, ref_num = bbclib_utils.get_n_byte_int(ptr, 2, data)
            self.reference_indices = []
            for i in range(ref_num):
                ptr, idx = bbclib_utils.get_n_byte_int(ptr, 2, data)
                self.reference_indices.append(idx)
                if ptr >= data_size:
                    return False
            ptr, appr_num = bbclib_utils.get_n_byte_int(ptr, 2, data)
            self.mandatory_approvers = []
            for i in range(appr_num):
                ptr, appr = bbclib_utils.get_bigint(ptr, data)
                self.idlen_conf["user_id"] = len(appr)
                self.mandatory_approvers.append(appr)
                if ptr >= data_size:
                    return False
            ptr, self.option_approver_num_numerator = bbclib_utils.get_n_byte_int(ptr, 2, data)
            ptr, self.option_approver_num_denominator = bbclib_utils.get_n_byte_int(ptr, 2, data)
            self.option_approvers = []
            for i in range(self.option_approver_num_denominator):
                ptr, appr = bbclib_utils.get_bigint(ptr, data)
                self.idlen_conf["user_id"] = len(appr)
                self.option_approvers.append(appr)
                if ptr >= data_size:
                    return False
            ptr, astsize = bbclib_utils.get_n_byte_int(ptr, 4, data)
            ptr, astdata = bbclib_utils.get_n_bytes(ptr, astsize, data)
            self.asset = BBcAsset()
            self.asset.unpack(astdata)
        except:
            return False
        return True
