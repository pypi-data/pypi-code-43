#!/usr/bin/env python
# -*- coding: utf-8 -*-
import binascii
import struct
import ctypes

CURRENCY = b'RAS'

# F_ formats
F_HASH = '64s'
F_BLOCK_SIZE = '64s I I'
F_TRANSACTION = '64s 32s 32s I Q 16s 32s'
F_SIGNATURE = '64s'
F_PUB_KEY = '32s'
F_DATA = '32s I Q 16s 32s'
F_COUNTERS = "Q Q Q"
F_BALANCE = "I Q"
F_HEADER = 'H I'
F_CURRENCY = '16s'
F_TRANSACTIONS = '64s Q H'
F_TRANSACTION_S = 'Q H 64s'
F_BLOCKS = 'Q H'
F_TRANSACTION_LEN = 'H'
F_BUFFER = '64s H'
F_BUFFER_PART = '64s H I I'

CMD_NUMS = {
    'Invalid': -1, 
    'TermBlock': 0,
    'GetInfo': 1,
    'SendInfo': 2,
    'GetBalance': 3,
    'SendBalance': 4,
    'GetCounters': 5,
    'SendCounters': 6,
    'GetLastHash': 7,
    'SendLastHash': 8,
    'GetBlocks': 9,
    'SendBlocks': 10,
    'GetBlockSize': 11,
    'SendBlockSize': 12,
    'GetTransactions': 13,
    'SendTransactions': 14,
    'GetTransaction': 15,
    'SendTransaction': 16,
    'CommitTransaction': 17,
    'GetLastError': 18,
    'Error': 19,
    'GetTransactionsByKey': 20,
	'SendTransactionsByKey': 21,
    'GetFee': 22,
    'SendFee': 23,
    'GetBuffer': 24,
    'SendBuffer': 25,
    'GetBufferPart': 26,
    'GetPrevHash': 27,
    'SendPrevHash': 28,
    'GetNodesCount': 29,
    'SendNodesCount': 30,
    'CommitTransactionArray': 31
}
CMD_NUMS_MAX = max(CMD_NUMS.values())

def calcsize(structure):
    return struct.calcsize(structure)

#Protos
class Proto(object):
    currency = CURRENCY
    structure = None
    buffer = None
    values = None
    cmd_num = -1

    def create_buffer(self):
        self.buffer = ctypes.create_string_buffer(self.structure.size)

    def pack(self):
        self.structure.pack_into(self.buffer, 0, *self.values)

    def unpack(self):
        self.values = self.structure.unpack_from(self.buffer.raw, 0)
        if len(self.values) > 0 and isinstance(self.values[0], int) \
            and self.values[0] <= CMD_NUMS_MAX:
            self.cmd_num = self.values[0]

    def check(self):
        if len(self.values) > 1 and self.cmd_num != 0 \
            and self.values[0] == self.cmd_num and self.values[1] > 0:
            return True
        return False

    def check_cmd_num(self, cmd):
        num = CMD_NUMS.get(cmd, None)
        if num is not None and self.cmd_num == num:
            return True
        return False

    def buf_size(self):
        return self.structure.size

class PublicKey(Proto):
    def __init__(self):
        self.structure = struct.Struct('=%s' % (F_PUB_KEY))
        self.create_buffer()

    def unpack(self):
        self.values = self.structure.unpack_from(self.buffer.raw, 0)

class Transaction(Proto):
    def __init__(self):
        self.structure = struct.Struct('=%s' % (F_TRANSACTION))
        self.create_buffer()

class Header(Proto):
    def __init__(self):
        self.size = 0
        self.structure = struct.Struct('=%s' % (F_HEADER))
        self.create_buffer()

    def unpack(self):
        super(Header, self).unpack()
        if len(self.values) > 1 and isinstance(self.values[1], int):
            self.size = self.values[1]

class BlockHash(Proto):
    def __init__(self):
        self.structure = struct.Struct('=%s' % (F_HASH))
        self.create_buffer()

    def get_hash(self):
        if len(self.values) > 0:
            return self.values[0]
        return None

class BlockSize(Proto):
    def __init__(self):
        self.hash = b''
        self.transactions = 0
        self.binary = 0
        self.structure = struct.Struct('=%s' % (F_BLOCK_SIZE))
        self.create_buffer()

    def unpack(self):
        super(BlockSize, self).unpack()
        if len(self.values) > 1:
            self.hash = self.values[0]
            if isinstance(self.values[1], int):
                self.transactions = self.values[1]
            if isinstance(self.values[2], int):
                self.binary = self.values[2]


class TerminatingBlock(Proto):
    def __init__(self):
        self.structure = struct.Struct("=%s" % (F_HEADER))
        self.values = (0, 0)
        self.create_buffer()

class Counters(Proto):
    def __init__(self):
        self.blocks = 0
        self.transactions = 0
        self.binary = 0
        self.structure = struct.Struct('=%s' % (F_COUNTERS))
        self.create_buffer()

    def unpack(self):
        super(Counters, self).unpack()
        if len(self.values) > 1:
            if isinstance(self.values[0], int):
                self.blocks = self.values[0]
            if isinstance(self.values[1], int):
                self.transactions = self.values[1]
            if isinstance(self.values[2], int):
                self.binary = self.values[2]

class Balance(Proto):
    def __init__(self):
        self.integral = 0
        self.fraction = 0
        self.structure = struct.Struct("=%s" % (F_BALANCE))
        self.create_buffer()

    def unpack(self):
        super(Balance, self).unpack()
        if len(self.values) > 1:
            if isinstance(self.values[0], int):
                self.integral = self.values[0]
            if isinstance(self.values[1], int):
                self.fraction = self.values[1]

class TransactionsByKey(Proto):
    def __init__(self):
        self.offset = 0
        self.limit = 0
        self.hash = b''
        self.structure = struct.Struct('=%s' % (F_TRANSACTION_S))
        self.create_buffer()

    def unpack(self):
        super(TransactionsByKey, self).unpack()
        if len(self.values) > 1:
            if isinstance(self.values[0], int):
                self.offset = self.values[0]
                print('offset', self.offset)
            if isinstance(self.values[1], int):
                self.limit = self.values[1]
                print('limit', self.limit)
            self.hash = self.values[2]


#Get methods
class GetBalance(Proto):
    def __init__(self):
        self.cmd_num = CMD_NUMS['GetBalance']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_CURRENCY))
        self.values = (self.cmd_num,
                       calcsize(F_CURRENCY),
                       self.currency)
        self.create_buffer()
        self.pack()


class GetCounters(Proto):
    def __init__(self):
        self.cmd_num = CMD_NUMS['GetCounters']
        self.structure = struct.Struct("=%s" % (F_HEADER))
        self.values = (self.cmd_num, 0)
        self.create_buffer()
        self.pack()


class GetLastHash(Proto):
    def __init__(self):
        self.cmd_num = CMD_NUMS['GetLastHash']
        self.structure = struct.Struct("=%s" % (F_HEADER))
        self.values = (self.cmd_num, 0)
        self.create_buffer()
        self.pack()


class GetBlockSize(Proto):
    def __init__(self, block_hash):
        self.cmd_num = CMD_NUMS['GetBlockSize']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_HASH))
        self.create_buffer()
        self.values = (self.cmd_num,
                       calcsize(F_HASH),
                       binascii.unhexlify(block_hash))
        self.pack()


class GetTransactions(Proto):
    def __init__(self, block_hash, offset, limit):
        self.cmd_num = CMD_NUMS['GetTransactions']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_TRANSACTIONS))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_TRANSACTIONS),
            binascii.unhexlify(block_hash),
            offset,
            limit
        )
        self.pack()

class GetPrevHash(Proto):
    def __init__(self, hash):
        self.cmd_num = CMD_NUMS['GetPrevHash']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_HASH))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_HASH),
            binascii.unhexlify(hash)
        )
        self.pack()

class GetBlocks(Proto):
    def __init__(self, offset, limit):
        self.cmd_num = CMD_NUMS['GetBlocks']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_BLOCKS))
        self.create_buffer()
        self.values = (self.cmd_num,
                       calcsize(F_BLOCKS),
                       offset,
                       limit)
        self.pack()


class GetTransaction(Proto):
    def __init__(self, b_hash, t_hash):
        self.cmd_num = CMD_NUMS['GetTransaction']
        self.structure = struct.Struct('=%s %s %s' % (F_HEADER, F_HASH, F_HASH))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_HASH)*2,
            binascii.unhexlify(b_hash),
            binascii.unhexlify(t_hash)
        )
        self.pack()


class GetInfo(Proto):
    def __init__(self, key):
        self.cmd_num = CMD_NUMS['GetInfo']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_PUB_KEY))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_PUB_KEY),
            key
        )
        self.pack()

class GetTransactionsByKey(Proto):
    def __init__(self, offset, limit):
        self.cmd_num = CMD_NUMS['GetTransactionsByKey']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_TRANSACTIONS))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_TRANSACTIONS),
            b'00',
            offset,
            limit
        )
        self.pack()


class GetFee(Proto):
    def __init__(self, amount):
        self.cmd_num = CMD_NUMS['GetFee']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_BALANCE))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_BALANCE),
            amount.integral,
            amount.fraction,
        )
        self.pack()


class GetBuffer(Proto):
    def __init__(self, buff):
        self.cmd_num = CMD_NUMS['GetBuffer']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_BUFFER))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_BUFFER),
            binascii.unhexlify(buff.hash),
            buff.id_onblock
        )
        self.pack()


class GetBufferPart(Proto):
    def __init__(self, binaryPart):
        self.cmd_num = CMD_NUMS['GetBufferPart']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_BUFFER_PART))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_BUFFER_PART),
            binascii.unhexlify(binaryPart.hash),
            binaryPart.id_onblock,
            binaryPart.offset,
            binaryPart.size
        )
        self.pack()


# Send Data
class SendTransaction(Proto):
    def __init__(self, t):
        self.cmd_num = CMD_NUMS['CommitTransaction']
        self.structure = struct.Struct('=%s %s' % (F_HEADER, F_TRANSACTION))
        self.create_buffer()
        self.values = (
            self.cmd_num,
            calcsize(F_TRANSACTION),
            t.hash_hex,
            binascii.unhexlify(t.sender_public),
            binascii.unhexlify(t.receiver_public),
            t.amount.integral,
            t.amount.fraction,
            self.currency,
            t.salt
        )
        self.pack()


class SendBuffer(Proto):
    def __init__(self, buffer):
        self.cmd_num = CMD_NUMS['SendBuffer']

        buffer_str = str(len(buffer)) + 's'
        self.structure = struct.Struct('=%s %s' % (F_HEADER, buffer_str))
        self.values = (self.cmd_num,
                       len(buffer), buffer)
        self.create_buffer()
        self.pack()


class SendClose(Proto):
    def __init__(self):
        self.cmd_num = CMD_NUMS['']
        self.structure = struct.Struct()
        self.values = (self.cmd_num, 0)
        self.create_buffer()
        self.pack()
