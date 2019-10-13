
# Code for finding dependencies by reading directly from Windows executable and DLL files (PE
# files).
#
# I switched to this because BindImageEx was not returning all dependencies.  The example I
# remember is Python 3.7's _ssl.pyd.

import sys
from ctypes import c_byte, c_char, c_ushort, c_ulong, c_long, c_ulonglong
from ctypes import Structure, sizeof
from os.path import exists, isabs

BYTE      = c_byte
WORD      = c_ushort
DWORD     = c_ulong
LONG      = c_long
ULONGLONG = c_ulonglong

IMAGE_DOS_SIGNATURE = 0x5A4D      # MZ
IMAGE_NT_SIGNATURE = 0x00004550  # PE00
IMAGE_NT_OPTIONAL_HDR32_MAGIC = 0x10b
IMAGE_NT_OPTIONAL_HDR64_MAGIC = 0x20b
IMAGE_NUMBEROF_DIRECTORY_ENTRIES = 16

IMAGE_FILE_SYSTEM = 0x1000  # System File.


class ImageInfo:
    """
    Information about the file that we need to know when determining which files to copy.
    """
    def __init__(self, path, issystem, dependencies):
        self.path = path
        # The fully qualified path to the image.

        self.issystem = issystem
        # True if the DLL's Characteristic has the IMAGE_FILE_SYSTEM bit set.  If set, we know
        # not to copy it.  Unfortunately this doesn't seem to be used.

        self.dependencies = dependencies
        # A list of DLL names this image depends on.  These are from the image's import table,
        # so they are just names and do not include a path.

    def __repr__(self):
        return '<ImageInfo %s issystem=%s deps=%r>' % (self.path, self.issystem, self.dependencies)


def find_dependencies(filename):
    """
    Returns an ImageInfo describing the file.
    """
    assert isabs(filename) and exists(filename)
    pefile = PEFile(filename)
    return ImageInfo(
        filename,
        pefile.issystem,
        ([] if pefile.issystem else pefile.dependencies)
    )


class PEFile:
    # This is a lot less efficient than I'd like, but ctypes structs require mutable buffers so
    # I don't seem to be able to use a read-only memory mapped file.
    #
    # This initial implementation reads tiny chunks from the file a little at a time.  If we
    # need some more efficiency, the read_imports part should be rewritten to read the entire
    # import section into memory at once.  The names should be in the same section.

    def __init__(self, path):
        self.path = path        # fully qualified filename

        self.file = open(self.path, 'rb')
        self.dosheader     = self._read_dosheader()
        self.ntheader      = self._read_ntheader()
        self.section_headers = self._read_section_headers()

        self.issystem = (self.ntheader.FileHeader.Characteristics & IMAGE_FILE_SYSTEM) != 0

        self.dependencies = self._read_dependencies()

        self.file.close()
        self.file = None

    def _read_dosheader(self):
        # This is the beginning of the file, so this one is easy.
        s = self._read_structure(0, IMAGE_DOS_HEADER)
        if s.e_magic != IMAGE_DOS_SIGNATURE:
            sys.exit('%s is not a valid Windows executable or DLL' % self.path)
        return s

    def _read_ntheader(self):
        # The DOS header's e_lfanew is the offset in the file of the "new exe" header.
        s = self._read_structure(self.dosheader.e_lfanew, IMAGE_NT_HEADERS64)
        if s.Signature != IMAGE_NT_SIGNATURE:
            sys.exit('%s is not a valid Windows executable or DLL' % self.path)
        if s.OptionalHeader.Magic == IMAGE_NT_OPTIONAL_HDR32_MAGIC:
            sys.exit('%s is a 32-bit DLL which Kelvin does not support' % self.path)
        if s.OptionalHeader.Magic != IMAGE_NT_OPTIONAL_HDR64_MAGIC:
            sys.exit('%s is not a valid Windows executable or DLL' % self.path)
        return s

    def _read_section_headers(self):
        """
        Returns the array of IMAGE_SECTION_HEADERs that describe the locations of the sections in
        this file.
        """
        # The section headers are an array of fixed-size structures immediately following the
        # DOS and NT headers.  They pretty much just have the addresses of the sections.
        offset = self.dosheader.e_lfanew + sizeof(self.ntheader)
        dtype = IMAGE_SECTION_HEADER * self.ntheader.FileHeader.NumberOfSections
        return self._read_structure(offset, dtype)

    def _read_dependencies(self):
        """
        Reads the file dependencies from the import table.
        """
        # The 2nd directory entry is always for the import table.  It will have an RVA, but
        # remember that is the address after the loader moves sections around to align them.
        # Convert the RVA to a file pointer.
        #
        # We also don't know exactly which section (usually ".rdata") so we have to first find
        # the right section by finding the one that would contain the RVA if it was moved
        # around.  Then we use its settings to adjust our pointer into that section in the
        # file.

        rva = self.ntheader.OptionalHeader.DataDirectory[1].VirtualAddress
        if not rva:
            # This file doesn't have an import table.
            return []

        section = self.section_header_from_rva(rva)

        ptr = self.ptr_from_rva(section, rva)

        # We really should just read id in the entire array of import descriptors, but I'm not
        # sure the right way to find the number of them.  Just reading in the entire section
        # would be good enough.

        deps = []

        while True:
            desc = self._read_structure(ptr, IMAGE_IMPORT_DESCRIPTOR)
            if not desc.Name:
                break
            np = self.ptr_from_rva(section, desc.Name)
            name = self._str_from_buffer(np, 255)
            deps.append(name)

            ptr += sizeof(IMAGE_IMPORT_DESCRIPTOR)

        return deps

    def _str_from_buffer(self, offset, maxlength):
        self.file.seek(offset)
        buf = self.file.read(maxlength)
        ix = buf.find(0)
        if ix != -1:
            buf = buf[:ix]
        return buf.decode('mbcs')

    def _read_structure(self, offset, struct):
        self.file.seek(offset)
        buf = bytearray(self.file.read(sizeof(struct)))
        return struct.from_buffer(buf)

    def section_header_from_rva(self, rva):
        """
        Returns the section that contains the relative address.
        """
        for s in self.section_headers:
            if s.VirtualAddress <= rva < (s.VirtualAddress + s.VirtualSize):
                return s
        return None

    def ptr_from_rva(self, section, rva):
        """
        Converts an RVA in a section to a file pointer.

        An RVA is a relative offset into the module after it is read into memory and has been
        processed by the loader.  In particular, sections are aligned in memory but are
        contiguous in files.  Fortunately the sections tell us what their virtual address would
        be (which would match the RVA) and we can adjust the RVA to account for the fact that
        we are dealing with the original, unmodified file.
        """
        # The VirtualAddress is where the linker should put the section, but PointerToRawData
        # is where it is in the file (IIRC).
        return rva - section.VirtualAddress + section.PointerToRawData


class IMAGE_SECTION_HEADER(Structure):
    _fields_ = [
        ('Name', c_char * 8),
        ('VirtualSize', DWORD),
        ('VirtualAddress', DWORD),
        ('SizeOfRawData', DWORD),
        ('PointerToRawData', DWORD),
        ('PointerToRelocations', DWORD),
        ('PointerToLinenumbers', DWORD),
        ('NumberOfRelocations', WORD),
        ('NumberOfLinenumbers', WORD),
        ('Characteristics', DWORD)
    ]


class IMAGE_DOS_HEADER(Structure):
    _pack_ = 1
    _fields_ = [
        ('e_magic', WORD),                     # Magic number
        ('e_cblp', WORD),                      # Bytes on last page of file
        ('e_cp', WORD),                        # Pages in file
        ('e_crlc', WORD),                      # Relocations
        ('e_cparhdr', WORD),                   # Size of header in paragraphs
        ('e_minalloc', WORD),                  # Minimum extra paragraphs needed
        ('e_maxalloc', WORD),                  # Maximum extra paragraphs needed
        ('e_ss', WORD),                        # Initial (relative) SS value
        ('e_sp', WORD),                        # Initial SP value
        ('e_csum', WORD),                      # Checksum
        ('e_ip', WORD),                        # Initial IP value
        ('e_cs', WORD),                        # Initial (relative) CS value
        ('e_lfarlc', WORD),                    # File address of relocation table
        ('e_ovno', WORD),                      # Overlay number
        ('e_res', WORD * 4),                    # Reserved words
        ('e_oemid', WORD),                     # OEM identifier (for e_oeminfo)
        ('e_oeminfo', WORD),                   # OEM information; e_oemid specific
        ('e_res2', WORD * 10),                  # Reserved words
        ('e_lfanew', LONG),                    # File address of new exe header
    ]


class IMAGE_DATA_DIRECTORY(Structure):
    _pack_ = 4
    _fields_ = [
        ('VirtualAddress', DWORD),
        ('Size', DWORD)
    ]


class IMAGE_OPTIONAL_HEADER64(Structure):
    _pack_ = 4
    _fields_ = [
        ('Magic',        WORD),
        ('MajorLinkerVersion', BYTE),
        ('MinorLinkerVersion', BYTE),
        ('SizeOfCode', DWORD),
        ('SizeOfInitializedData', DWORD),
        ('SizeOfUninitializedData', DWORD),
        ('AddressOfEntryPoint', DWORD),
        ('BaseOfCode', DWORD),
        ('ImageBase', ULONGLONG),
        ('SectionAlignment', DWORD),
        ('FileAlignment', DWORD),
        ('MajorOperatingSystemVersion', WORD),
        ('MinorOperatingSystemVersion', WORD),
        ('MajorImageVersion', WORD),
        ('MinorImageVersion', WORD),
        ('MajorSubsystemVersion', WORD),
        ('MinorSubsystemVersion', WORD),
        ('Win32VersionValue', DWORD),
        ('SizeOfImage', DWORD),
        ('SizeOfHeaders', DWORD),
        ('CheckSum', DWORD),
        ('Subsystem', WORD),
        ('DllCharacteristics', WORD),
        ('SizeOfStackReserve', ULONGLONG),
        ('SizeOfStackCommit', ULONGLONG),
        ('SizeOfHeapReserve', ULONGLONG),
        ('SizeOfHeapCommit', ULONGLONG),
        ('LoaderFlags', DWORD),
        ('NumberOfRvaAndSizes', DWORD),
        ('DataDirectory', IMAGE_DATA_DIRECTORY * IMAGE_NUMBEROF_DIRECTORY_ENTRIES)
    ]


class IMAGE_FILE_HEADER(Structure):
    _pack_ = 4
    _fields_ = [
        ('Machine', WORD),
        ('NumberOfSections',    WORD),
        ('TimeDateStamp',   DWORD),
        ('PointerToSymbolTable',   DWORD),
        ('NumberOfSymbols',   DWORD),
        ('SizeOfOptionalHeader',    WORD),
        ('Characteristics',    WORD),
    ]


class IMAGE_NT_HEADERS64(Structure):
    _pack_ = 4
    _fields_ = [
        ('Signature', DWORD),
        ('FileHeader', IMAGE_FILE_HEADER),
        ('OptionalHeader', IMAGE_OPTIONAL_HEADER64)
    ]


class IMAGE_IMPORT_DESCRIPTOR(Structure):
    _fields_ = [
        ('Characteristics', DWORD),  # 0 for last
        ('TimeDateStamp', DWORD),
        ('ForwarderChain', DWORD),  # -1 if no forwarders
        ('Name', DWORD),
        ('FirstThunk', DWORD)       # RVA to IAT
    ]
