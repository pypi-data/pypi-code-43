#!/usr/bin/env python

"""
While there are a buch of command-line utilities, objutils is a library in the first place,
which sets it apart from most other similar projects in this category.

historical aspects

aims at a comprehensive feature set for current applications
"""

from copy import copy
import os
import unittest
from objutils import dump, dumps, load, loads, probe, probes


TEST1 = ''':10C00000576F77212044696420796F7520726561CC
:10C010006C6C7920676F207468726F756768206137
:10C020006C6C20746869732074726F75626C652023
:10C03000746F207265616420746869732073747210
:04C040007696E67397
:00000001FF
'''

TEST2 = ''':100000004578616D706C65207769746820616E2039
:0B0010006164647265737320676170A7
:101000004865726520697320612067617020696E90
:1010100020746865206D656D6F727920616C6C6FEE
:06102000636174696F6E4C
:00000001FF
'''

TEST3 = ''':020000022BC011
:1012340054686973207061727420697320696E2028
:0D12440061206C6F77207365676D656E74B7
:020000027F007D
:1080000054686973207061727420697320696E20EE
:108010007468652068696768207365676D656E744C
:00000001FF
'''

TEST4 = """:0D00000048656C6C6F2C20576F726C640AA1
:00000001FF"""

result = probes(TEST1)
print("File is: '{0}'".format(result))

data = loads("ihex", TEST4)
print(data.hexdump())

BASE_DIR = r'C:\transfer\projekte\winIDEA\2009\Examples'

def recurseDirsForExtensions(base, path, result, extensions):
    curPath = os.path.join(base, *path)
    for fname in  os.listdir(curPath):
        if os.path.isdir(os.path.join(curPath, fname)):
            path.append(fname)
            recurseDirsForExtensions(base, path, result, extensions)
            path.pop(-1)
        elif os.path.isfile(os.path.join(curPath, fname)):
            _, ext = os.path.splitext(fname)
            if ext.lower() in extensions:
                print(path, fname)
                result.append((copy(path), fname))

result = []

"""
recurseDirsForExtensions(BASE_DIR, [], result, ('.hex', '.ihex'))
for path, fname  in result:
    rfname = os.path.join(os.path.join(BASE_DIR, *path), fname)
    print rfname
    data = load("ihex", file(rfname))
    print data
    print "=" * 80
"""

data = load("ihex", open(r'C:\transfer\projekte\winIDEA\2009\Examples\iTRACE_PRO\ARM7\ITLPC2138\Interrupts\Debug\display.hex'))
data.hexdump()

# C:\transfer\projekte\winIDEA\2009\Examples\OSEK\HC12\OSEKM106\sample.hex

#data = load("ihex", file(r"C:\transfer\projekte\winIDEA\2009\Examples\ICE\Z80\Z80\2500AD\Debug\TEST.HEX"))
#print data

#data = load("ihex", file(r"C:\transfer\projekte\winIDEA\2009\Examples\ICE\HC11\NoBank\2500AD\M.HEX"))
#print data

#data = load("ihex", file(r"C:\Users\Administrator.christoph303-HP\Documents\Atmel Studio\6.1\GETTING-STARTED1\GETTING-STARTED1\Debug\GETTING-STARTED1.hex"))
#print data

class TestIHex(unittest.TestCase):
    def test01(self):
        data = loads("ihex", TEST1)
        print(data)
        print("---\n")

    def test02(self):
        data = loads("ihex", TEST2)
        print(data)
        print("---\n")

    def test03(self):
        data = loads("ihex", TEST3)
        print(data)
        print("---\n")

unittest.main()


def main():
    data = load("ihex", "../tests/redboot.hex")
    print(data)
    print("===\n")

if __name__=='__main__':
    main()

