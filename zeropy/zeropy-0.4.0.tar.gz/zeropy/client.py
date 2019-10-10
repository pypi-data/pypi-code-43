#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zeropy.socket as sock
import zeropy.utils as utils
import zeropy.logger as logger
import zeropy.proto as proto
import zeropy.structs as struct

class apiClient(object):
    __socketlayer = None
    private_key = None
    public_key = None

    def __init__(self):
        self.__socketlayer = sock.SocketManager()
        self.log = None

    def connect(self, ip, port):
        self.__socketlayer.connect(ip, port)

    def disconnect(self):
        self.__socketlayer.disconnect()

    def active(self) -> bool:
        return self.__socketlayer.is_connected()

    def logger(self, path, logger_name):
        if path is None:
            return None
        self.log = logger.setup(path, logger_name)
        return True

    def set_keys(self,
                 pub_key,
                 pr_key):
        self.public_key = pub_key
        self.private_key = pr_key

    def send_info(self,
                  key):
        if not self.__socketlayer.is_connected():
            return False

        resp_key = self.__socketlayer.method(key,
                                             _type=proto.CMD_NUMS['GetInfo'],
                                             term_block=True)
        if resp_key is None:
            return None

        return resp_key

    def get_counters(self):
        if not self.__socketlayer.is_connected():
            return

        r_counters = self.__socketlayer.method(
                                    _type=proto.CMD_NUMS['GetCounters'],
                                    term_block=True)
        if r_counters is None:
            return

        counters = struct.Counters()
        counters.set_vals(r_counters.blocks,
                          r_counters.transactions, r_counters.binary)
        return counters

    def get_last_hash(self):
        if not self.__socketlayer.is_connected():
            return

        r_block_hash = self.__socketlayer.method(
                                _type=proto.CMD_NUMS['GetLastHash'],
                                term_block=True)

        block = struct.Block()
        block.set_hash(r_block_hash.get_hash())
        return block

    def get_prev_hash(self, hash):
        if not self.__socketlayer.is_connected():
            return None

        r_block_hash = self.__socketlayer.method(hash,
                                                 _type=proto.CMD_NUMS['GetPrevHash'],
                                                 term_block=True)

        block = struct.Block()
        block.set_hash(r_block_hash.get_hash())

        return block

    def get_block_size(self, block_hash):
        if not self.__socketlayer.is_connected():
            return

        block_size = self.__socketlayer.method(block_hash,
                                               _type=proto.CMD_NUMS['GetBlockSize'],
                                               term_block=True)
        if block_size is None:
            return


        counters = struct.BlockCounters()
        counters.set_vals(block_size.transactions,
                          block_size.binary)

        return counters

    def get_transactions(self,
                         block_hash,
                         offset,
                         limit):
        if not self.__socketlayer.is_connected():
            return

        block_hash = self.__socketlayer.method(block_hash,
                                               offset,
                                               limit,
                                               _type=proto.CMD_NUMS['GetTransactions'],
                                               term_block=False)


        txs_list = []

        hash_size = 64
        txs_list_size = self.__socketlayer.response.size - hash_size

        if txs_list_size % hash_size > 0:
            return txs_list
        txs_count = int(txs_list_size / hash_size)

        for i in range(0, txs_count):
            hash = self.__socketlayer.recv_into('BlockHash')
            if hash is None:
                return

            hash = hash.get_hash()
            txs_list.append(hash)

        self.__socketlayer.recv_into('Termblock')

        return txs_list


    def get_blocks(self,
                   offset,
                   limit):
        if not self.__socketlayer.is_connected():
            return


        hash  = self.__socketlayer.method(offset,
                                          limit,
                                          _type=proto.CMD_NUMS['GetBlocks'],
                                          term_block=False)

        blocks = []
        block_size = 64
        blocks_count = int(self.__socketlayer.response.size / block_size)

        block = struct.Block()
        block.set_hash(hash.get_hash())
        blocks.append(block)

        for b in range(0, blocks_count-1):
            block_hash = self.__socketlayer.recv_into('BlockHash')
            block = struct.Block()
            block.set_hash(block_hash.get_hash())
            blocks.append(block)

        self.__socketlayer.recv_into('Termblock')

        return blocks

    def get_transaction(self,
                        b_hash,
                        t_hash):
        if not self.__socketlayer.is_connected():
            return None

        bloch_hash = self.__socketlayer.method(b_hash,
                                               t_hash,
                                               _type=proto.CMD_NUMS['GetTransaction'],
                                               term_block=False)


        tx = self.__socketlayer.recv_into('Transaction')

        tr = struct.Transaction()
        tr.parse(tx.values)

        self.__socketlayer.recv_into('Termblock')

        return tr

    def get_balance(self):
        if not self.__socketlayer.is_connected():
            return

        balance = self.__socketlayer.method(
                _type=proto.CMD_NUMS['GetBalance'],
                term_block=True)

        if balance is None:
            return None

        amount = struct.Amount()
        amount.set_amount(balance.integral,
                          balance.fraction)

        return amount

    def get_transactionsbykey(self,
                              offset,
                              limit):
        if not self.__socketlayer.is_connected():
            return

        answer = self.__socketlayer.method(offset,
                                           limit,
                                           _type=proto.CMD_NUMS['GetTransactionsByKey'],
                                           term_block=False)

        if answer is None:
            return

        txs = []

        tx_size = proto.calcsize('=%s' % proto.F_TRANSACTION)
        util_size = proto.calcsize('=%s' % proto.F_HASH)
        txs_buffer_size = self.__socketlayer.response.size - util_size

        if txs_buffer_size % tx_size > 0:
            return None

        txs_count = int(txs_buffer_size /
                        tx_size)

        for _ in range(0, txs_count):
            tx = self.__socketlayer.recv_into('Transaction')
            tr = struct.Transaction()
            tr.parse(tx.values)
            txs.append(tr)

        self.__socketlayer.recv_into('Termblock')

        return txs

    def get_fee(self,
                amount):
        if not self.__socketlayer.is_connected():
            return False

        fee = self.__socketlayer.method(amount,
                                        _type=proto.CMD_NUMS['GetFee'],
                                        term_block=True)

        _amount = struct.Amount()
        _amount.set_amount(fee.integral, fee.fraction)
        return _amount

    def get_buffer(self, hash, id_onblock):
        if not self.__socketlayer.is_connected():
            return False

        bin_part = struct.BinaryPart()
        bin_part.hash = hash
        bin_part.id_onblock = id_onblock
        buffer = self.__socketlayer.method(bin_part,
                                            _type=proto.CMD_NUMS['GetBuffer'],
                                            term_block=True)

        return buffer


    def get_buffer_part(self, hash, id_onblock, offset, size, ):
        if not self.__socketlayer.is_connected():
            return False

        bin_part = struct.BinaryPart()
        bin_part.hash = hash
        bin_part.id_onblock = id_onblock
        bin_part.offset = offset
        bin_part.size = size

        buffer = self.__socketlayer.method(bin_part,
                                           _type=proto.CMD_NUMS['GetBufferPart'],
                                           term_block=True)

        view = memoryview(buffer)
        buffer = view[proto.calcsize('=%s' % proto.F_BUFFER_PART):len(buffer)].tobytes()

        return buffer

    def send_transaction(self,
                         target,
                         intg,
                         frac):
        # if not self.__socketlayer.is_connected():
        #     return False

        tr = utils.transaction(self.private_key,
                              self.public_key,
                              target,
                              intg,
                              frac)

        if tr is None:
            return False
        answer = self.__socketlayer.method(tr,
                                           _type=proto.CMD_NUMS['CommitTransaction'],
                                           term_block=True)

        return True

    def send_buffer(self, buffer, crcsum: bool):
        if not self.__socketlayer.is_connected():
            return False

        if crcsum is True:
            buffer = utils.crc32_buffer(buff=buffer)
        answer = self.__socketlayer.method(buffer,
                                           _type=proto.CMD_NUMS['SendBuffer'],
                                           term_block=True)

        return True
