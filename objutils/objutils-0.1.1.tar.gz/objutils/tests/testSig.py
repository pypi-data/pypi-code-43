#!/usr/bin/env python
# -*- coding: utf-8 -*-

from objutils import loads, dumps
import unittest



SIG = b""":B00010A5576F77212044696420796F75207265617B
:B01010E56C6C7920676F207468726F756768206136
:B02010256C6C20746861742074726F75626C652068
:B0300D5F746F207265616420746869733FD1
:B03D00"""

SREC = b"""S113B000576F77212044696420796F7520726561D8
S113B0106C6C7920676F207468726F756768206143
S113B0206C6C20746861742074726F75626C652036
S110B030746F207265616420746869733F59
S5030004F8"""


class TestRoundtrip(unittest.TestCase):

    def testLoadsWorks(self):
        data = loads("sig", SIG)
        self.assertEqual(dumps("srec", data, s5record = True), SREC)
        
    def testDumpsWorks(self):
        data = loads("srec", SREC)
        self.assertEqual(dumps("sig", data), SIG)

if __name__=='__main__':
    unittest.main()
