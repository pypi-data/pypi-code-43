#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File name: product_counter
# Author: Oswaldo Cruz Simon
# Email: oswaldo_cs_94@hotmail.com
# Maintainer: Oswaldo Cruz Simon
# Date created: 03/10/19
# Date last modified: 03/10/19
# Project Name: scrapingtools

import redis
from scrapingtools.utils import transform

MAX_DATABASES = 15
EXECUTION_COUNTER_DATABASE = 0
expected_template = '{}:{}:{}'
received_template = '{}:{}:{}'

TTL_DAY = 60*60*24
TTL_WEEK = TTL_DAY * 7


#%%
class ProductCounter(object):

    def __init__(self, retailer, date, ttl, execution_id=None,
                 store='all', host='localhost', port=6379, password=None):
        self._retailer = retailer
        self._date = date
        self._execution_id = execution_id
        self._host = host
        self._port = port
        self._db = redis.Redis(host=host, port=port, db=self.database_name(date), password=password)
        self._name_template = '{}:{}:{}:{}:{}:{}:{}'
        self._ttl = ttl
        self._store = store
        if not host or not port:
            raise ValueError('Invalid host and port {}:{}'.format(host, port))

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, value):
        self._store = value

    @classmethod
    def database_name(cls, date):
        return int(date) % MAX_DATABASES

    @property
    def execution_id(self):
        if not self._execution_id:
            counter_db = redis.Redis(db=EXECUTION_COUNTER_DATABASE)
            self._execution_id = counter_db.incr("{}.{}".format(self._retailer, self._date))
        return self._execution_id

    def set_expected_products(self, department, category, page, total):
        category = transform.to_key(category)
        department = transform.to_key(department)
        hash_name = self._name_template.format(
            self._date, self._retailer, self.execution_id, self._store, department, category, page)
        self._db.hset(
            hash_name, 'expected', total)
        self._db.expire(name=hash_name, time=self._ttl)

    def get_expected_products(self, name, key):
        return self._db.hget(name, key)

    def set_received_products(self, department, category, page, total):
        category = transform.to_key(category)
        department = transform.to_key(department)
        hash_name = self._name_template.format(
            self._date, self._retailer, self.execution_id, self._store, department, category, page)
        self._db.hset(hash_name, 'received', total)
        self._db.expire(name=hash_name, time=self._ttl)

    def get_received_products(self, name, key):
        return self._db.hget(name, key)

    def increase_expected_products(self, department, category, page, delta):
        category = transform.to_key(category)
        department = transform.to_key(department)
        hash_name = self._name_template.format(
            self._date, self._retailer, self.execution_id, self._store, department, category, page
        )
        total = self._db.hincrby(hash_name, 'expected', delta)
        self._db.expire(name=hash_name, time=self._ttl)
        return total

    def increase_received_products(self, department, category, page, delta):
        category = transform.to_key(category)
        department = transform.to_key(department)
        hash_name = self._name_template.format(
            self._date, self._retailer, self.execution_id, self._store, department, category, page
        )
        total = self._db.hincrby(hash_name, 'received', delta)
        self._db.expire(name=hash_name, time=self._ttl)
        return total

    def generate_hash_name(self, breadcrumb):
        breadcrumb = [transform.to_key(str(i)) for i in breadcrumb if str(i)]
        depth = len(breadcrumb) + 4  # Four for: date, retailer, execution_id, store_uuid
        name_template = ':'.join(['{}'] * depth)

        complete_breadcrumb = [self._date, self._retailer, self.execution_id, self._store] + breadcrumb
        hash_name = name_template.format(*complete_breadcrumb)
        return hash_name

    def set_value_by_breadcrumb(self, breadcrumb, key_name, total):
        hash_name = self.generate_hash_name(breadcrumb)
        self._db.hset(
            hash_name, key_name, total)
        self._db.expire(name=hash_name, time=self._ttl)

    def increase_value_by_breadcrumb(self, breadcrumb, key_name, delta):
        hash_name = self.generate_hash_name(breadcrumb)
        total = self._db.hincrby(hash_name, key_name, delta)
        self._db.expire(name=hash_name, time=self._ttl)
        return total

if __name__ == '__main__':
    from datetime import datetime
    date = datetime.now().date().strftime('%Y%m%d')
    retailer = 'walmart'
    ttl = 120
    counter = ProductCounter(retailer, date, ttl=120, store='0101')
    counter.set_value_by_breadcrumb(['tecnologia', 'laptos', 'page', 'aiuda'], 'recieved', 12)

    counter2 = ProductCounter(retailer, date, ttl=ttl)
    counter2.set_value_by_breadcrumb(['tecnologia', 'laptos', 'page', 'aiuda'], 'recieved', 12)

    counter3 = ProductCounter(retailer, date, ttl=ttl, execution_id=1)
    counter3.increase_value_by_breadcrumb(['tecnologia', 'laptos', 'page'], 'expected', 13)