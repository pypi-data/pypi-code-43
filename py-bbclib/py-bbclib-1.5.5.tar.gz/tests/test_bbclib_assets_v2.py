# -*- coding: utf-8 -*-
import binascii
import sys
sys.path.extend(["../"])
import bbclib
from bbclib import BBcTransaction, BBcRelation, KeyPair, BBcAssetRaw, BBcAssetHash, configure_id_length_all

ID_LEN = 32
configure_id_length_all(ID_LEN)

user_id = bbclib.get_new_id("user_id_test1")[:ID_LEN]
user_id2 = bbclib.get_new_id("user_id_test2")[:ID_LEN]
domain_id = bbclib.get_new_id("testdomain")
asset_group_id = bbclib.get_new_id("asset_group_1")[:ID_LEN]
transaction1_id = bbclib.get_new_id("transaction_1")[:ID_LEN]
transaction2_id = bbclib.get_new_id("transaction_2")[:ID_LEN]
keypair1 = KeyPair()
keypair1.generate()
keypair2 = KeyPair()
keypair2.generate()

asset_content = b'abcdefg'

print("\n")
print("private_key:", binascii.b2a_hex(keypair1.private_key))
print("private_key(pem):\n", keypair1.get_private_key_in_pem())
print("public_key:", binascii.b2a_hex(keypair1.public_key))


class TestBBcLibAssetsV2(object):

    def test_00_keypair(self):
        print("\n-----", sys._getframe().f_code.co_name, "-----")
        global keypair1
        kp = KeyPair(pubkey=keypair1.public_key)
        assert kp.public_key

    def test_01_transaction_with_relation_and_witness_and_proof(self):
        print("\n-----", sys._getframe().f_code.co_name, "-----")
        transaction1 = bbclib.make_transaction(relation_num=1, witness=True)
        transaction1.version = 2

        bbclib.add_relation_asset(transaction1, relation_idx=0, asset_group_id=asset_group_id,
                                  user_id=user_id, asset_body=b'ccccc')

        rtn1 = BBcRelation(asset_group_id=asset_group_id)
        rtn2 = BBcRelation(asset_group_id=asset_group_id)
        transaction1.add(relation=[rtn1, rtn2])

        asid = bbclib.get_new_id("assetraw1")[:ID_LEN]
        asset_raw = BBcAssetRaw(asset_id=asid, asset_body=b'1234567890abcdefg')
        rtn1.add(asset_raw=asset_raw)

        ash = [bbclib.get_new_id("assethash%d"%i)[:ID_LEN] for i in range(1, 4)]
        asset_hash = BBcAssetHash(asset_ids=ash)
        rtn2.add(asset_hash=asset_hash)

        bbclib.add_relation_pointer(transaction1, relation_idx=0, ref_transaction_id=bbclib.get_new_id("dummy1"))
        bbclib.add_relation_pointer(transaction1, relation_idx=1, ref_transaction_id=bbclib.get_new_id("dummy2"))
        bbclib.add_relation_pointer(transaction1, relation_idx=2, ref_transaction_id=bbclib.get_new_id("dummy3"))

        transaction1.witness.add_witness(user_id=user_id)
        transaction1.witness.add_witness(user_id=user_id2)

        sig = transaction1.sign(private_key=keypair2.private_key, public_key=keypair2.public_key)
        if sig is None:
            print(bbclib.error_text)
            assert sig
        transaction1.witness.add_signature(user_id=user_id2, signature=sig)

        sig = transaction1.sign(private_key=keypair1.private_key, public_key=keypair1.public_key)
        if sig is None:
            print(bbclib.error_text)
            assert sig
        transaction1.witness.add_signature(user_id=user_id, signature=sig)
        digest = transaction1.digest()
        dat = transaction1.pack()
        print("Digest:", binascii.b2a_hex(digest))
        print("Serialized data:", binascii.b2a_hex(dat))
        print(transaction1)

        transaction_tmp = BBcTransaction()
        transaction_tmp.unpack(dat)
        transaction1 = transaction_tmp
        print(transaction1)

        assert transaction1.relations[1].asset_raw is not None
        assert transaction1.relations[1].asset_raw.asset_id == asid
        assert transaction1.relations[2].asset_hash is not None
        for i, h in enumerate(transaction1.relations[2].asset_hash.asset_ids):
            assert ash[i] == h

        digest = transaction1.digest()
        ret = transaction1.signatures[0].verify(digest)
        print("Proof result:", ret)
        if not ret:
            print(bbclib.error_text)
            assert ret

    def test_02_create_transaction_by_utility(self):
        print("\n-----", sys._getframe().f_code.co_name, "-----")
        transaction1 = bbclib.make_transaction(relation_num=3, witness=True, version=3)
        ash = [bbclib.get_new_id("assethash%d"%i)[:ID_LEN] for i in range(7)]

        bbclib.add_relation_asset(transaction1, relation_idx=0, asset_group_id=asset_group_id, user_id=user_id, asset_body=b'ccccc')
        bbclib.add_relation_asset_raw(transaction1, relation_idx=1, asset_group_id=asset_group_id, asset_id=ash[0])
        bbclib.add_relation_asset_hash(transaction1, relation_idx=2, asset_group_id=asset_group_id, asset_ids=ash[1:3])
        rtn3 = bbclib.make_relation_with_asset(asset_group_id, user_id, asset_body=b'xxxxxx')
        rtn4 = bbclib.make_relation_with_asset_raw(asset_group_id, asset_id=ash[4], asset_body=b'yyyyyy')
        rtn5 = bbclib.make_relation_with_asset_hash(asset_group_id, asset_ids=ash[5:])
        transaction1.add(relation=[rtn3, rtn4, rtn5])

        bbclib.add_relation_pointer(transaction1, relation_idx=0, ref_transaction_id=bbclib.get_new_id("dummy1"))
        bbclib.add_relation_pointer(transaction1, relation_idx=1, ref_transaction_id=bbclib.get_new_id("dummy2"))
        bbclib.add_relation_pointer(transaction1, relation_idx=2, ref_transaction_id=bbclib.get_new_id("dummy3"))

        transaction1.witness.add_witness(user_id=user_id)
        transaction1.witness.add_witness(user_id=user_id2)

        sig = transaction1.sign(private_key=keypair2.private_key, public_key=keypair2.public_key)
        if sig is None:
            print(bbclib.error_text)
            assert sig
        transaction1.witness.add_signature(user_id=user_id2, signature=sig)

        sig = transaction1.sign(private_key=keypair1.private_key, public_key=keypair1.public_key)
        if sig is None:
            print(bbclib.error_text)
            assert sig
        transaction1.witness.add_signature(user_id=user_id, signature=sig)
        digest = transaction1.digest()
        dat = transaction1.pack()
        print("Digest:", binascii.b2a_hex(digest))
        print("Serialized data:", binascii.b2a_hex(dat))
        print(transaction1)

        transaction_tmp = BBcTransaction()
        transaction_tmp.unpack(dat)
        transaction1 = transaction_tmp
        print(transaction1)

        assert transaction1.relations[1].asset_raw is not None
        assert transaction1.relations[1].asset_raw.asset_id == ash[0]
        assert transaction1.relations[2].asset_hash is not None
        for i, h in enumerate(transaction1.relations[2].asset_hash.asset_ids):
            assert ash[i+1] == h
        assert transaction1.relations[3].asset.asset_body == b'xxxxxx'
        assert transaction1.relations[4].asset_raw.asset_id == ash[4]
        assert len(transaction1.relations[5].asset_hash.asset_ids) == 2

        digest = transaction1.digest()
        ret = transaction1.signatures[0].verify(digest)
        print("Proof result:", ret)
        if not ret:
            print(bbclib.error_text)
            assert ret
