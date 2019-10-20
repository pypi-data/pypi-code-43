#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1.0"

__copyright__ = """
    objutils - Object file library for Python.

   (C) 2010-2016 by Christoph Schueler <cpu12.gems@googlemail.com>

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

import construct
from construct import Struct, If, Const, Adapter, FlagsEnum, Enum, String, Array, Padding, HexDump, Probe, CString, IfThenElse, Pass, Float64l
from construct import OnDemandPointer, Pointer, Byte, GreedyRange, Bytes, Int16ul, Int16sl, Int32ul, Int64ul, Construct, this, GreedyBytes, Switch


DOS_MAGIC = 'MZ'
PE_MAGIC = "PE\x00\x00"


class PrintContext(Construct):

    def _parse(self, stream, context):
        print(context)

class DateTimeAdapter(Adapter):

    def _decode(self, obj, context):
        return time.ctime(obj)

##
## File header format.
##

DOSFileHeader = "DOSFileHeader" / Struct(
    Const(DOS_MAGIC),
    "e_cblp" / Int16ul,
    "e_cp" / Int16ul,
    "e_crlc" / Int16ul,
    "e_cparhdr" / Int16ul,
    "e_minalloc" / Int16ul,
    "e_maxalloc" / Int16ul,
    "e_ss" / Int16ul,
    "e_sp" / Int16ul,
    "e_csum" / Int16ul,
    "e_ip" / Int16ul,
    "e_cs" / Int16ul,
    "e_lfarlc" / Int16ul,
    "e_ovno" / Int16ul,
    "e_res" / Int16ul,
    Padding(3 * 2),
    "e_oemid" / Int16ul,
    "e_oeminfo" / Int16ul,
    "e_res2" / Int16ul,
    Padding(9 * 2),
    "e_lfanew" / Int32ul,
#    Int16ul("e_"),
)

print(DOSFileHeader.sizeof())

PEFileHeader = "PEFileHeader" / Struct(
    Const(PE_MAGIC),
    "machine" / Enum(Int16ul,
        MACHINE_UNKNOWN           = 0,
        MACHINE_I386              = 0x014c,  # Intel 386.
        MACHINE_R3000             = 0x0162,  # MIPS little-endian, 0x160 big-endian
        MACHINE_R4000             = 0x0166,  # MIPS little-endian
        MACHINE_R10000            = 0x0168,  # MIPS little-endian
        MACHINE_WCEMIPSV2         = 0x0169,  # MIPS little-endian WCE v2
        MACHINE_ALPHA             = 0x0184,  # Alpha_AXP
        MACHINE_SH3               = 0x01a2,  # SH3 little-endian
        MACHINE_SH3DSP            = 0x01a3,
        MACHINE_SH3E              = 0x01a4,  # SH3E little-endian
        MACHINE_SH4               = 0x01a6,  # SH4 little-endian
        MACHINE_SH5               = 0x01a8,  # SH5
        MACHINE_ARM               = 0x01c0,  # ARM Little-Endian
        MACHINE_THUMB             = 0x01c2,
        MACHINE_AM33              = 0x01d3,
        MACHINE_POWERPC           = 0x01F0,  # IBM PowerPC Little-Endian
        MACHINE_POWERPCFP         = 0x01f1,
        MACHINE_IA64              = 0x0200,  # Intel 64
        MACHINE_MIPS16            = 0x0266,  # MIPS
        MACHINE_ALPHA64           = 0x0284,  # ALPHA64
        MACHINE_MIPSFPU           = 0x0366,  # MIPS
        MACHINE_MIPSFPU16         = 0x0466,  # MIPS
        # MACHINE_AXP64             = MACHINE_ALPHA64,
        MACHINE_TRICORE           = 0x0520,  # Infineon
        MACHINE_CEF               = 0x0CEF,
        MACHINE_EBC               = 0x0EBC,  # EFI Byte Code
        MACHINE_AMD64             = 0x8664,  # AMD64 (K8)
        MACHINE_M32R              = 0x9041,  # M32R little-endian
        MACHINE_CEE               = 0xC0EE,
        _default_dict             = Pass,
    ),
    "numberOfSections" / Int16ul,
    "timeDateStamp" / DateTimeAdapter(Int32ul),
    "pointerToSymbolTable" / Int32ul,
    "numberOfSymbols" / Int32ul,
    "sizeOfOptionalHeader" / Int16ul,

    "characteristics" / FlagsEnum(Int16ul,
        RELOCS_STRIPPED           = 0x0001,  # Relocation info stripped from file.
        EXECUTABLE_IMAGE          = 0x0002,  # File is executable  (i.e. no unresolved externel references).
        LINE_NUMS_STRIPPED        = 0x0004,  # Line nunbers stripped from file.
        LOCAL_SYMS_STRIPPED       = 0x0008,  # Local symbols stripped from file.
        AGGRESIVE_WS_TRIM         = 0x0010,  # Agressively trim working set
        LARGE_ADDRESS_AWARE       = 0x0020,  # App can handle >2gb addresses
        BYTES_REVERSED_LO         = 0x0080,  # Bytes of machine word are reversed.
        MACHINE_32BIT             = 0x0100,  # 32 bit word machine.
        DEBUG_STRIPPED            = 0x0200,  # Debugging info stripped from file in .DBG file
        REMOVABLE_RUN_FROM_SWAP   = 0x0400,  # If Image is on removable media, copy and run from the swap file.
        NET_RUN_FROM_SWAP         = 0x0800,  # If Image is on Net, copy and run from the swap file.
        SYSTEM                    = 0x1000,  # System File.
        DLL                       = 0x2000,  # File is a DLL.
        UP_SYSTEM_ONLY            = 0x4000,  # File should only be run on a UP machine
        BYTES_REVERSED_HI         = 0x8000,  # Bytes of machine word are reversed.
    )
    #PrintContext("ctx"),
)

PeCOFFFile = "PeCOFFFile" / Struct(
    DOSFileHeader,
    #PEFileHeader,
)


#TEST_FILE = r'C:\projekte\csProjects\k-ps\tests\Posix_Serial.exe'
TEST_FILE = r'C:\projekte\csProjects\k-ps\tools\libzmq-v120-mt-4_0_4.dll'

def main():
    with open(TEST_FILE) as peFile:
        result = PeCOFFFile.parse_stream(peFile)
        peFile.seek(result['DOSFileHeader']['e_lfanew'], os.SEEK_SET)
        pe0 = PEFileHeader.parse_stream(peFile)
        print(pe0)
        # time.ctime(1394843357)

if __name__ == '__main__':
    main()


##
## Microsoft Portable Executable and Common Object File Format
## s. http://www.microsoft.com/whdc/system/platform/firmware/PECOFF.mspx
##    WinNT.h
##

MSDOS_SIGNATURE     = 0x5a4d        # 'MZ'
PE_SIGNATURE        = 0x00004550    # 'PE00'
OS2_SIGNATURE       = 0x454E        # 'NE'
OS2_SIGNATURE_LE    = 0x454C        # 'LE'
VXD_SIGNATURE_LE    = 0x454C        # 'LE'
PE_OFFSET           = 0x3c

"""
    HLIStruct
    A higher-level interface to the Python <i>struct</i> module.
"""

class BaseType(object):

    def __init__(self, displayOrder):
        self.displayOrder = displayOrder


class Byte(BaseType):
    FORMAT = "B"


class Word(BaseType):
    FORMAT = "H"


class DWord(BaseType):
    FORMAT = "I"


class QWord(BaseType):
    FORMAT = "Q"


class CTime(DWord):

    @classmethod
    def converter(cls, data):
        return time.ctime(data)

DYNAMIC = -1

class Array(BaseType):

    def __init__(self, displayOrder, numberOfElements, **kws):
        super(Array, self).__init__(displayOrder)
        self.numberOfElements = numberOfElements


class MetaType(type):

    def __new__(cls, name, bases, namespace):
        newCls = super(MetaType, cls).__new__(cls, name, bases, namespace)
        if not '__metaclass__' in namespace:
            newCls.attributes = {a: getattr(newCls, a) for a in namespace if not a.startswith('_')}
            #newCls._buildFormatString()
        return newCls

    def _buildFormatString(cls):
        format = ["<"]  # TODO: Parameter!!!
        for name, attr in sorted(cls.attributes.items(), key = lambda o: o[1].displayOrder):
            #print type(attr).__bases__
            if not issubclass(type(attr), Array):
                format.append(attr.FORMAT)
            else:
                fstr = "{1}{0}".format(attr.FORMAT[1 : ], attr.numberOfElements)
                format.append(fstr)
        cls.FORMAT = ''.join(format)
        cls.SIZE = struct.calcsize(cls.FORMAT)


class Structure(object):
    __metaclass__ = MetaType

    def __init__(self, fp, offset,  **kws):
        self.fp = fp
        if not offset:
            offset = fp.tell()
        self.offset = offset
        for key, value in kws.items():
            if key.endswith('length'):
                pos = key.pos('length')
                print(key, value)
        self._buildFormatString()

        fp.seek(offset, os.SEEK_SET)
        chunk = fp.read(self.SIZE)
        result = struct.unpack(self.FORMAT, chunk)
        for (attr, _), value in zip(sorted(self.attributes.items(), key = lambda o: o[1].displayOrder), result):
            setattr(self, attr, value)

    def _buildFormatString(cls):
        format = ["<"]  # TODO: Parameter!!!
        for name, attr in sorted(cls.attributes.items(), key = lambda o: o[1].displayOrder):
            #print type(attr).__bases__
            if not issubclass(type(attr), Array):
                format.append(attr.FORMAT)
            else:
                if attr.numberOfElements == DYNAMIC:
                    pass
                fstr = "{1}{0}".format(attr.FORMAT[1 : ], attr.numberOfElements)
                format.append(fstr)
        cls.FORMAT = ''.join(format)
        cls.SIZE = struct.calcsize(cls.FORMAT)


##
##  Directory format.
##
class DataDirectory(Array, Structure): # TODO: 'Structure' hinter 'Structure' 'verbergen'!!!
    virtualAddress  = DWord(1)
    size            = DWord(2)


NUMBEROF_DIRECTORY_ENTRIES    = 16

class OptionalHeader(Structure):
    ##
    ## Standard fields.
    ##
    magic                       = Word(1)
    majorLinkerVersion          = Byte(2)
    minorLinkerVersion          = Byte(3)
    sizeOfCode                  = DWord(4)
    sizeOfInitializedData       = DWord(5)
    sizeOfUninitializedData     = DWord(6)
    addressOfEntryPoint         = DWord(7)
    baseOfCod                   = DWord(8)
    baseOfData                  = DWord(9)
    ##
    ## NT additional fields.
    ##
    imageBase                   = DWord(10)
    sectionAlignment            = DWord(11)
    fileAlignment               = DWord(12)
    majorOperatingSystemVersion = Word(13)
    minorOperatingSystemVersion = Word(14)
    majorImageVersion           = Word(15)
    minorImageVersion           = Word(16)
    majorSubsystemVersion       = Word(17)
    minorSubsystemVersion       = Word(18)
    win32VersionValue           = DWord(19)
    sizeOfImage                 = DWord(20)
    sizeOfHeaders               = DWord(21)
    checkSum                    = DWord(22)
    subsystem                   = Word(23)
    dllCharacteristics          = Word(24)
    sizeOfStackReserve          = DWord(25)
    sizeOfStackCommit           = DWord(26)
    sizeOfHeapReserve           = DWord(27)
    sizeOfHeapCommit            = DWord(28)
    loaderFlags                 = DWord(29)
    numberOfRvaAndSizes         = DWord(30)
#    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
    dataDirectory               = DataDirectory(31, NUMBEROF_DIRECTORY_ENTRIES)


"""
//
// Optional header format.
//

typedef struct _IMAGE_OPTIONAL_HEADER {
    //
    // Standard fields.
    //

    WORD    Magic;
    BYTE    MajorLinkerVersion;
    BYTE    MinorLinkerVersion;
    DWORD   SizeOfCode;
    DWORD   SizeOfInitializedData;
    DWORD   SizeOfUninitializedData;
    DWORD   AddressOfEntryPoint;
    DWORD   BaseOfCode;
    DWORD   BaseOfData;

    //
    // NT additional fields.
    //

    DWORD   ImageBase;
    DWORD   SectionAlignment;
    DWORD   FileAlignment;
    WORD    MajorOperatingSystemVersion;
    WORD    MinorOperatingSystemVersion;
    WORD    MajorImageVersion;
    WORD    MinorImageVersion;
    WORD    MajorSubsystemVersion;
    WORD    MinorSubsystemVersion;
    DWORD   Win32VersionValue;
    DWORD   SizeOfImage;
    DWORD   SizeOfHeaders;
    DWORD   CheckSum;
    WORD    Subsystem;
    WORD    DllCharacteristics;
    DWORD   SizeOfStackReserve;
    DWORD   SizeOfStackCommit;
    DWORD   SizeOfHeapReserve;
    DWORD   SizeOfHeapCommit;
    DWORD   LoaderFlags;
    DWORD   NumberOfRvaAndSizes;
    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
} IMAGE_OPTIONAL_HEADER32, *PIMAGE_OPTIONAL_HEADER32;

typedef struct _IMAGE_ROM_OPTIONAL_HEADER {
    WORD   Magic;
    BYTE   MajorLinkerVersion;
    BYTE   MinorLinkerVersion;
    DWORD  SizeOfCode;
    DWORD  SizeOfInitializedData;
    DWORD  SizeOfUninitializedData;
    DWORD  AddressOfEntryPoint;
    DWORD  BaseOfCode;
    DWORD  BaseOfData;
    DWORD  BaseOfBss;
    DWORD  GprMask;
    DWORD  CprMask[4];
    DWORD  GpValue;
} IMAGE_ROM_OPTIONAL_HEADER, *PIMAGE_ROM_OPTIONAL_HEADER;

typedef struct _IMAGE_OPTIONAL_HEADER64 {
    WORD        Magic;
    BYTE        MajorLinkerVersion;
    BYTE        MinorLinkerVersion;
    DWORD       SizeOfCode;
    DWORD       SizeOfInitializedData;
    DWORD       SizeOfUninitializedData;
    DWORD       AddressOfEntryPoint;
    DWORD       BaseOfCode;
    ULONGLONG   ImageBase;
    DWORD       SectionAlignment;
    DWORD       FileAlignment;
    WORD        MajorOperatingSystemVersion;
    WORD        MinorOperatingSystemVersion;
    WORD        MajorImageVersion;
    WORD        MinorImageVersion;
    WORD        MajorSubsystemVersion;
    WORD        MinorSubsystemVersion;
    DWORD       Win32VersionValue;
    DWORD       SizeOfImage;
    DWORD       SizeOfHeaders;
    DWORD       CheckSum;
    WORD        Subsystem;
    WORD        DllCharacteristics;
    ULONGLONG   SizeOfStackReserve;
    ULONGLONG   SizeOfStackCommit;
    ULONGLONG   SizeOfHeapReserve;
    ULONGLONG   SizeOfHeapCommit;
    DWORD       LoaderFlags;
    DWORD       NumberOfRvaAndSizes;
    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
} IMAGE_OPTIONAL_HEADER64, *PIMAGE_OPTIONAL_HEADER64;
"""


class Reader(object):
    FORMATS = {1: "B", 2: "H", 4: "I", 8: "Q"}

    def __init__(self, fp, readContent = True):
        if not hasattr(fp, 'read'):
            raise TypeError("Need a file-like object.")
        self.fp = fp
        dosSig = self.read(0x00, 2)
        flonz = self.readU32(PE_OFFSET)
        peSig = self.read(flonz, 4)
        self.imageFileHeader = self.readSection(ImageFileHeader, 0x00)
        #size = self.imageFileHeader.??? /
        self.optionalHeader = self.readSection(OptionalHeader, self.fp.tell(), dataDirectoryLength = 0x10)

    def readSection(self, readerClass, offset, **kws):
#        length = readerClass.SIZE
#        if offset:
#            self.inFile.seek(offset, os.SEEK_SET)
#        data = self.inFile.read(length)
        reader = readerClass(self.fp, offset, **kws)
        return reader
        #ts = reader.timeDateStamp
        #print time.ctime(ts)

    def read(self, pos, length):
        self.fp.seek(pos, os.SEEK_SET)
        data = self.fp.read(length)
        value = struct.unpack("<{0}".format(self.FORMATS.get(length)), data)[0]
        return value

    def readU8(self, pos):
        return self.read(pos, 1)

    def readU16(self, pos):
        return self.read(pos, 2)

    def readU32(self, pos):
        return self.read(pos, 4)

    def readU64(self, pos):
        return self.read(pos, 8)



#        self.header = ELFHeader(self)


"""
Disclaimer: This map is my on work and is by no means associated/affiliated with KNX Association (nor authorized)
(But the dataset is extracted ... from their web-site).
"""

# Official home of Wildfire the open-source KNX protocol stack.
# .. offers automotive grade software for your building automation project

# Isotope - ISO-15762-2

"""
Embedded Systems Expert and 1337 HaXx0R

xxx BBAL ( Big Badass List of xxx)

Hit me up on ...
"""

"""
If you are a Windows user like me (and don't know anything about Ruby) and you intend to setup GitHub Pages, please
don't try to use Octopress -- you will fail.
Don't  waste your precious time and safe yourself from a lot a lot of trouble and pain an sorow.
... if you are a proficient ReST coder...
the documentation isn't great, admitted, on the other hand there is not much to say about it, it's just
dead simple (hassle-free) to install and use :-)

... themes (including Bootstrap hipster HTML stuff :-))
https://github.com/getpelican/pelican-themes
live preview http://www.pelicanthemes.com/
Just thrust me!

TAGS: meta, advice
"""

# A corollary is that,
# counter-question: what hardware are you using/do you want to use?
# Presently, I am more into MSP430s and AT-SAMs, but I will surely continue my work on CPU12 parts.

# Equal parts editor of this bolg
# One season, many traditions
# DIVERSITY IN PRACTICE
# SO GLAD YOU FOUND ME!

