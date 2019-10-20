#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pprint import pprint
import construct

from objutils.utils import create_memorymapped_fileview


#print(dir(construct))

import unittest
from objutils.coff import ti


obj = create_memorymapped_fileview(r'C:\projekte\csProjects\pyCCP\Sample.out')
#obj = memoryMap(r'C:\projekte\csProjects\pyCCP\CPUTest.obj')
#obj = memoryMap(r'C:\projekte\csProjects\pyCCP\main.obj')
#print(fileHeader, dir(fileHeader))
#

#coff = ti.TICOFF(r'C:\projekte\csProjects\pyCCP\Sample.out')
coff = ti.TICOFF(r'C:\projekte\csProjects\pyCCP\CPUTest.obj')

#obj.size()
#fh = ti.fileHeader.parse(obj, context = {"size": obj.size()})
fh = ti.fileHeader.parse(obj, size = obj.size())


# Syms: 25342   0x62fe      6300 od. 6302

def main():
  unittest.main()

if __name__ == '__main__':
  main()

