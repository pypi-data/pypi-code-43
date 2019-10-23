# MIT License
#
# Copyright (c) 2019 Red Hat, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
from os import getenv

from redis import Redis


class PersistentDict:
    """
    Dictionary backed by Redis DB.

    We use Redis` 'hash' type [1] and store whole dictionary in one hash called self.hash.

    Usage:
    db = PersistentDict(hash_name="my-persistent-dict")
    # add bug to the db with a value
    db[key] = value
    # show whole dictionary
    print(db)
    # iterate of bugs in db
    for key, value in db.items():
      do_something(key)
    # do sth with key if it is in db
    if key in db:
      do_something(key)
    # delete bug from db
    del db[key]

    [1] https://redis.io/topics/data-types-intro#hashes is basically Python's dict, but values
        can be strings only, so we use json serialization
    """

    def __init__(self, hash_name="dict-in-redis"):
        """

        :param hash_name: name of the dictionary/hash [1] we store all the info in
        """
        self.db = Redis(
            host=getenv("REDIS_SERVICE_HOST", "localhost"),
            port=getenv("REDIS_SERVICE_PORT", "6379"),
            db=1,  # 0 is used by Celery
            decode_responses=True,
        )
        self.hash = hash_name

    def __contains__(self, key):
        """
        Is key in db ?

        Usage:
        if key in PersistentDict():

        :param key: can be int or string
        :return: bool
        """
        return self.db.hexists(self.hash, key)

    def __getitem__(self, key):
        """
        Get info to key

        Usage:
        xyz = PersistentDict()[key]

        :param key: can be int or string
        :return: value assigned to the key or None if key not in db
        """
        value = self.db.hget(self.hash, key)
        if value is None:
            raise KeyError(f"Key '{key}' does not exist.")
        return json.loads(value)

    def __len__(self):
        """

        Number of items in db.

        Usage:
        len(PersistentDict())
        """
        return self.db.hlen(self.hash)

    def __setitem__(self, key, value):
        """
        Store key in db along with a value.
        Because values in a hash can be only strings, we first json serialize the value

        Usage:
        PersistentDict()[key] = value

        :param key: can be int or string
        :param value: additional info, can be any json serializable object
        """
        self.db.hset(self.hash, key, json.dumps(value))

    def __delitem__(self, key):
        """
        Remove key from db

        Usage:
        del PersistentDict()[key]

        :param key: can be int or string
        """
        self.db.hdel(self.hash, key)

    def __repr__(self):
        """
        print(PersistentDict())

        :return: string representation
        """
        return str(self.get_all())

    def clear(self):
        """
        Remove all items from dictionary
        """
        for key in self.keys():
            self.__delitem__(key)

    def get(self, key, default=None):
        """Get info to key or default, if key not present.

        Usage:
        xyz = PersistentDict().get(key, default)

        :param key: can be int or string
        :param default: can be anything, default is None
        :return: value assigned to the key or default if key not in db
        """
        value = self.db.hget(self.hash, key)
        if value is None:
            return default
        return json.loads(value)

    def get_all(self):
        """
        Return whole dictionary

        Usage:
        all_bugs_dict = PersistentDict().get_all()

        :return: dictionary of {key: value}
        """
        return {k: json.loads(v) for k, v in self.db.hgetall(self.hash).items()}

    def items(self):
        """
        Return iterator over the (key, value) pairs

        Usage:
        for key, value in PersistentDict().items():

        :return: iterator over the (key, value) pairs
        """
        return self.get_all().items()

    def keys(self):
        """
        :return: view object that displays a list of all the keys
        """
        return self.get_all().keys()
