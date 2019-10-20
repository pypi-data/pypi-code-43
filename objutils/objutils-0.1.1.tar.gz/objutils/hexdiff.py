#!/usr/bin/env python
# -*- coding: utf-8 -*-

from objutils import load, dumps
import difflib

##
##
##  TODO: diff() yielded tupel (addr, size).
##        diffdump() -> als hexdump().
##
##

def calculateDifferences(a, b):
    sa = len(a)
    sb = len(b)
    print(sa, sb)
    sm = difflib.SequenceMatcher(None, a, b, autojunk = False)   # New in version 3.2: The autojunk parameter.
    prevA = prevB = prevSize = None
    for idx, block in enumerate(sm.get_matching_blocks()):
        if block.a != sa and block.b != sb:
            #assert block.a == block.b
            print(idx, block)
            if not prevSize is None:
                print("    Diff: Addr: {} Size: {}".format(prevSize, block.a - prevSize))
        else:
            print("Final:", idx, block)
        prevA = block.a
        prevB = block.b
        prevSize = block.size
        

print(end="\n")

F1 = r"C:\Users\Public\Documents\Vector CANape 15\Examples\CDM Studio\Automation\Vb\CompareAction\CCPsimNoVariants.hex"
F2 = r"C:\Users\Public\Documents\Vector CANape 15\Examples\CDM Studio\Automation\Vb\MergeAction\CCPsimNoVariants.hex"

F1 = r"C:\Users\Public\Documents\Vector CANape 15\Examples\Datasets_Thesaurus\Datasets\XCPsim_Reworked\XCPsim_Reworked_XCPsim_Updated_Reference2_1\XCPsim_Updated_Reference2.HEX"
F2 = r"C:\Users\Public\Documents\Vector CANape 15\Examples\Datasets_Thesaurus\Datasets\XCPsim\XCPsim_XCPsim_Updated_Reference_1\XCPsim_Updated_Reference.HEX"

h0 = load("ihex", open(F1))
h1 = load("ihex", open(F2))

#calculateDifferences(h0[1].data, h1[1].data)
calculateDifferences(h0[0].data, h1[0].data)

print(end="\n")

b0 = bytes(range(64))
b1 = bytes(range(32))
calculateDifferences(b0, b1)

# e090
# 580

# E6400