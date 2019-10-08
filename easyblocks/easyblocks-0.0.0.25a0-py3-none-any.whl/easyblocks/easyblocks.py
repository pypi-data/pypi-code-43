#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import utils
from easyrocks import DB, WriteBatch


class Blockchain:

    # meta_ -> labels ro by the user
    # labels_ -> labels rw by the user
    # block_ -> blocks ro
    # hash_ -> blocks ro
    # height_ -> blocks ro

    def __init__(self, path='./chaindata', signature_checker=None, create_if_missing=False, read_only=False):
        self._db = DB(path=path, opts={'create_if_missing': create_if_missing}, read_only=read_only)
        if signature_checker:
            self.signature_checker = signature_checker
        self._write_batch = None

    def put(self, key, value):
        self._put(f'label_{key}', value)

    def get(self, key):
        return self._db.get(f'label_{key}')

    def add_block(self, block_dict):
        self.begin()

        height = self._increment_height()
        if self.get_block_by_hash(block_dict['hash']):
            raise PermissionError
        if not self._prev_hash_is_correct(height, block_dict['prev_hash']):
            raise PermissionError
        if not self._signature_is_valid(block_dict):
            raise PermissionError
        block_key = self._get_block_key(height, block_dict['hash'])

        # Remove items array since they are already stored in the merkle tree
        block_items = block_dict.pop('items')

        # height, block_hash -> block_dict
        self._put(block_key, block_dict)

        # height -> block_hash
        self._put(f'height_{height}', block_dict['hash'])

        # block_hash -> height
        self._put(f"hash_{block_dict['hash']}", height)

        # tx -> block_hash
        for item_dict in block_items:
            item_key = self._get_item_key(item_dict['hash'])
            self._put(item_key, item_dict)

        self.commit()

    def get_block_by_height(self, height):
        block_hash = self._db.get(f'height_{height}')
        return self._get_block(height, block_hash)

    def get_block_by_hash(self, block_hash):
        height = self._db.get(f'hash_{block_hash}')
        return self._get_block(height, block_hash)

    def get_block_hash_by_height(self, height):
        return self._db.get(f'height_{height}')

    def get_block_hash_by_item_hash(self, item_hash):
        item_key = self._get_item_key(item_hash)
        return self._db.get(item_key)

    def exists_item_by_hash(self, item_hash):
        item_key = self._get_item_key(item_hash)
        return self._db.exists(item_key)

    def get_block_height_by_hash(self, block_hash):
        return self._db.get(f'hash_{block_hash}')

    def get_height(self):
        height = self.get_meta('height')
        return height

    def get_meta(self, key):
        return self._db.get(f'meta_{key}')

    def print_chain(self):
        for key, value in self._db.scan(prefix='block_'):
            height = int(key.split('_')[1])
            print(f'Height: {height}')
            block_dict = utils.dump_pretty_dict(value)
            print(f'{block_dict}\n')

    def print_meta(self):
        for key, value in self._db.scan(prefix='label_'):
            print(f'key: {key}, value: {value}')

    def begin(self):
        if self._write_batch is None:
            self._write_batch = WriteBatch()

    def commit(self):
        if self._write_batch is not None:
            self._db.commit(self._write_batch)
            self._write_batch = None

    def _get_block_key(self, height, prev_hash):
        return f'block_{utils.get_padded_int(height)}_{prev_hash}'

    def _get_item_key(self, item_hash):
        return f'item_{item_hash}'

    def _get_block(self, height, block_hash):
        block_key = self._get_block_key(height, block_hash)
        block = self._db.get(block_key)
        return block

    def _can_put(self, key):
        prefix = key.split('_')[0]

        if self._db.get(key) is None \
        or prefix == 'label' \
        or prefix == 'meta':
            return True
        else:
            return False

    def _put(self, key, value):
        if not self._can_put(key):
            raise PermissionError
        self._db.put(key, value, write_batch=self._write_batch)

    def _increment_height(self):
        height = self.get_height()
        if height is None:
            height = 0
        else:
            height += 1
        self._put('meta_height', height)
        return height

    def _prev_hash_is_correct(self, current_height, prev_hash):
        if self.get_height() is None:
            return True

        prev_height = self.get_block_height_by_hash(prev_hash)
        if prev_height != current_height - 1:
            return False

        block_dict = self.get_block_by_hash(prev_hash)
        if not block_dict:
            return False

        if block_dict['hash'] == prev_hash:
            return True

        return False

    def _signature_is_valid(self, block_dict):
        if not hasattr(self, 'signature_checker'):
            return True

        if not 'signature' in block_dict:
            return False
        return self.signature_checker(block_dict['signature'])