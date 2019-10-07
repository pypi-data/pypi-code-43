#!/usr/bin/env python

from pynng import Pair0

s1 = Pair0()
s1.listen('tcp://127.0.0.1:54321')

s2 = Pair0()
s2.dial('tcp://127.0.0.1:54321')

s1.send(b'Well hello there')

print(s2.recv())

s1.close()
s2.close()
