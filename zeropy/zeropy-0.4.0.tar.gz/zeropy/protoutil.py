#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zeropy.proto as proto


"""
    Create proto structure
"""
def create_proto(*args, type):
    reqType = None

    if type == proto.CMD_NUMS['GetBalance']:
        reqType = proto.GetBalance()
    elif type == proto.CMD_NUMS['GetLastHash']:
        reqType = proto.GetLastHash()
    elif type == proto.CMD_NUMS['GetCounters']:
        reqType = proto.GetCounters()
    elif type == proto.CMD_NUMS['GetBlockSize']:
        hash = args[0]
        reqType = proto.GetBlockSize(hash)
    elif type == proto.CMD_NUMS['GetBlocks']:
        offset = args[0]
        limit = args[1]
        reqType = proto.GetBlocks(offset, limit)
    elif type == proto.CMD_NUMS['GetTransaction']:
        block_hash = args[0]
        t_hash = args[1]
        reqType = proto.GetTransaction(block_hash, t_hash)
    elif type == proto.CMD_NUMS['GetTransactions']:
        b_hash = args[0]
        offset = args[1]
        limit = args[2]
        reqType = proto.GetTransactions(b_hash, offset, limit)
    elif type == proto.CMD_NUMS['GetTransactionsByKey']:
        offset = args[0]
        limit = args[1]
        reqType = proto.GetTransactionsByKey(offset, limit)
    elif type == proto.CMD_NUMS['GetFee']:
        amount = args[0]
        reqType = proto.GetFee(amount)
    elif type == proto.CMD_NUMS['CommitTransaction']:
        tr = args[0]
        reqType = proto.SendTransaction(tr)
    elif type == proto.CMD_NUMS['GetInfo']:
        key = args[0]
        reqType = proto.GetInfo(key)
    elif type == proto.CMD_NUMS['SendBuffer']:
        __buffer = args[0]
        reqType = proto.SendBuffer(__buffer)
    elif type == proto.CMD_NUMS['GetBuffer']:
        __buff = args[0]
        reqType = proto.GetBuffer(__buff)
    elif type == proto.CMD_NUMS['GetBufferPart']:
        __bufferPart = args[0]
        reqType = proto.GetBufferPart(__bufferPart)
    elif type == proto.CMD_NUMS['GetPrevHash']:
        __hash = args[0]
        reqType = proto.GetPrevHash(__hash)
    return reqType

"""
    Create answer structure
"""
def create_struct(type):
    struct = proto.BlockHash()
    if type is proto.CMD_NUMS['GetFee']:
        struct = proto.Balance()
    if type is proto.CMD_NUMS['GetBalance']:
        struct = proto.Balance()
    elif type is proto.CMD_NUMS['GetInfo']:
        struct = proto.PublicKey()
    elif type is proto.CMD_NUMS['GetCounters']:
        struct = proto.Counters()
    elif type is proto.CMD_NUMS['GetBlockSize']:
        struct = proto.BlockSize()
    return struct

"""
    Create proto, for manual receive
"""
def recv_proto(type):
    result = None
    if type == 'Transaction':
        result = proto.Transaction()
    elif type == 'BlockHash':
        result = proto.BlockHash()
    elif type == 'BlockSize':
        result = proto.BlockSize()
    elif type == 'Termblock':
        result = proto.TerminatingBlock()
    return result


