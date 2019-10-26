# -*- coding: utf-8 -*-
import pytest

import binascii
import sys
sys.path.extend(["../"])
from bbclib import KeyPair
import bbclib
from bbclib import configure_id_length, validate_transaction_object


user_id = bbclib.get_new_id("user_id_test1")
asset_group_id = bbclib.get_new_id("asset_group_1")
transactions = [None for i in range(20)]
txdata = [None for i in range(20)]
txdata_deserialized = [None for i in range(20)]
keypair1 = KeyPair()
keypair1.generate()


def make_transactions(id_len_conf={}, idlen=None):
    global transactions
    if idlen is None:
        configure_id_length(id_len_conf)
    else:
        bbclib.configure_id_length_all(idlen)
    transactions[0] = bbclib.make_transaction(relation_num=1, witness=True)
    bbclib.add_relation_asset(transactions[0], relation_idx=0, asset_group_id=asset_group_id,
                              user_id=user_id, asset_body=b'transaction_0')
    transactions[0].witness.add_witness(user_id)
    sig = transactions[0].sign(keypair=keypair1, no_pubkey=True)
    transactions[0].witness.add_signature(user_id, sig)
    txdata[0] = bbclib.serialize(transactions[0])

    for i in range(1, 20):
        k = i - 1
        transactions[i] = bbclib.make_transaction(relation_num=1, witness=True)
        bbclib.add_relation_asset(transactions[i], 0, asset_group_id=asset_group_id, user_id=user_id,
                                  asset_body=b'transaction_%d' % i)
        bbclib.add_relation_pointer(transactions[i], 0, ref_transaction_id=transactions[k].transaction_id,
                                    ref_asset_id=transactions[k].relations[0].asset.asset_id)
        transactions[i].witness.add_witness(user_id)
        sig = transactions[i].sign(keypair=keypair1, no_pubkey=True)
        transactions[i].witness.add_signature(user_id, sig)
        txdata[i] = bbclib.serialize(transactions[i])

    bbclib.configure_id_length_all(32)
    for i in range(0, 20):
        txobj, fmt_type = bbclib.deserialize(txdata[i])
        txdata_deserialized[i] = txobj


class TestBBcLib(object):

    def test_01_transaction_len_32(self):
        print("\n-----", sys._getframe().f_code.co_name, "-----")
        make_transactions(idlen=32)
        for i in range(0, 20):
            print("txdata_len: %d" % len(txdata[i]))
            digest = txdata_deserialized[i].digest()
            #print("transaction_id_len: %d" % len(txdata_deserialized[i].transaction_id))
            #print("asset_group_id_len: %d" % len(txdata_deserialized[i].relations[0].asset_group_id))
            #print("user_id_len: %d" % len(txdata_deserialized[i].relations[0].asset.user_id))
            #print("asset_id_len: %d" % len(txdata_deserialized[i].relations[0].asset.asset_id))
            assert len(txdata_deserialized[i].transaction_id) == 32
            assert len(txdata_deserialized[i].relations[0].asset_group_id) == 32
            assert len(txdata_deserialized[i].relations[0].asset.user_id) == 32
            assert len(txdata_deserialized[i].relations[0].asset.asset_id) == 32
            ret = txdata_deserialized[i].signatures[0].verify(digest, pubkey=keypair1.public_key)
            assert ret

    def test_02_transaction_len_16(self):
        print("\n-----", sys._getframe().f_code.co_name, "-----")
        make_transactions(idlen=16)
        for i in range(0, 20):
            print("txdata_len: %d" % len(txdata[i]))
            digest = txdata_deserialized[i].digest()
            #print("transaction_id_len: %d" % len(txdata_deserialized[i].transaction_id))
            #print("asset_group_id_len: %d" % len(txdata_deserialized[i].relations[0].asset_group_id))
            #print("user_id_len: %d" % len(txdata_deserialized[i].relations[0].asset.user_id))
            #print("asset_id_len: %d" % len(txdata_deserialized[i].relations[0].asset.asset_id))
            assert len(txdata_deserialized[i].transaction_id) == 16
            assert len(txdata_deserialized[i].relations[0].asset_group_id) == 16
            assert len(txdata_deserialized[i].relations[0].asset.user_id) == 16
            assert len(txdata_deserialized[i].relations[0].asset.asset_id) == 16
            ret = txdata_deserialized[i].signatures[0].verify(digest, pubkey=keypair1.public_key)
            assert ret

    def test_03_transaction_len_custom(self):
        print("\n-----", sys._getframe().f_code.co_name, "-----")
        id_length = {
            "transaction_id": 24,
            "asset_group_id": 6,
            "user_id": 8,
            "asset_id": 16,
            "nonce": 9
        }
        make_transactions(id_len_conf=id_length)
        for i in range(0, 20):
            print("txdata_len: %d" % len(txdata[i]))
            digest = txdata_deserialized[i].digest()
            #print("transaction_id_len: %d" % len(txdata_deserialized[i].transaction_id))
            #print("asset_group_id_len: %d" % len(txdata_deserialized[i].relations[0].asset_group_id))
            #print("user_id_len: %d" % len(txdata_deserialized[i].relations[0].asset.user_id))
            #print("asset_id_len: %d" % len(txdata_deserialized[i].relations[0].asset.asset_id))
            assert len(txdata_deserialized[i].transaction_id) == id_length["transaction_id"]
            assert len(txdata_deserialized[i].relations[0].asset_group_id) == id_length["asset_group_id"]
            assert len(txdata_deserialized[i].relations[0].asset.user_id) == id_length["user_id"]
            assert len(txdata_deserialized[i].relations[0].asset.asset_id) == id_length["asset_id"]
            ret = txdata_deserialized[i].signatures[0].verify(digest, pubkey=keypair1.public_key)
            assert ret
            ret, _, _ = validate_transaction_object(txdata_deserialized[i])
            assert ret
        print(txdata_deserialized[19])
