# -*- coding: utf-8 -*-
# @Time    : 2019-05-29 10:35
# @E-Mail  : wujifan1106@gmail.com
# @Site    : 
# @File    : bloomfilter.py
# @Software: PyCharm

import traceback
from CBloomfilter import CBloomfilter

class LocalBloomFilter():

    def __init__(self,capacity,error,prime_length = True):
        self.bf = CBloomfilter(capacity,error,prime_length)
        self.bitmap = bytes(int(self.bf.bits/8)+1)

    def add(self,data):
        if isinstance(data,(list,tuple)):
            for v in data:
                assert isinstance(v,str),'add() arg must be a str or list/tuple of strings'
                self.bf.add(self.bitmap, v)
        else:
            assert isinstance(data, str), 'add() arg must be a str or list/tuple of strings'
            self.bf.add(self.bitmap,data)

    def is_contain(self,data):
        if isinstance(data,(list,tuple)):
            for v in data:
                assert isinstance(v,str),'is_contain() arg must be a str or list/tuple of strings'
            return [self.bf.is_contain(self.bitmap, v) for v in data]
        else:
            assert isinstance(data, str), 'is_contain() arg must be a str or list/tuple of strings'
            return self.bf.is_contain(self.bitmap, data)

    def clean(self):
        self.bf.clean_bitmap(self.bitmap)


class RedisBloomFilter():
    def __init__(self, capacity, error, redis_conn, prime_length=True):
        self.bf = CBloomfilter(capacity, error, prime_length)
        self.redis_conn = redis_conn

    def add(self, key, data):
        if isinstance(data, (list, tuple)):
            offset = []
            for v in data:
                assert isinstance(v, str), 'add() arg must be a str or list/tuple of strings'
                offset += self.bf.hash(v)
            with self.redis_conn.pipeline() as pipe:
                for o in offset:
                    pipe.setbit(key,o,1)
                pipe.execute()

        else:
            assert isinstance(data, str), 'add() arg must be a str or list/tuple of strings'
            offset = self.bf.hash(data)
            with self.redis_conn.pipeline() as pipe:
                for o in offset:
                    pipe.setbit(key,o,1)
                pipe.execute()


    def delete(self,key,data):
        if isinstance(data, (list, tuple)):
            offset = []
            for v in data:
                assert isinstance(v, str), 'add() arg must be a str or list/tuple of strings'
                offset += self.bf.hash(v)
            with self.redis_conn.pipeline() as pipe:
                for o in offset:
                    pipe.setbit(key,o,0)
                pipe.execute()

        else:
            assert isinstance(data, str), 'add() arg must be a str or list/tuple of strings'
            offset = self.bf.hash(data)
            with self.redis_conn.pipeline() as pipe:
                for o in offset:
                    pipe.setbit(key,o,0)
                pipe.execute()


    def is_contain(self, key, data):
        try:
            if isinstance(data, (list, tuple)):
                offset = []
                for v in data:
                    assert isinstance(v, str), 'is_contain() arg must be a str or list/tuple of strings'
                    offset += self.bf.hash(v)

                with self.redis_conn.pipeline() as pipe:
                    for o in offset:
                        pipe.getbit(key, o)
                    result_bits = pipe.execute()
                    result = []
                    for i in range(len(data)):
                        result_bit = result_bits[i*self.bf.hashes:(i+1)*self.bf.hashes]
                        if sum(result_bit) == self.bf.hashes:
                            result.append(True)
                        else:
                            result.append(False)
                    return result

            else:
                assert isinstance(data, str), 'is_contain() arg must be a str or list/tuple of strings'
                offset = self.bf.hash(data)
                with self.redis_conn.pipeline() as pipe:
                    for o in offset:
                        pipe.getbit(key, o)
                    results = pipe.execute()
                    if sum(results) == self.bf.hashes:
                        return True
                    return False
        except Exception:
            print(traceback.format_exc())
            return None

    def clean(self,key):
        self.redis_conn.delete(key)




