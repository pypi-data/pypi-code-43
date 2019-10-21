#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
__version__ = "0.1.0"

__copyright__ = """
    objutils - Object file library for Python.

   (C) 2010-2017 by Christoph Schueler <cpu12.gems@googlemail.com>

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

import binascii
from collections import namedtuple, OrderedDict
import enum
import os
from pprint import pprint
import struct
import time


from objutils.dwarf import constants

from construct import Struct, If, Const, Adapter, FlagsEnum, Enum, String, Array, Padding, HexDump, Probe, CString, IfThenElse
from construct import Pointer, Byte, GreedyRange, Bytes, Construct, this, GreedyBytes, RepeatUntil
from construct import singleton, Pass, Computed, Switch, Union, GreedyString, GreedyBytes, Tell, Computed
from construct import Int8ul, Int16ul, Int32ul, Int32sl, Int64ul, Int64sl
from construct import         Int16ub, Int32ub, Int32sb, Int64ub, Int64sb

from objutils.utils import create_memorymapped_fileview

@singleton
class Pass2(Construct):
    r"""
    A do-nothing construct, useful as the default case for Switch. Returns None on parsing, puts nothing on building.
    Example::
        >>> Pass.parse(b"")
        >>> Pass.build(None)
        b''
        >>> Pass.sizeof()
        0
    """
    def __init__(self):
        super(self.__class__, self).__init__()
        self.flagbuildnone = True
    def _parse(self, stream, context, path):
        #print("ÜÜÜ", context)
        return None
    def _build(self, obj, stream, context, path):
        print(obj)
        pass
    def _sizeof(self, context, path):
        return 0

Test = Struct(
    "ei_version"  / Enum(Int8ul, default = Pass,
        EV_NONE = 0,
        EV_CURRENT = 1,
    )
)

print(Test.parse(b'\x32'))

class UTCTimeStampAdapter(Adapter):

    def _decode(self, obj, context):
        return time.ctime(obj)

    def _encode(self, obj, context):
        return int(time.mktime(time.strptime(obj)))


def UTCTimeStamp(name):
    return UTCTimeStampAdapter(name / Int32ul)


class ListToBytesAdapter(Adapter):

    def _decode(self, obj, context):
        return bytes(obj)

    def _encode(self, obj, context):
        return list(obj)


class PrintContext(Construct):

    def _parse(self, stream, context, *args, **kws):
        print("CTX: {} {} {}".format(context, args, kws))
        print("CTX_END")

MAGIC = b'\x7fELF'

import datetime
import time
import mmap

##
##def create_memorymapped_fileview(filename, writeable = False):
##    size = os.path.getsize(filename)
##    fd = os.open(filename, os.O_RDWR if writeable else os.O_RDONLY)
##    #return fd
##    return memoryview(mmap.mmap(fd, size, access = mmap.ACCESS_WRITE if writeable else mmap.ACCESS_READ))
##

class Sh_Type(enum.IntEnum):

    SHT_NULL        = 0
    SHT_PROGBITS    = 1
    SHT_SYMTAB      = 2
    SHT_STRTAB      = 3
    SHT_RELA        = 4
    SHT_HASH        = 5
    SHT_DYNAMIC     = 6
    SHT_NOTE        = 7
    SHT_NOBITS      = 8
    SHT_REL         = 9
    SHT_SHLIB       = 10
    SHT_DYNSYM      = 11
    SHT_LOPROC      = 0x70000000
    SHT_HIPROC      = 0x7fffffff
    SHT_LOUSER      = 0x80000000
    SHT_HIUSER      = 0xffffffff

class ElfFileStruct(Struct):

    def __init__(self, *args, **kws):
        super(ElfFileStruct, self).__init__(*args, **kws)
        #print(dir(self))

    def  elf32Addr(self):
        pass

    def setByteOrder(self):
        print("*** {}".format(self))



DebugInfo = namedtuple('DebugInfo', 'section image')

class ElfParser(object):

    EI_NIDENT = 16

    DATATYPES = {
        "Elf32_Addr":   (Int32ul, Int32ub), # 4 - Unsigned program address
        "Elf32_Half":   (Int16ul, Int16ub), # 2 - Unsigned medium integer
        "Elf32_Off":    (Int32ul, Int32ub), # 4 - Unsigned file offset
        "Elf32_Sword":  (Int32sl, Int32sb), # 4 - Signed large integer
        "Elf32_Word":   (Int32ul, Int32ub), # 4 - Unsigned large integer
        "Elf64_Addr":   (Int64ul, Int64ub), # 8 - Unsigned program address
        "Elf64_Off":    (Int64ul, Int64ub), # 8 - Unsigned file offset
        "Elf64_Half":   (Int16ul, Int16ub), # 2 - Unsigned medium integer
        "Elf64_Word":   (Int32ul, Int32ub), # 4 - Unsigned integer
        "Elf64_Sword":  (Int32sl, Int32sb), # 4 - Signed integer
        "Elf64_Xword":  (Int64ul, Int64ub), # 8 - Unsigned long integer
        "Elf64_Sxword": (Int64sl, Int64sb), # 8 - Signed long integer
    }

    BasicHeader = Struct(
        "header" / Union(None,
            "fields"/ Struct(
                Const(MAGIC),
                "ei_class"  / Int8ul,
                "ei_data"  / Int8ul,
                "ei_version"  / Int8ul,
                "ei_osabi" / Int8ul,
                "ei_abiversion" / Int8ul,
                Padding(7),
            ),
            "bytes" / Bytes(EI_NIDENT)
        ),
    )

    def __init__(self, filename):
        self._images = dict()
        self._sectionsByName = OrderedDict()
        self.asciiCString = CString(encoding = "ascii")
        self.fp = create_memorymapped_fileview(filename)
        print(filename)
        self.basicHeader = ElfParser.BasicHeader.parse(self.fp)
        self.b64 = (self.ei_class == 2)
        if self.ei_data == 1:   # Little-Endian
            offset = 0
        elif self.ei_data == 2: # Big-Endian
            offset = 1
        else:
            offset = 0   # TODO: Error!!!
        for key, value in ElfParser.DATATYPES.items():
            setattr(self, key, value[offset])

        print(self.basicHeader)
        self._parserExtendedHeader()
        self._parseSectionHeaders()
        self._parseProgramHeaders()

    def _parserExtendedHeader(self):
        ExtendedHeader = Struct(
            "e_type" / self.Elf64_Half if self.b64 else self.Elf32_Half,        # Object file type
            "e_machine" / self.Elf64_Half if self.b64 else self.Elf32_Half,     # Machine type
            "e_version" / self.Elf64_Word if self.b64 else self.Elf32_Word,     # Object file version
            "e_entry" / self.Elf64_Addr if self.b64 else self.Elf32_Addr,       # Entry point address
            "e_phoff" / self.Elf64_Off if self.b64 else self.Elf32_Off,         # Program header offset
            "e_shoff" / self.Elf64_Off if self.b64 else self.Elf32_Off,         # Section header offset
            "e_flags" / self.Elf64_Word if self.b64 else self.Elf32_Word,       # Processor-specific flags
            "e_ehsize" / self.Elf64_Half if self.b64 else self.Elf32_Half,      # ELF header size
            "e_phentsize" / self.Elf64_Half if self.b64 else self.Elf32_Half,   # Size of program header entry
            "e_phnum" / self.Elf64_Half if self.b64 else self.Elf32_Half,       # Number of program header entries
            "e_shentsize" / self.Elf64_Half if self.b64 else self.Elf32_Half,   # Size of section header entry
            "e_shnum" / self.Elf64_Half if self.b64 else self.Elf32_Half,       # Number of section header entries
            "e_shstrndx" / self.Elf64_Half if self.b64 else self.Elf32_Half,    # Section name string table index
        )
        print(ExtendedHeader.sizeof())
        self.extendedHeader = ExtendedHeader.parse(self.fp[self.EI_NIDENT : ])
        print(self.extendedHeader)

    def _parseSectionHeaders(self):
        SectionHeaders = Struct(
            "sections" / Array(lambda ctx: self.e_shnum,
                "section" / Struct(
                    "sh_name" / self.Elf64_Word if self.b64 else self.Elf32_Word,
                    "sh_type" / self.Elf64_Word if self.b64 else self.Elf32_Word,
                    "sh_flags" / self.Elf64_Xword if self.b64 else self.Elf32_Word,
                    "sh_addr" / self.Elf64_Addr if self.b64 else self.Elf32_Addr,
                    "sh_offset" / self.Elf64_Off if self.b64 else self.Elf32_Off,
                    "sh_size" / self.Elf64_Xword if self.b64 else self.Elf32_Word,
                    "sh_link" / self.Elf64_Word if self.b64 else self.Elf32_Word,
                    "sh_info" / self.Elf64_Word if self.b64 else self.Elf32_Word,
                    "sh_addralign" / self.Elf64_Xword if self.b64 else self.Elf32_Word,
                    "sh_entsize" /self.Elf64_Xword if self.b64 else self.Elf32_Word,
                    "allocate" / Computed(lambda ctx: (ctx.sh_type not in (0, 8) and ctx.sh_size > 0)),
                )
            )
        )
        if self.e_shnum:
            print("SH_size: {}".format(SectionHeaders.sizeof() / self.e_shnum))
        self.sectionHeaders = SectionHeaders.parse(self.fp[self.e_shoff : ])
        for idx, section in enumerate(self.sectionHeaders.sections):
            if section.allocate:
                image = self.fp[section.sh_offset : section.sh_offset + section.sh_size]
            else:
                image = None
            self._images[idx] = image
            section.image = image
        for section in self.sectionHeaders.sections:
            name = self.getString(self.e_shstrndx, section.sh_name)
            section.name = name
            self._sectionsByName[name] = section
            if section.sh_type == Sh_Type.SHT_NOTE:
                print("NOTE!!! {:08X} {:04X}".format(section.sh_offset, section.sh_size))
                self._parseNote(self.fp[section.sh_offset : section.sh_offset + section.sh_size])

    def getString(self, tableIndex, entry):
        name = self.asciiCString.parse(self._images[tableIndex][entry : ])
        print("getString: {}".format(name))
        return name

    def _parseProgramHeaders(self):
        ProgramHeaders = Struct(
            "segments" / Array(lambda ctx: self.e_phnum,
                "segment" / IfThenElse(lambda ctx: self.b64,
                    Struct(
                        "p_type" / self.Elf64_Word,
                        "p_flags" / self.Elf64_Word,
                        "p_offset" / self.Elf64_Off,
                        "p_vaddr" / self.Elf64_Addr,
                        "p_paddr" / self.Elf64_Addr,
                        "p_filesz" / self.Elf64_Xword,
                        "p_memsz" / self.Elf64_Xword,
                        "p_align" / self.Elf64_Xword,
                    ),
                    Struct(
                        "p_type" / self.Elf32_Word,
                        "p_offset" / self.Elf32_Off,
                        "p_vaddr" / self.Elf32_Addr,
                        "p_paddr" / self.Elf32_Addr,
                        "p_filesz" / self.Elf32_Word,
                        "p_memsz" / self.Elf32_Word,
                        "p_flags" / self.Elf32_Word,
                        "p_align" / self.Elf32_Word,
                    )
                ),
            )
        )
        if self.e_shnum:
            print("PG_size: {}".format(ProgramHeaders.sizeof() / self.e_phnum))
        self.programHeaders = ProgramHeaders.parse(self.fp[self.e_phoff : ])
        print(self.programHeaders)

    def _parseNote(self, data):
        Note = Struct(
            "namesz" / self.Elf64_Word if self.b64 else self.Elf32_Word,
            "descsz" / self.Elf64_Word if self.b64 else self.Elf32_Word,
            "type" / self.Elf64_Word if self.b64 else self.Elf32_Word,
            "name" / Bytes(this.namesz),
            "desc" / Bytes(this.descsz)
        )

        print(len(data), data.tobytes())
        result = Note.parse(data)
        #result.name = binascii.b2a_hex(result.name).decode()
        result.desc = binascii.b2a_hex(result.desc).decode()
        print(result.desc)
        print(result)

    def debugSections(self):
        debugSections = OrderedDict()
        for idx, section in enumerate(self.sections):
            name = section.name
            if name.startswith('.debug'):
                print(name)
                if name == '.debug_abbrev':
                    pass
                debugSections[name] = section
        result = OrderedDict()
        for name, section in debugSections.items():
            #image = self._images[idx]
            result[name]= DebugInfo(section, section.image)
        return result

    def getBasicHeaderField(self, name):
        return getattr(self.basicHeader.header.fields, name)

    def getExtendedHeaderField(self, name):
        return getattr(self.extendedHeader, name)

    @property
    def ei_class(self):
        return self.getBasicHeaderField('ei_class')

    @property
    def ei_data(self):
        return self.getBasicHeaderField('ei_data')

    @property
    def ei_version(self):
        return self.getBasicHeaderField('ei_version')

    @property
    def ei_osabi(self):
        return self.getBasicHeaderField('ei_osabi')

    @property
    def ei_abiversion(self):
        return self.getBasicHeaderField('ei_abiversion')

    @property
    def headerBytes(self):
        return self.basicHeader.header.bytes

    @property
    def e_type(self):
        return self.getExtendedHeaderField('e_type')

    @property
    def e_machine(self):
        return self.getExtendedHeaderField('e_machine')

    @property
    def e_version(self):
        return self.getExtendedHeaderField('e_version')

    @property
    def e_entry(self):
        return self.getExtendedHeaderField('e_entry')

    @property
    def e_phoff(self):
        return self.getExtendedHeaderField('e_phoff')

    @property
    def e_shoff(self):
        return self.getExtendedHeaderField('e_shoff')

    @property
    def e_flags(self):
        return self.getExtendedHeaderField('e_flags')

    @property
    def e_ehsize(self):
        return self.getExtendedHeaderField('e_ehsize')

    @property
    def e_phentsize(self):
        return self.getExtendedHeaderField('e_phentsize')

    @property
    def e_phnum(self):
        return self.getExtendedHeaderField('e_phnum')

    @property
    def e_shentsize(self):
        return self.getExtendedHeaderField('e_shentsize')

    @property
    def e_shnum(self):
        return self.getExtendedHeaderField('e_shnum')

    @property
    def e_shstrndx(self):
        return self.getExtendedHeaderField('e_shstrndx')

    @property
    def sections(self):
        return self.sectionHeaders.sections


from objutils.dwarf.encoding import ULEB, SLEB

def doAbbrevs(section):
    image = section.image
    #Abbrevations = Struct(
    #    "abbrevations" / Array(lambda ctx: self.e_shnum,
    #        "abbrevation" / Struct(
    #        )
    #    )
    #)

    """
    print("   {0:d}      {1!s}    [{2!s}]".format(code, tag, "has children" if children == constants.DW_CHILDREN_yes else "no children"))
    while True:
        attrValue = dr.uleb()
        attr = constants.AttributeEncoding(attrValue)
        formValue = dr.uleb()
    """

    Abbrevation = Struct(
        "start" / Tell,
        "code" / ULEB,
        "details" / If(lambda ctx: ctx.code != 0,
           Struct(
                "tag" / ULEB,
                "children" / Int8ul,
            )
        ),
        "stop" / Tell,
    )

    Attribute = Struct(
        "start" / Tell,
        "attrValue" / ULEB,
        "formValue" / ULEB,
        "stop" / Tell,
        "next"/ Computed((this.attrValue !=0) and (this.formValue != 0)),
    )
    print(bytearray(section.image))

    length = len(section.image)
    print("LEN: {}".format(length))

    offset = 0
    number = 1
    while True:
        print("OFS: {} NUM: {}".format(offset, number))
        abbrev = Abbrevation.parse(image[offset : ])
        #print(abbrev)
        if abbrev.code != 0:
            print("{} {}".format(abbrev.code, constants.TAG_MAP.get(abbrev.details.tag, abbrev.details.tag)))
        offset += abbrev.stop - abbrev.start
        if offset >= length:
            break
        number += 1
        if abbrev.code == 0:
            continue
        #if abbrev.children:
        while True:
            attr = Attribute.parse(image[offset : ])
            #print("    OFS: {}".format(offset))
            #print("   {}".format(attr))
            print("   {} {}".format(constants.ATTR_MAP.get(attr.attrValue, attr.attrValue), constants.FORM_MAP.get(attr.formValue, attr.formValue)))
            offset += (attr.stop - attr.start)
            if not attr.next:
                #offset += 1
                break


def doMacInfo(section):
    image = section.image
    #print(bytearray(section.image))

    length = len(section.image)
    print("LEN: {}".format(length))

    MacInfo = Struct(
        "start" / Tell,
        "macType" / ULEB,

        "parameters" / If(this.macType != constants.DW_MACINFO_end_file,
           Struct(
                "lineNumber" / ULEB,
                "param" / IfThenElse(lambda ctx: ctx._.macType in (constants.DW_MACINFO_start_file, ),
                    ULEB,
                    CString(encoding = "ascii"),
                ),
            ),
        ),
        "stop" / Tell,
    )
    offset = 0
    while True:
        macInfo = MacInfo.parse(image[offset : ])
        offset += macInfo.stop - macInfo.start
        print(offset, macInfo)
        if offset >= length - 1:
            break

def main():
    #fname = r'f:\projekte\csProjects\yOBJl\objutils\tests\ELFFiles\lib_with_two_dynstr_sections_reversed.so.1.elf'
    fname = r'f:\projekte\csProjects\yOBJl\objutils\tests\ELFFiles\testfile51'
    #fname = r'C:\projekte\csProjects\yOBJl\objutils\tests\ELFFiles\testfile_i686_core'
    ep = ElfParser(fname)
    print(ep.ei_class)
    print(ep.e_machine)
    print(ep.headerBytes)
    #pprint(ep._sectionsByName)
    print(Sh_Type.SHT_NOTE == 7)
    dbSecs = ep.debugSections()
    abbrevs = dbSecs['.debug_abbrev']
    doAbbrevs(abbrevs)
    macs = dbSecs['.debug_macinfo']
    doMacInfo(macs)
    #print(bytes(macs.image))

if __name__ == '__main__':
    main()


"""
ei_osabi
--------
Value   ABI
0x00    System V
0x01    HP-UX
0x02    NetBSD
0x03    Linux
0x06    Solaris
0x07    AIX
0x08    IRIX
0x09    FreeBSD
0x0A    Tru64
0x0B    Novell Modesto
0x0C    OpenBSD
0x0D    OpenVMS
0x0E    NonStop Kernel
0x0F    AROS
0x10    Fenix OS
0x11    CloudABI
0x53    Sortix
"""
