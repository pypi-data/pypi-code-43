#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import unittest
from objutils import load, dump, loads, dumps


HELLO = b"""%256D980000006B48656C6C6F2C20576F726C64210A
%09819800000000"""


TTT = b"%4E62B440004E80507B00F9100410040004100040003437070EA607E680164418C6016B0232303D"

def main():
    data = load('etek', open("./tests/test.etek"))
    #data = loads("etek", TTT)
    #data = loads("etek", HELLO)
    #print  "*** '%s' ***" % data
    print(dumps("etek", data, row_length = 34))
    print(dumps("srec", data, row_length = 32))
    print(data.hexdump())

if __name__ == '__main__':
    main()

