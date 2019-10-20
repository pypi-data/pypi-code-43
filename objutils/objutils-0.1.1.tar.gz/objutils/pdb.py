#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
__version__ = "0.1.0"

__copyright__ = """
    objutils - Object file library for Python.

   (C) 2010-2018 by Christoph Schueler <cpu12.gems@googlemail.com>

   All Rights Reserved

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from collections import namedtuple
import enum
import mmap
import os
from pprint import pprint
import sys
import time
import types
import struct
import uuid

import construct
from construct import Struct, If, Const, Adapter, FlagsEnum, Enum, String, Array, Padding, HexDump, Tell, Union
from construct import CString, IfThenElse, Pass, Float64l, Int8ul, Construct, this, GreedyBytes, Switch, Seek
from construct import Pointer, Byte, GreedyRange, Bytes, Int16ul, Int16sl, Int32ul, Int64ul, this, RepeatUntil
from construct import Computed, Int32sl, BitsInteger, BitStruct, Flag

import six

from objutils.utils import create_memorymapped_fileview, slicer

StreamInfo = namedtuple("StreamInfo", "size blocks")

PDB7_MAGIC = b'Microsoft C/C++ MSF 7.00\r\n\x1ADS\0\0\0'

"""
00000000  4d 69 63 72 6f 73 6f 66  74 20 43 2f 43 2b 2b 20  |Microsoft C/C++ |
00000010  4d 53 46 20 37 2e 30 30  0d 0a 1a 44 53 00 00 00  |MSF 7.00...DS...|
00000020  00 10 00 00 01 00 00 00  1b 00 00 00 60 00 00 00  |............`...|
"""

PDB2_MAGIC = b"Microsoft C/C++ program database 2.00\r\n\032JG\0\0"
"""
00000000  4d 69 63 72 6f 73 6f 66  74 20 43 2f 43 2b 2b 20  |Microsoft C/C++ |
00000010  70 72 6f 67 72 61 6d 20  64 61 74 61 62 61 73 65  |program database|
00000020  20 32 2e 30 30 0d 0a 1a  4a 47 00 00 00 04 00 00  | 2.00...JG......|
00000030  09 00 49 00 b0 00 00 00  90 1e 3c 00 41 00 00 00  |..I.......<.A...|
00000040  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|

"""

import io
import math
import os


def pred(x, *args):
    return x != 0


# FRED: (Container(BlockSize=4096)(FreeBlockMapBlock=1)(NumBlocks=27)(NumDirectoryBytes=100)(Unknown=0)(BlockMapAddr=26),)
def fred(*args):
    print("FRED: {}".format(args))

#DirectoryBlock = Struct (
#    "Directorys" / RepeatUntil(pred, Int32ul)
#)


StreamDirectory = Struct (
    "NumStreams" / Int32ul,
    "StreamSizes" / Int32ul[this.NumStreams],
    "offset" / Tell,
)

SuperBlock = Struct(
    Const(PDB7_MAGIC),
    "BlockSize" / Int32ul,
    "FreeBlockMapBlock" / Int32ul,
    "NumBlocks" / Int32ul,
    "NumDirectoryBytes" / Int32ul,
    "Unknown" / Int32ul,
    "BlockMapAddr" / Int32ul,

    Seek(this.BlockSize * this.BlockMapAddr),
    "DirectoryBlocks" / RepeatUntil(pred, Int32ul),
)

#def uu(val):
#    print("VAL: {}".format(val))
#    return uuid.UUID(bytes = val)


PdbStreamVersion = {
    19941610: "VC2",
    19950623: "VC4",
    19950814: "VC41",
    19960307: "VC50",
    19970604: "VC98",
    19990604: "VC70Dep",
    20000404: "VC70",
    20030901: "VC80",
    20091201: "VC110",
    20140508: "VC140",
}

PdbStreamHeader = Struct(
    "_Version" / Int32ul,
    "Signature" / Int32ul,
    "Age" / Int32ul,
    "_Guid" / Bytes(16),
    "num" / Int32ul,
)


ModInfo =  Struct(
    Padding(4),
    "SectionContribEntry " / Struct(
        "Section" / Int16ul,
        Padding(2),
        "Offset" / Int32sl,
        "Size" / Int32sl,
        "Characteristics" / Int32ul,
        "ModuleIndex" / Int16ul,
        Padding(2),
        "DataCrc" / Int32ul,
        "RelocCrc" / Int32ul,
    ),
    "Flags" / Int16ul,
    "ModuleSymStream" / Int16ul,
    "SymByteSize" / Int32ul,
    "C11ByteSize" / Int32ul,
    "C13ByteSize" / Int32ul,
    "SourceFileCount" / Int16ul,
    "Unused2" / Bytes(2),
    #Padding(4),
    "Offsets" / Int32ul,
    "SourceFileNameIndex" / Int32ul,
    "PdbFilePathNameIndex" / Int32ul,
    "ModuleName" / CString(encoding = "utf_8"),
    "ObjFileName" / CString(encoding = "utf_8"),
)

#DbiStreamHeader = Struct(
DbiStream = Struct(
    "DbiStreamHeader" / Struct(
        "VersionSignature" / Int32sl,
        "VersionHeader" / Enum(Int32ul,
            VC41 = 930803,
            VC50 = 19960307,
            VC60 = 19970606,
            VC70 = 19990903,
            VC110 = 20091201,
        ),
        "Age" / Int32ul,
        "GlobalStreamIndex" / Int16ul,
        "BuildNumber" / BitStruct(
            "MinorVersion" / BitsInteger(8),
            "MajorVersion" / BitsInteger(7),
            "NewVersionFormat" / Flag,
        ),
        "PublicStreamIndex" / Int16ul,
        "PdbDllVersion" / Int16ul,
        "SymRecordStream" / Int16ul,
        "PdbDllRbld" / Int16ul,
        "ModInfoSize" / Int32sl,
        "SectionContributionSize" / Int32sl,
        "SectionMapSize" / Int32sl,
        "SourceInfoSize" / Int32sl,
        "TypeServerSize" / Int32sl,
        "MFCTypeServerIndex" / Int32ul,
        "OptionalDbgHeaderSize" / Int32sl,
        "ECSubstreamSize" / Int32sl,
        #"Flags" / Int16ul,
        "Flags" / BitStruct(
            "WasIncrementallyLinked" / Flag,
            "ArePrivateSymbolsStripped" / Flag,
            "HasConflictingTypes" / Flag,
            Padding(13),
        ),
        "Machine" / Int16ul,
        #"Padding" / Int32ul,
        Padding(4),
    ),
    #Padding(2),
    "m0" / ModInfo,
    "m1" / ModInfo,
    "m2" / ModInfo,
    "m3" / ModInfo,
    "m4" / ModInfo,
)

print("SZ:", DbiStream.DbiStreamHeader.sizeof())

# 0x0000c4f0 + 4

FNAME = r"C:\projekte\csProjects\XCP\cXCP\XCP_SIM\vc120.pdb"
FNAME = r"c:\symbols\xpsprint.pdb\35F6A89417B14A43BEA68539AB5717991\xpsprint.pdb"
FNAME = r"c:\symbols\wmp_notestroot.pdb\F7597C0206C641AAABCB1EB12E52C9A62\wmp_notestroot.pdb"


class Directory(object): pass

class Reader(object):

    def __init__(self, fname):
        self.fname = fname

        self._getBasicMSFData()
        self._parseStreams()
        #self._linearizeStreams()

    def _getBasicMSFData(self):
        self.image = memoryview(io.open(self.fname, "rb").read())

        pdb = SuperBlock.parse(self.image)
        #print(pdb)
        #print(pdb.NumDirectoryBytes / pdb.BlockSize, int(math.ceil(pdb.NumDirectoryBytes / pdb.BlockSize)))

        assert len(self.image) == pdb.BlockSize * pdb.NumBlocks

        self.blockSize = pdb.BlockSize
        self.directories = []
        for db in pdb.DirectoryBlocks:
            directory = Directory()
            addr = db * self.blockSize
            sd = StreamDirectory.parse(self.image[addr : ])
            directory.numStreams = sd.NumStreams
            directory.streamSizes = sd.StreamSizes
            directory.numBlocks = [int(math.ceil(x / self.blockSize)) for x in directory.streamSizes]

            assert pdb.NumDirectoryBytes == (directory.numStreams * 4) + (sum(directory.numBlocks) * 4) + 4

            blocks = Array(sum(directory.numBlocks), Int32ul).parse(self.image[addr + sd.offset: ])

            streamBlocks = []
            offset = 0
            for numBlocks in directory.numBlocks:
                streamBlocks.append(blocks[offset : offset + numBlocks])
                offset += numBlocks
            streamInfo = [(x, y) for x, y in zip(directory.streamSizes, streamBlocks)]

            directory.images = []
            for si in streamInfo:
                img = self._readStream(*si)
                directory.images.append(img)

            self.directories.append(directory)

    def _readStream(self, size, blocks):
        if not size and not blocks:
            return []
        remaining = size % self.blockSize
        blockReads = len(blocks)
        result = bytearray()
        for idx, block in enumerate(blocks, 1):
            offset = block * self.blockSize
            img = self.image[offset : offset + self.blockSize].tobytes()
            if idx == blockReads:
                result.extend(img[ : remaining])
            else:
                result.extend(img)
        return result

    def _parseStreams(self):
        print(self.fname)
        images = self.directories[0].images
        img = images[1]
        psh = PdbStreamHeader.parse(img)
        psh.Guid = uuid.UUID(bytes = psh._Guid)
        psh.Version = PdbStreamVersion.get(psh._Version, psh._Version)
        #print(uuid.UUID(bytes = psh._Guid))
        print(psh)

        if images[3]:
            dsh = DbiStream.parse(images[3])
            print(dsh)

        print("=" * 80)
        for idx, img in enumerate(self.directories[0].images):
            with io.open("image.{}".format(idx), "wb") as fo:
                fo.write(bytes(img))

# uuid.UUID(bytes = bytes(mem[12:12+16]))

folders = []
files = []
def traverse(pth):
    for entry in os.scandir(pth):
        if entry.is_dir():
            traverse(entry.path)
        elif entry.is_file():
            #print("{}\t{}".format(entry.stat().st_size, entry.path))
            #data = io.open(entry.path, "rb").read()
            try:
                rd = Reader(entry.path)
                #pdb = SuperBlock.parse(data)
                #if pdb.BlockSize != 1024:
                #    print("!= 1024 {}\t{}".format(entry.stat().st_size, entry.path))
            except Exception as e:
                print("{} ==> {}".format(entry.path, str(e)))


#traverse(r"c:\symbols")

def main():

    #fname = r"C:\projekte\csProjects\XCP\cXCP\XCP_SIM\vc120.pdb"
    fname = r"c:\symbols\xpsprint.pdb\35F6A89417B14A43BEA68539AB5717991\xpsprint.pdb"
    #fname = r"c:\symbols\wmp_notestroot.pdb\F7597C0206C641AAABCB1EB12E52C9A62\wmp_notestroot.pdb"
    #parse(fname)
    rd = Reader(fname)
    #ep = ElfParser(fname)

if __name__ == '__main__':
    main()

"""
00019000  08 00 00 00 64 00 00 00  4b 00 00 00 b0 72 00 00  |....d...K....r..|
00019010  00 00 00 00 c8 2b 00 00  19 00 00 00 94 09 00 00  |.....+..........|
00019020  c8 05 00 00 09 00 00 00  18 00 00 00 0f 00 00 00  |................|
00019030  03 00 00 00 04 00 00 00  07 00 00 00 0b 00 00 00  |................|
00019040  0a 00 00 00 0c 00 00 00  06 00 00 00 16 00 00 00  |................|
00019050  11 00 00 00 14 00 00 00  05 00 00 00 0e 00 00 00  |................|
00019060  10 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00019070  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|

"""
