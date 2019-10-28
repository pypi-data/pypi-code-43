#!/usr/bin/env python

from io import BytesIO
from hashlib import sha1
from sys import argv

from DKFileHelper import DKFileHelper


class githash(object):

    def __init__(self):
        self.buf = BytesIO()

    def update(self, data):
        self.buf.write(data)

    def hexdigest(self):
        data = self.buf.getvalue()
        h = sha1()
        h.update("blob %u\0" % len(data))
        h.update(data)

        return h.hexdigest()


def githash_data(data):
    h = githash()
    h.update(data)
    return h.hexdigest()


def githash_by_file_name(file_name):
    file_contents = DKFileHelper.read_file(file_name)
    return githash_data(file_contents)


if __name__ == '__main__':
    for filename in argv[1:]:
        print(githash_by_file_name(filename))
