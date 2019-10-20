#!/usr/bin/env python
# -*- coding: utf-8 -*-

from array import array
import unittest
import sys

from objutils import loads, dumps
from objutils.section  import Section
from objutils.image  import Image, Builder
from objutils.utils import PYTHON_VERSION

##
## TODO: Image methods tobytes(), tolist()
##       Slices erzeugen wiederum Images
##

class TestCreateSections(unittest.TestCase):

    def testRead(self):
        builder = Builder()
        data = bytearray(range(256))
        builder.addSection(data, 0x1000)
        image = builder.image
        image.writeString(0x10f0, "HELLO WORLD!!!")
        val = image.readString(0x10f0)
        print(val)
        image.writeNumeric(0x1004, 0x4711, "uint32_be")
        val = image.readNumeric(0x1004, "uint32_be")
        print(hex(val))
        #print(dumps("ihex", image[0]))
        print([x for x in image[0]])
        print("", 0x1000 in image[0])



        print(list(image[0].find("G.*?J")))

        data = image.read(0x10e0, 32)
        print(data.hexdump())
        print(data.tobytes())
        print(data.tolist())

        #val = image.readNumeric(0x10fe, "uint32_be")
        #result = dumps('ihex', builder.image)
        #print(image.hexdump())

if __name__ == '__main__':
    unittest.main()

unittest.main()
