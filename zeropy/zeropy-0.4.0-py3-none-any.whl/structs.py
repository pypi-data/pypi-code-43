#!/usr/bin/env python
# -*- coding: utf-8 -*-
import binascii
import zeropy.utils as utils

class Amount(object):
    def __init__(self):
        self.integral = 0
        self.fraction = 0

    def set_amount(self, integral=None, fraction=None):
        if integral is not None:
            self.integral = integral
        if fraction is not None:
            self.fraction = fraction

class Counters(object):
    def __init__(self):
        self.blocks = 0
        self.transactions = 0
        self.binary = 0

    def set_vals(self, blocks=None, transactions=None, binary = None):
        if blocks is not None:
            self.blocks = blocks
        if transactions is not None:
            self.transactions = transactions
        if binary is not None:
            self.binary = binary


class BlockCounters(object):
    def __init__(self):
        self.transactions = 0
        self.binary = 0

    def set_vals(self,transactions=None, binary = None):
        if transactions is not None:
            self.transactions = transactions
        if binary is not None:
            self.binary = binary


class Transaction(object):
    def __init__(self):
        self.hash_hex = None
        self.sender_public = None
        self.receiver_public = None
        self.amount = Amount()
        self.currency = None
        self.salt = None

    def parse(self, proto_transaction_values):
        self.hash_hex = binascii.hexlify(proto_transaction_values[0])
        self.sender_public = binascii.hexlify(proto_transaction_values[1])
        self.receiver_public = binascii.hexlify(proto_transaction_values[2])
        self.amount.set_amount(
            integral=proto_transaction_values[3],
            fraction=proto_transaction_values[4]
        )
        if proto_transaction_values != None:
           self.currency = proto_transaction_values[5].decode("utf-8").rstrip('\0')

class BinaryPart(object):
    def __init__(self):
        self.hash = None
        self.id_onblock = 0
        self.offset = 0
        self.size = 0

class Block(object):
    def __init__(self):
        self.hash = None
        self.hash_hex = None

    def set_hash(self, data):
        if isinstance(data, bytes):
            self.hash = data
            self.hash_hex = binascii.hexlify(data)

    def __eq__(self, other):
        return utils.check_equal_bytearrays(self.hash, other.hash)

    def __ne__(self, other):
        import operator
        result = utils.check_equal_bytearrays(self.hash, other.hash)
        return operator.not_(result)