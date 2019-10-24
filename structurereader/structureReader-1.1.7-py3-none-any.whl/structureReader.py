#-*- coding: utf-8 -*-

#!/usr/bin/python3

#!/Author : Gibartes

# https://www.sqlite.org/fileformat.html

import os,sys,struct
from collections import OrderedDict
from datetime import datetime, timedelta, tzinfo

class _StructureReaderConstant(object):
    # Error
    SUCCESS          = 0    # 성공
    EINVAL_ATTRIBUTE = -1   # Invalid attribute
    EINVAL_FILE      = -2   # Invalid file input
    EINVAL_TYPE      = -3   # Invalid data type
    EINVAL_NONE      = -4   # Nothing to getw

    BYTE   = 1
    WORD   = 2
    DWORD  = 4
    QWORD  = 8
    UINT8  = 1
    UINT16 = 2
    UINT32 = 4
    UINT64 = 8

    enable  = 1
    disable = 0

class _SQLStructure(object):

    def __init__(self):
        # db file size = size_in_header_database * size_page
        self.dataBaseHeader = OrderedDict({
            "signature"                     :[ 0,16,None], # The header string: "SQLite format 3\000"
            "size_page"                     :[16, 2,None], # The database page size in bytes. 512~32768, or the value 1 representing a page size of 65536.
            "ver_write"                     :[18, 1,None], # File format write version. 1 for legacy; 2 for WAL.
            "ver_read"                      :[19, 1,None], # File format read version. 1 for legacy; 2 for WAL.
            "unused"                        :[20, 1,None], # Bytes of unused "reserved" space at the end of each page. Usually 0.
            "frmaxe"                        :[21, 1,None], # Maximum embedded payload fraction. Must be 64.
            "frmine"                        :[22, 1,None], # Minimum embedded payload fraction. Must be 32.
            "frleaf"                        :[23, 1,None], # Leaf payload fraction. Must be 32.
            "fcc"                           :[24, 4,None], # File change counter.
            "size_database"                 :[28, 4,None], # Size of the database file in pages. The "in-header database size".
            "pnum_of_free"                  :[32, 4,None], # Page number of the first freelist trunk page.
            "pnum_of_to_free"               :[36, 4,None], # Total number of freelist pages.
            "schema_cookie"                 :[40, 4,None], # The schema cookie.
            "schema_form"                   :[44, 4,None], # The schema format number. Supported schema formats are 1, 2, 3, and 4.
            "size_page_cache"               :[48, 4,None], # Default page cache size.
            "pnum_root"                     :[52, 4,None], # The page number of the largest root b-tree page when in auto-vacuum or incremental-vacuum modes, or zero otherwise.
            "encoding"                      :[56, 4,None], # The database text encoding. A value of 1 means UTF-8. A value of 2 means UTF-16le. A value of 3 means UTF-16be.
            "ver_user"                      :[60, 4,None], # The "user version" as read and set by the user_version pragma.
            "modeinc"                       :[64, 4,None], # True (non-zero) for incremental-vacuum mode. False (zero) otherwise.
            "appid"                         :[68, 4,None], # The "Application ID" set by PRAGMA application_id.
            "reserved"                      :[72,20,None], # Reserved for expansion. Must be zero.
            "ver_valid"                     :[92, 4,None], # The version-valid-for number.
            "versqlite"                     :[96, 4,None], # SQLITE_VERSION_NUMBER
        })
        self.btreePageHeader = OrderedDict({
            "flag"                          :[ 0, 1,None], # The one-byte flag at offset 0 indicating the b-tree page type.
                                                           # 0x2 : index-B-Tree internal node / 0xA : index-B-Tree Leaf node
                                                           # 0x5 : B-Tree internal node       / 0xD : B-Tree Leaf node
            "ffb"                           :[ 1, 2,None], # The two-byte integer at offset 1 gives the start of the first freeblock on the page, or is zero if there are no freeblocks.
            "num_of_cells"                  :[ 3, 2,None], # The two-byte integer at offset 3 gives the number of cells on the page.
            "start_cell"                    :[ 5, 2,None], # The two-byte integer at offset 5 designates the start of the cell content area. A zero value for this integer is interpreted as 65536.
            "frag_free"                     :[ 7, 1,None], # The one-byte integer at offset 7 gives the number of fragmented free bytes within the cell content area.
            "pointer"                       :[ 8, 4,None], # The four-byte page number at offset 8 is the right-most pointer.
                                                           # This value appears in the header of interior b-tree pages only and is omitted from all other pages.
                                                           # Sizeof(B-Tree Header) : Leaf Pages : 8 Bytes / Interior Pages : 12 Bytes
        })
        self.rollBackJournal = OrderedDict({
            "signature"                     :[ 0, 8,None], # Header string: 0xd9, 0xd5, 0x05, 0xf9, 0x20, 0xa1, 0x63, 0xd7
            "count_page"                    :[ 8, 4,None], # The "Page Count" - The number of pages in the next segment of the journal, or -1 to mean all content to the end of the file
            "nonce"                         :[12, 4,None], # A random nonce for the checksum
            "size_initial"                  :[16, 4,None], # Initial size of the database in pages
            "size_disk_sectior"             :[20, 4,None], # Size of a disk sector assumed by the process that wrote this journal.
            "size_pages_in_this"            :[24, 4,None], # Size of pages in this journal.
        })
        self.walHeader       = OrderedDict({
            "signature"                     :[ 0, 4,None], # Magic number. 0x377f0682 or 0x377f0683
            "version"                       :[ 4, 4,None], # File format version.
            "size_page"                     :[ 8, 4,None], # Database page size
            "checkpoint_sequnce"            :[12, 4,None], # Checkpoint sequence number
            "salt_1"                        :[16, 4,None], # Salt-1: random integer incremented with each checkpoint
            "salt_2"                        :[20, 4,None], # Salt-2: a different random number for each checkpoint
            "checksum_1"                    :[24, 4,None], # Checksum-1: First part of a checksum on the first 24 bytes of header
            "checksum_2"                    :[28, 4,None], # Checksum-2: Second part of the checksum on the first 24 bytes of header
        })
        self.walFormatHeader = OrderedDict({
            "number_page"                   :[ 0, 4,None], # Page number
            "record_type"                   :[ 4, 4,None], # For commit records, the size of the database file in pages after the commit. For all other records, zero.
            "salt_1"                        :[ 8, 4,None], # Salt-1 copied from the WAL header
            "salt_2"                        :[12, 4,None], # Salt-2 copied from the WAL header
            "checksum_1"                    :[16, 4,None], # Checksum-1: Cumulative checksum up through and including this page
            "checksum_2"                    :[20, 4,None], # Checksum-2: Second half of the cumulative checksum.
        })
        # Leaf Cells [CellHeader,Record[DataHeader,Data of Field]]
        self.cellHeader      = OrderedDict({
            "length"                        :[ 0,None,None],    # Length of the Record (Varaiable length)
            "rowid"                         :[None,None,None],  # Primary key
        })
        self.dataHeader      = OrderedDict({
            "length"                        :[ 0, 2,None],  # [2 Bytes] Length of the data Header in the record.
            "dataheader"                    :[ 2,None,None] # Array of the size of fields
        })

    @staticmethod
    def virtual_page_offset(pageNum,pageSize):
        return (pageNum-1)*pageSize

# https://github.com/libyal/libscca/blob/master/documentation/Windows%20Prefetch%20File%20(PF)%20format.asciidoc
# See https://github.com/PoorBillionaire/Windows-Prefetch-Parser/blob/master/windowsprefetch/prefetch.py
# Problem : Without RtlDecompressBufferEx which is defined in windll.ntdll.

class _PrefetchStructure(object):

    PrefetchVersion  = {
        17:("Windows XP","Windows 2003"),
        23:("Windows Vista","Windows 7"),
        26:("Windows 8.1"),
        30:("Windows 10")
    }
    def __init__(self):
        # LZXPRESS Huffman compressed data (Originally NT.DLL needs to do)
        self.MAMHeader  = OrderedDict({
            "signature" : [ 0, 4,None],  # Signature  0x4d, 0x41, 0x4d
            "size"      : [ 4, 8,None],  # Total uncompressd data size
        })
        # Follows

        self.SCCAHeader = OrderedDict({
            "version"   : [ 0, 4,None],  # Format version
            "signature" : [ 4, 4,None],  # Signature SCCA
            "unknown"   : [ 8, 4,None],
            "size"      : [12, 4,None],  # File Size
            "name"      : [16,60,None],  # Executable Filename (UTF16-LE + EOF Char), The executable filename will store a maximum of 29 characters
            "hash"      : [76, 4,None],  # Prefetch Hash
            "flag"      : [80, 4,None],  # 0x01 -> boot prefetch
        })

        self.FileInfoCommon = OrderedDict({
            "maro"      : [ 0, 4,None],  # File metrics array offset. The offset is relative to the start of the file.
            "nfme"      : [ 4, 4,None],  # Number of file metrics entries
            "tcaro"     : [ 8, 4,None],  # Trace chains array offset. The offset is relative to the start of the file.
            "ntcae"     : [12, 4,None],  # Number of trace chains array entries
            "fnso"      : [16, 4,None],  # Filename strings offset
            "fnss"      : [20, 4,None],  # Filename strings size
            "vio"       : [24, 4,None],  # Volumes information offset
            "nov"       : [28, 4,None],  # Number of volumes
            "vis"       : [32, 4,None],  # Volumes information size
        })

        self.FileMetrics17 = OrderedDict({
            "start"     : [ 0, 4,None],  # Prefetch start time
            "duration"  : [ 4, 8,None],  # Duration Time
            "fso"       : [ 8, 4,None],  # Filename string offset. The offset is relative to the start of the filename strings
            "fsnoc"     : [12, 4,None],  # Filename string number of characters. (Does not include eoc.)
            "flags"     : [16, 4,None],
        })

        self.FileMetrics23 = OrderedDict({
            "start"     : [ 0, 4,None],  # Prefetch start time
            "duration"  : [ 4, 8,None],  # Duration Time
            "unknown"   : [ 8, 4,None],  # Average prefetch duration time
            "fso"       : [12, 4,None],  # Filename string offset. The offset is relative to the start of the filename strings
            "fsnoc"     : [16, 4,None],  # Filename string number of characters. (Does not include eoc.)
            "flags"     : [20, 4,None],
            "mft"       : [24, 8,None],  # File reference ($MFT)
        })

        self.TraceChain17      = OrderedDict({
            "naei"      : [ 0, 4,None],  # Next array entry index. Contains the next trace chain array entry index in the chain, where the first entry index starts with 0, or -1 (0xffffffff) for the end-of-chain.
            "tblc"      : [ 4, 4,None],  # Total block lad count. Total number of blocks loaded (or fetched)
            "unknown"   : [ 8, 1,None],
            "unknown1"  : [ 9, 1,None],
            "unknown2"  : [10, 2,None],
        })

        self.TraceChain30      = OrderedDict({
            "tblc"      : [ 0, 4,None],  # Total block lad count. Total number of blocks loaded (or fetched)
            "flags"     : [ 4, 1,None],
            "unknown"   : [ 5, 1,None],
            "unknown1"  : [ 6, 2,None],
        })

        self.VolumeInfoEntry17 = OrderedDict({
            "vdpo"      : [ 0, 4,None],  # Volume device path offset. The offset is relative from the start of the volume information
            "vdpnc"     : [ 4, 4,None],  # Volume device path number of characters
            "create"    : [ 8, 8,None],  # Volume creation time. Contains a FILTIME
            "vsn"       : [16, 4,None],  # Volume serial number
            "fro"       : [20, 4,None],  # File reference offset
            "frds"      : [24, 4,None],  # File refernce data size
            "dso"       : [28, 4,None],  # Directory strings offset
            "nos"       : [32, 4,None],  # Number of directory strings
            "unknown"   : [36, 4,None],  # Unknown
        })

        self.VolumeInfoEntry23 = OrderedDict({
            "vdpo"      : [ 0, 4,None],  # Volume device path offset. The offset is relative from the start of the volume information
            "vdpnc"     : [ 4, 4,None],  # Volume device path number of characters
            "create"    : [ 8, 8,None],  # Volume creation time. Contains a FILTIME
            "vsn"       : [16, 4,None],  # Volume serial number
            "fro"       : [20, 4,None],  # File reference offset
            "frds"      : [24, 4,None],  # File refernce data size
            "dso"       : [28, 4,None],  # Directory strings offset
            "nos"       : [32, 4,None],  # Number of directory strings
            "unknown"   : [36, 4,None],  # Unknown
            "reserved"  : [40,28,None],  # Unknown
            "reserved1" : [68, 4,None],  # Unknown
            "reserved2" : [72,28,None],  # Unknown
            "reserved3" : [100,4,None],  # Unknwon (alignment padding?)
        })

        self.VolumeInfoEntry30  = OrderedDict({
            "vdpo"      : [ 0, 4,None],  # Volume device path offset. The offset is relative from the start of the volume information
            "vdpnc"     : [ 4, 4,None],  # Volume device path number of characters
            "create"    : [ 8, 8,None],  # Volume creation time. Contains a FILTIME
            "vsn"       : [16, 4,None],  # Volume serial number
            "fro"       : [20, 4,None],  # File reference offset
            "frds"      : [24, 4,None],  # File refernce data size
            "dso"       : [28, 4,None],  # Directory strings offset
            "nos"       : [32, 4,None],  # Number of directory strings
            "unknown"   : [36, 4,None],  # Unknown
            "reserved"  : [40,24,None],  # Unknown
            "reserved1" : [64, 4,None],  # Unknown
            "reserved2" : [78,24,None],  # Unknown
            "reserved3" : [92, 4,None],  # Unknwon (alignment padding?)
        })

class _MFTEntryHeader(object):

    def __init__(self):
        self.MFTEntryHeader = OrderedDict({
            "signature" : [ 0, 4,None],  # Signature  "FILE"
            "off_fixup" : [ 4, 2,None],  # Offset Fixup Array
            "num_fixup" : [ 6, 2,None],  # The number of fixup values
            "lsn"       : [ 8, 8,None],  # $LogFile Sequence Number
            "seq"       : [16, 2,None],  # Sequnce Value
            "num_hard"  : [18, 2,None],  # Hard link count
            "off_attr"  : [20, 2,None],  # Offset to the first attribute
            "flags"     : [22, 2,None],  # Flags
            "used_size" : [24, 4,None],  # Used size of this entry
            "alloc_size": [28, 4,None],  # Allocation size of this entry
            "file_ref"  : [32, 8,None],  # File reference to base mft entry
            "next_attr" : [40, 2,None],  # Next attribute ID
            "record_id" : [42, 6,None]   # ID of this record
        })

# https://github.com/msuhanov/regf/blob/master/Windows%20registry%20file%20format%20specification.md
class _RegistryStructure(object):

    BASEBLOCK_SIZE    = 0x1000
    HIVEBIN_SIZE      = 0x1000

    #KeyNode Flags

    KEY_VOLATILE      = 0x1
    KEY_HIVE_EXIT     = 0x2
    KEY_HIVE_ENTRY    = 0x4
    KEY_NO_DELETE     = 0x8
    KEY_SYM_LINK      = 0x10
    KEY_COMP_NAME     = 0x20
    KEY_PREDEF_HANDLE = 0x40

    def __init__(self):
        self.BaseBlock = OrderedDict({
            # Common
            "signature"     : [ 0, 4,None],  # "regf" ASCII string
            "prime"         : [ 4, 4,None],  # Primary Sequnce Number
            "second"        : [ 8, 4,None],  # Secondary Sequence Number
            "last_write"    : [12, 8,None],  # Last Written Number
            "major"         : [20, 4,None],  # Major Version
            "minor"         : [24, 4,None],  # Minor Version
            "type"          : [28, 4,None],  # File Type : 0 means primary file
            "format"        : [32, 4,None],  # File Format : 1 means direct memory load
            "root"          : [36, 4,None],  # Root cell offset : Offset of a root cell in bytes, relative from the start of the hive bins data
            "hbs"           : [40, 4,None],  # Hive bins data size : Size of the hive bins data in bytes
            "clf"           : [44, 4,None],  # Clustering Factor
            "filename"      : [48,64,None],  # File name : UTF-16LE string used for debugging purposes
            # Windows 10
            "rmid"          : [112,16,None], # GUID
            "logid"         : [128,16,None], # GUID
            "flags"         : [144,4,None],  # Bitmask : 1-> KTM locked the hive
                                             # 2 -> The hive has been defragmented and it is being written to a disk .
            "tmid"          : [148,16,None], # GUID
            "gsig"          : [164,4,None],  # "rmtm" ASCII string
            "ltsmp"         : [168,8,None],  # Last reogranized timestamp : FILETIME(UTC)
            # offreg.dll
            "osig"          : [176,4,None],  # "OfRg" ASCII string
            "oflags"        : [180,4,None],  # "This is the only value used"
            # Common
            "checksum"      : [508,4,None],  # XOR-32 checksum of the previous 508 bytes
            # offreg.dll
            "stsmp"         : [512,8,None],  # Serialized Timestamp FILETIME (UTC)
            # reserved_1    : [512,3576,None],
            # boot_type     : [4088,4,None], # This field has no meaning on a disk
            # boot_recover  : [4092,4,None], # This field has no meaning on a disk
        })

        self.HiveBin  = OrderedDict({
            "signature"     : [ 0, 4,None],  # "hbin" ASCII string
            "offset"        : [ 4, 4,None],  # Offset of a current hive bin in bytes, relative from the start of the hive bins data
            "size"          : [ 8, 4,None],  # Size of a current hive bin in bytes
            "reserved"      : [12, 8,None],
            "timestamp"     : [20, 4,None],  # FILETIME(UTC), defined for the first hive bin only
                                             # A Timestamp in the header of the first hive bin acts as a backup copy of a Last written timestamp in the base block.
            "spare"         : [28, 4,None],  # This field has no meaning on a disk
        })

        # In the case of the Index Leaf, Fast Leaf, Hash Leaf and Index Root
        self.Cell     = OrderedDict({
            "size"          : [ 0, 4,None],  # Size of a current cell in bytes. the size is positive if a cell is unallocated or negative if a cell is allocated.
            "type"          : [ 4, 2,None],
            "noe"           : [ 6, 2,None],  # Number of elements
        })

        # Key node cell
        self.KeyNode  = OrderedDict({
            "size"          : [ 0, 4,None],  # Size of a current cell in bytes. the size is positive if a cell is unallocated or negative if a cell is allocated.
            "type"          : [ 4, 2,None],  # "nk" ASCII String
            "flags"         : [ 6, 2,None],  # Bitmask
            "timestamp"     : [ 8, 8,None],  # Last written timestamp : FILETIME(UTC)
            "access_bit"    : [16, 4,None],  # Bitmask
            "parent"        : [20, 4,None],  # Offset of a parent key node in bytes, relative from the start of the hive bins data
            "nok"           : [24, 4,None],  # Number of subkeys
            "novk"          : [28, 4,None],  # Number of volatile subkeys
            "ko"            : [32, 4,None],  # Subkeys list offset : In bytes, relative from the start of the hive bins data
            "vko"           : [36, 4,None],  # Volatile subkeys list offset : This field has no meaning on a disk (volatile keys are not written to a file)
            "nov"           : [40, 4,None],  # Number of values
            "kvo"           : [44, 4,None],  # Key value list offset : In bytes, relative from the start of the hive bins data
            "ksot"          : [48, 4,None],  # Key security offset   : In bytes, relative from the start of the hive bins data
            "cno"           : [52, 4,None],  # Class name offst      : In bytes, relative from the start of the hive bins data
            "lsnl"          : [56, 4,None],  # Largest subkey name length : In bytes, a subkey name is treated as a UTF-16LE string
            "lscnl"         : [60, 4,None],  # Largest subkey class name length : In bytes, relative from the start of the hive bins data
            "lvnl"          : [64, 4,None],  # Largest value name length : In bytes, a value name is treated as UTF-16LE string
            "lvds"          : [68, 4,None],  # Largest value data size
            "work_var"      : [72, 4,None],  # Work var : Cached index
            "knl"           : [74, 2,None],  # Key name length
            "cnl"           : [76, 2,None],  # Class name length
            # Keyty name string...
        })

    def getRootCell(self):
        if(self.BaseBlock.get("root_cell")[_RegistryStructure.Value]!=None):
            return self.BaseBlock.get("root")[_RegistryStructure.Value] + \
                     _RegistryStructure.BASEBLOCK_SIZE
        return _StructureReaderConstant.EINVAL_NONE

# https://github.com/libyal/liblnk/blob/master/documentation/Windows%20Shortcut%20File%20(LNK)%20format.asciidoc
class _LinkFileStructure(object):

    class CLSID(object):
        CLSID_ShellDesktop  = (0x1E,0x1F)
        CLSID_MyComputer    = tuple(range(0x20,0x2F))
        CLSID_ShellFSFolder = tuple(range(0x30,0x3F))
        CLSID_Network       = tuple(range(0x40,0x4F))
        CLSID               = tuple(
                                CLSID_ShellDesktop+
                                CLSID_MyComputer+
                                CLSID_ShellFSFolder+CLSID_Network
                              )

    class Location(object):
        VolumeIDAndLocalBasePath               = 0x1
        CommonNetworkRelativeLinkAndPathSuffix = 0x2

    class DriveTypes(object):
        DRIVE_UNKNOWN       = 0x0
        DRIVE_NO_ROOT_DIR   = 0x1
        DRIVE_REMOVABLE     = 0x2
        DRIVE_FIXED         = 0x3
        DRIVE_REMOTE        = 0x4
        DRIVE_CDROM         = 0x5
        DRIVE_RAMDISK       = 0x6

    class NetShared(object):
        ValidDevice         = 0x1
        ValidNetType        = 0x2


    def __init__(self):
        self.ShellLinkHeader = OrderedDict({
            # ShellLinkHeader (76 Bytes)
            "size"          : [ 0, 4,None],  # The header size
            "id"            : [ 4,16,None],  # The LNK class identifier
            "flags"         : [20, 4,None],  # Data flags
            "fflags"        : [24, 4,None],  # File attribute flags
            "ctime"         : [28, 8,None],  # Creation date an time
            "atime"         : [36, 8,None],  # Last access date and time
            "ltime"         : [44, 8,None],  # Last modification date and time
            "fsize"         : [52, 4,None],  # File size in bytes
            "iival"         : [56, 4,None],  # Icon index value
            "swv"           : [60, 4,None],  # ShowWindow value. Contains an unsigned integer
            "hkey"          : [64, 2,None],  # Hot key
            "rsvd1"         : [66, 2,None],  # Reserved
            "rsvd2"         : [68, 4,None],  # Reserved
            "rsvd3"         : [72, 4,None],  # Reserved
            # Link target identifier (2+A)
            "lti"           : [76, 2,None],  # Link Target Identifier
        })
        self.ShellItemList  = OrderedDict({
            "size"          : [ 0, 2,None],  # The size of the shll item
            "type"          : [ 2, 2,None],  # Class type indicator
        })
        self.FileLocationInfo = OrderedDict({
            "size"          : [ 0, 4,None],  # The size of the location information
                                             # including the 4 bytes of the size itself
                                             # Location information header
            "hsize"         : [ 4, 4,None],  # Location information header size
            "flags"         : [ 8, 4,None],  # Location Flags
            "oftvi"         : [12, 4,None],  # Offset to the volume information
                                             # The offset is relative to the start of the location information
            "oftlp"         : [16, 4,None],  # Offset to the local path
            "oftnsi"        : [20, 4,None],  # Offset to the network share information
            "oftcp"         : [24, 4,None],  # Offset to the common path
        })
        self.VolumeInformation = OrderedDict({
            "size"          : [ 0, 4,None],  # The size of the volume information
                                             # including the 4 bytes of the size itself
            "drive"         : [ 4, 4,None],  # Drive Type
            "serial"        : [ 8, 4,None],  # Drive Serial Number
            "offvl"         : [12, 4,None],  # Offset to the volume label
                                             # The offset is relative to the start of the location information
        })
        self.NetworkShareInformation = OrderedDict({
            "size"          : [ 0, 4,None],  # The size of the network share information
                                             # including the 4 bytes of the size itself
            "flags"         : [ 4, 4,None],  # Network share flags
            "oftnm"         : [ 8, 4,None],  # Offset to the network share name
            "offdn"         : [12, 4,None],  # Offset to the device name
            "prvdr"         : [16, 4,None],  # Network provider type
        })

# https://github.com/libyal/libmsiecf/blob/master/documentation/MSIE%20Cache%20File%20(index.dat)%20format.asciidoc

class _IndexDatStructure(object):

    def __init__(self):
        self.IndexDatHeader          = OrderedDict({
            "signature"          : [ 0,28,None],  # signature, necessarily “Client UrlCache MMF Ver 5.2”, including null terminator
            "size"               : [28, 4,None],  # The file size
            "offhtr"             : [32, 4,None],  # The first hash table record offset
            "nob"                : [36, 4,None],  # The total number of blocks
            "nab"                : [40, 4,None],  # The number of allocated blocks
            "reserved"           : [44, 4,None],  # Unknown
            "lccs"               : [48, 8,None],  # The cache size(quota) limit of the container contains the number of bytes
            "ccs"                : [56, 8,None],  # The cache size of the container
            "cnrcs"              : [64, 8,None],  # The non-release cache size of the container
        })
        # offset 72
        self.CacheDirTable          = OrderedDict({
            "size"               : [ 0, 4,None],  # Number of cache directory entries
        })
        self.CachedDirTableEntry    = OrderedDict({
            "size"               : [ 0, 4,None],  # The number of cached files in the directory
            "name"               : [ 4, 8,None],  # Cache directory name ASCII string without an end-of-string character
        })
        self.HashTableRecord        = OrderedDict({
            "signature"          : [ 0, 4,None],  # "HASH". Ths signature
            "nob"                : [ 4, 4,None],  # The number of blocks in hash table. This value includes the size of the hash table header.
            "offnht"             : [ 8, 4,None],  # Next hash table record offset
                                                  # The file offset to the next part of the hash table or 0 if this is the last part of the hash table
            "seq"                : [12, 4,None],  # The sequnce number. 0 identifies the first hash table record
        })
        self.HashTableEntry         = OrderedDict({
            "hash"               : [ 0, 4,None],  # Record hash
            "offrec"             : [ 4, 4,None],  # Record offset
                                                  # This value always should be a multitude of 128 and greater equal 0x4000
                                                  # If the record offset contains the same value as the record hash the value is unused
        })
        self.URLRecord              = OrderedDict({
            "signature"          : [ 0, 4,None],
            "nob"                : [ 4, 4,None],  # The number of blocks in URL record
            "stv"                : [ 8, 8,None],  # The secondary time value Contains a FILETIME or 0 if not set
            "ptv"                : [16, 8,None],  # The primary time value Contains a FILETIME or 0 if not set
            "edt"                : [24, 4,None],  # Expiration date and time. Contains a FAT date time or 0 if not set
            "reserved"           : [28, 4,None],
            "lcfs"               : [32, 4,None],  # Cached file size. Contains the number of bytes
            "ucfs"               : [36, 4,None],  # Upper part of Cached file size. Contains the number of bytes
            "offgrp"             : [40, 4,None],  # Group or group list offset
            "td"                 : [44, 4,None],  # The non-releasble time delta. The time delta is relative to the last access time
            "reserved1"          : [48, 4,None],  # The value is relative to the start of the URL record
            "offloc"             : [52, 4,None],  # THe location offset
            "cdi"                : [56, 1,None],  # Cache directory index
            "sync"               : [57, 1,None],  # Synchronization Count
            "fver"               : [58, 1,None],  # Format version
            "cfver"              : [59, 1,None],  # Copy of format version
            "offname"            : [60, 4,None],  # The filename offset
            "ceflags"            : [64, 4,None],  # Cache entry flags
            "offdata"            : [68, 4,None],  # The data offset
            "size"               : [72, 4,None],  # The data size
            "offext"             : [76, 4,None],  # File extension offset or empty values
            "lcdt"               : [80, 4,None],  # Last checked data and time
            "noh"                : [84, 4,None],  # Number of hits (number of times the entry has benn locks)
            "reserved2"          : [88, 4,None],  # Use count used in memory? (level of lock nesting of the entry)
            "reserved3"          : [92, 4,None],  # Last cache synchronization date and time (entry creation time?)
            "reserved4"          : [96, 4,None],  # 8 byte aligned
            "reserved5"          : [100,4,None],  # Unknown
            # location offset
            # filename offset
            # data offset
        })
        self.URLRecord4              = OrderedDict({
            "signature"          : [ 0, 4,None],
            "nob"                : [ 4, 4,None],  # The number of blocks in URL record
            "stv"                : [ 8, 8,None],  # The secondary time value Contains a FILETIME or 0 if not set
            "ptv"                : [16, 8,None],  # The primary time value Contains a FILETIME or 0 if not set
            "edt"                : [24, 4,None],  # Expiration date and time. Contains a FAT date time or 0 if not set
            "reserved"           : [28, 4,None],
            "cfs"                : [32, 4,None],  # Cached file size. Contains the number of bytes
            "reserved1"          : [36,16,None],  # Upper part of Cached file size. Contains the number of bytes
            "reserved2"          : [52, 4,None],  # Group or group list offset
            "offloc"             : [56, 4,None],  # The non-releasble time delta. The time delta is relative to the last access time
            "cdi"                : [60, 1,None],  # Cache directory index
            "reserved3"          : [61, 3,None],  # Padding
            "offname"            : [64, 4,None],  # The filename offset
            "ceflags"            : [68, 4,None],  # Cache entry flags
            "offdata"            : [72, 4,None],  # The data offset
            "size"               : [76, 4,None],  # The data size
            "reserved4"          : [80, 4,None],  # ?
            "lcdt"               : [84, 4,None],  # Last checked data and time
            "noh"                : [87, 4,None],  # Number of hits (number of times the entry has benn locks)
            "reserved5"          : [92, 4,None],  # Use count used in memory? (level of lock nesting of the entry)
            "reserved6"          : [96, 4,None],  # Last cache synchronization date and time (entry creation time?)
            "reserved7"          : [100,4,None],  # ?
            # location offset
            # filename offset
            # data offset
        })
        self.RedirectRecord         = OrderedDict({
            "signature"          : [ 0, 4,None],
            "nob"                : [ 4 ,4,None],  # The number of blocks in redirected record The block size is 128 bytes
            "offhash"            : [ 8, 4,None],  # Target hash table entry offset The offset is relative from the start of the file
            "hash"               : [12, 4,None],  # Target URL hash value
            # locaction
        })
        self.LeakRecord             = OrderedDict({
            "signature"          : [ 0, 4,None],
            "nob"                : [ 4 ,4,None],  # The number of blocks in redirected record The block size is 128 bytes
            "reserved"           : [ 8,24,None],
            "cfs"                : [32, 4,None],  # Cached file size. Contains the number of bytes
            "reserved2"          : [36, 8,None],
            "next"               : [44, 4,None],  # Next leak record offset. The offset is relative from the start of the file
            "reserved3"          : [48, 8,None],
            "cdi"                : [56, 1,None],  # Cache directory index
            "reserved4"          : [57, 3,None],
            "offname"            : [60, 4,None],  # The filename offset
            "reserved5"          : [64,28,None],
            "reserved6"          : [92,12,None],
            # filename offset
        })

class _WindowsEventLogStructure(object):

    def __init__(self):
        self.evtFileHeader              = OrderedDict({
            "size"                   : [ 0, 4,None],  # Size
            "signature"              : [ 4, 4,None],  # Signature LfLe
            "major"                  : [ 8, 4,None],  # Major format version
            "minor"                  : [12, 4,None],  # Minor format version
            "off_fr"                 : [16, 4,None],  # First record offset
            "off_er"                 : [20, 4,None],  # End of file record offset
            "lrn"                    : [24, 4,None],  # Last record number
            "frn"                    : [28, 4,None],  # First record number
            "msize"                  : [32, 4,None],  # Maximum file size
            "flags"                  : [36, 4,None],  # File flags
            "reserved"               : [40, 4,None],  # Unknown
            "cos"                    : [44, 4,None],  # Copy of size. This value is used to indicate the end of the file header
        })
        self.evtRecord                 = OrderedDict({
            "size"                   : [ 0, 4,None],  # Size
            "signature"              : [ 4, 4,None],  # Signature LfLe
            "number"                 : [ 8, 4,None],  # Record number
            "create"                 : [12, 4,None],  # Creation date and time. 32Bit Unix epoch
            "written"                : [16, 4,None],  # Last written date and time. 32Bit Unix epoch
            "id"                     : [20, 4,None],  # Event identifier
            "type"                   : [24, 2,None],  # Event type
            "nos"                    : [26, 2,None],  # Number of strings
            "cat"                    : [28, 2,None],  # Event category
            "reserved"               : [30, 2,None],  # Unknown
            "reserved1"              : [32, 4,None],  # Unknown
            "off_str"                : [36, 4,None],  # Strings offset
            "uids"                   : [40, 4,None],  # User identifier size
            "uido"                   : [44, 4,None],  # User identifier offset
            "dsize"                  : [48, 4,None],  # Data size
            "off_da"                 : [52, 4,None],  # Data offset
            # Source name
            # Computer name
            # User SID (From uido)
            # Strings
            # Data
            # Padding (DWORD-align)
            # Copy of Size (4)
        })
        self.evtEndOfFileRecord         = OrderedDict({
            "size"                   : [ 0, 4,None],  # Size
            "signature1"             : [ 4, 4,None],  # Signature LfLe
            "signature2"             : [ 8, 4,None],  # Record number
            "signature3"             : [12, 4,None],  # Creation date and time. 32Bit Unix epoch
            "signature4"             : [16, 4,None],  # Creation date and time. 32Bit Unix epoch
            "off_fr"                 : [20, 4,None],  # Signature LfLe
            "off_er"                 : [24, 4,None],  # Record number
            "lrn"                    : [28, 4,None],  # Creation date and time. 32Bit Unix epoch
            "frn"                    : [32, 4,None],  # Creation date and time. 32Bit Unix epoch
            "cos"                    : [36, 4,None],  # Copy of size. This value is used to indicate the end of the file header
        })
        # evtx header size is 4KiB (4096)
        self.evtxFileHeader             = OrderedDict({
            "signature"              : [ 0, 8,None],  # Signature ElfFile\x00
            "fchunk"                 : [ 8, 8,None],  # First chunk number
            "lchunk"                 : [16, 8,None],  # Last chunk number
            "nrid"                   : [24, 8,None],  # Next record identifier
            "size"                   : [32, 4,None],  # Header size (128)
            "minor"                  : [36, 2,None],  # Minor version
            "major"                  : [38, 2,None],  # Major version
            "hbsize"                 : [40, 2,None],  # Header block size (chunk data offset)
            "noc"                    : [42, 2,None],  # Number of chunks
            "reserved"               : [44,76,None],  # Unknown
            "flags"                  : [120,4,None],  # File flags
            "checksum"               : [124,4,None],  # CRC32 of the first 120bytes of the file header
        })
        self.evtxFileChunkHeader        = OrderedDict({
            "signature"              : [ 0, 8,None],  # Signature ElfChnk\x00
            "fevrn"                  : [ 8, 8,None],  # First event record number
            "levrn"                  : [16, 8,None],  # Last evnet record number
            "fevrid"                 : [24, 8,None],  # First event record identifier
            "levrid"                 : [32, 8,None],  # Last event record identifier
            "size"                   : [40, 4,None],  # Header size (128)
            "off_last"               : [44, 4,None],  # Last event record data offset
            "off_free"               : [48, 4,None],  # Free space offset
            "erchk"                  : [52, 4,None],  # Event records checksum
            "reserved"               : [56,64,None],  # Unknown
            "flags"                  : [120,4,None],  # File flags
            "checksum"               : [124,4,None],  # CRC32 of the first 120 bytes and bytes 128 to 512 of the chunk.
        })
        self.evtxEventRecord            = OrderedDict({
            "signature"              : [ 0, 4,None],  # Signature 0x2a2a0000
            "size"                   : [ 4, 4,None],  # Event record size
            "erid"                   : [ 8, 8,None],  # Event record identifier
            "time"                   : [16, 8,None],  # Written date and time
            # Event : Contains binary XML
            # (4bytes) Copy of Size
        })

class _MP3Structure(object):
    FOOTER_BE   = 0x00FFFBE4
    FOOTER_LE   = 0xE4FBFF00
    FOOTER_BIN  = b'\xff\xfb\xe4'
    TAG1        = b'TAG'
    TAG2        = b'ID3'

    bitRateIndex = {
            0:0,
            1:32,
            2:40,
            3:48,
            4:56,
            5:64,
            6:80,
            7:96,
            8:112,
            9:128,
            10:160,
            11:192,
            12:224,
            13:256,
            14:320,
            15:0,
    }
    samplingRateIndex = {
            0:44100,
            1:48000,
            2:32000,
    }

    frameIdentifier   = [
        b'TRCK',b'TENC',b'WXXX',b'TCOP',b'TOPE',b'TCOM',
        b'TCON',b'COMM',b'TYER',b'TALB',b'TPE1',b'TIT2'
    ]

    def __init__(self):
        # TAG
        self.TagV1      = OrderedDict({
            "signature" : [ 0, 3,None],  # TAG
            "name"      : [ 3,30,None],  # Song Name
            "artist"    : [33,30,None],  # Artist
            "album"     : [63,30,None],  # Album
            "year"      : [93, 4,None],  # Year
            "comment"   : [97,30,None],  # Comment
            "genre"     : [127,1,None],  # Genre
        })
        self.TagV2      = OrderedDict({
            "signature" : [0, 3,None],  # ID3
            "major"     : [3, 1,None],  # ID3 Major
            "minor"     : [4, 1,None],  # ID3 Minor
            "flags"     : [5, 1,None],  # 7:Unsync,6:Extended,5:Experimental,4:Footer
            "tag_size"  : [6, 4,None],  # Header Size (Excl Footer Signature)
        })
        self.FrameHeader = OrderedDict({
            "frame"  : [0, 4,None],
            # AAAAAAAA AAABBCCD EEEEFFGH IIJJKLMM
            # A: Frame synchronizer
            # B: MPEG version ID
            # C: Layer
            # D: CRC Protection
            # E: Bitrate Index
            # F: Sampling rate frequency index
            # G: Padding
            # H: Private Bit
            # I: Channel
            # J: Mode extension
            # K: Copyright
            # L: Original
            # M: Emphasis
            # FrameLen = int(144*BitRate/SampleRate)+Padding
        })
        self.TagFrames   = OrderedDict({
            "id"        :[0,4,None],
            "size"      :[4,4,None],
            "flag"      :[8,2,None],
            # Frame identifier consist of four characters. 
        })
        self.VBRFrame    = OrderedDict({
            "signature":[  0,  4,None],
            "reserved" :[  4, 36,None],
            "flags"    :[ 40,  4,None],
            "frames"   :[ 44,  4,None],
            "length"   :[ 48,  4,None],
            "toc"      :[ 52,100,None],
            "scale"    :[152,  4,None],
        })

    @staticmethod
    def constant(_long):
        return (_long&0xFFFF0000)>>16
    @staticmethod
    def getFrameLen(bitrate,samplerate,padding):
        return int(int((144*bitrate*1000)/samplerate)+padding)
    @staticmethod
    def rate(_long):
        return ((_long&0xF000)>>12,(_long&0x0C00)>>10,(_long&0x0200)>>9)
    @staticmethod
    def frameLen(_long):
        b,s,p = MP3Structure.rate(_long)
        try:return MP3Structure.getFrameLen(MP3Structure.bitRateIndex.get(b,0),
                                        MP3Structure.samplingRateIndex.get(s,0),p)
        except:return 0
    @staticmethod
    def findMSB(n): 
        n|=n>>1
        n|=n>>2
        n|=n>>4
        n|=n>>8
        n|=n>>16
        n+=1
        return (n>>1)


class CStructure(object):
    def __init__(self,field=None,size=None):
        self.init()
        if(field!=None):
            self.build(field,size)

    def __add__(self,structure):
        if(type(structure)!=CStructure):
            return
        self.__data.update(structure)

    def __repr__(self):
        return str(type(self).__name__)

    def __str__(self):
        return str(type(self).__name__)

    def __byte2int(self,data,order='little'):
        try:return int.from_bytes(data,byteorder=order)
        except:return -1

    def init(self):
        self.__data = OrderedDict()
        self.__type = ""

    def copyof(self,structure):
        if(type(structure)!=OrderedDict()):
            return
        self.__data = structure

    def copy(self):
        return self.__data.copy()

    def sizeof(self):
        try:
            o,s,_ = tuple(list(self.__data.items())[-1][1])
            return o+s
        except:return -1

    def build(self,field,size=None):
        if(size==None and type(field)==OrderedDict):
            return self.__build_dict(field)
        if(type(field)==list and type(size)==list):
            return self.__build_struct(field,size)
        return False

    def __build_dict(self,field):
        offset = 0
        inx    = 0
        keys  = tuple(field.keys())
        value = tuple(field.values())
        
        while(inx<len(keys)):
            if(type(value[inx])!=int):
                return
            self.__data.update({keys[inx]:[offset,value[inx],None]})
            offset+=value[inx]
            inx+=1
        return True

    def __build_struct(self,field,size):
        if(len(field)!=len(size)):
            return False
        offset = 0
        inx    = 0
        while(inx<len(field)):
            if(type(size[inx])!=int):
                return
            self.__data.update({field[inx]:[offset,size[inx],None]})
            offset+=size[inx]
            inx+=1
        return True

    def push(self,field,offset,size,value=None):
        self.__data.update({field:[offset,size,value]})

    def pop(self,field):
        return self.__data.pop(field,None)

    def get(self,field):
        try:return self.__data.get(field,None)[2]
        except:return None

    def set(self,field,value):
        res = self.__data.get(field,None)
        if(res!=None and type(value)==int):
            self.__data.update({field:[res[0],res[1],value]})
        elif(res!=None and type(value) in (bytes,bytearray)):
            if(len(value)>res[1]):
                self.__data.update({field:[res[0],res[1],bytes(value[0:res[1]])]})
            else:
               self.__data.update({field:[res[0],res[1],bytes(value)]})

    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self,binary):
        try:
            _last = list(self.__data.items())[-1][1]
            _temp = binary[0:last_field[0]+last_field[1]]
            for key,value in self.__data.items():
                value[2] = \
                        temp[value[0]:value[0]+value[1]]
            return True
        except:
            return False

    def print(self,endian='little'):
        print("{0:>16} | {1:>6} | {2:>24}".format("Field","Size","Value"))
        print("-"*52)
        try:
            for key,value in self.__data.items():
                if(type(value[2])==bytes):
                    print("{0:>16} | {1:>6} | {2:>24}".format(key,value[1],hex(self.__byte2int(value[2],endian))))
                else:
                    print("{0:>16} | {1:>6} | {2:>24}".format(key,value[1],hex(value[2])))
        except:
            pass

    @staticmethod
    def sprint(structure,endian='little'):
        print("{0:>16} | {1:>6} | {2:>24}".format("Field","Size","Value"))
        print("-"*52)
        try:
            if(type(value[2])==bytes):
                print("{0:>16} | {1:>6} | {2:>24}".format(key,value[1],hex(self.__byte2int(value[2],endian))))
            else:
                print("{0:>16} | {1:>6} | {2:>24}".format(key,value[1],hex(value[2])))
        except:pass


class Union(object):
    def __init__(self):
        self.init()

    def __del__(self):
        pass

    def __repr__(self):
        return str(type(self).__name__)

    def __str__(self):
        return str(type(self).__name__)

    def init(self):
        self.__data = OrderedDict()
        self.__structure = dict()
        self.max    = 0

    def get(self,name):
        return self.__structure.get(name,None)

    def get_field(self,name,field):
        try:return self.__structure.get(name).get(field)[2]
        except:return None

    def size(self):
        return len(self.__data.get("data"))

    def set_size(self,size):
        self.__data = OrderedDict({"data":[0,size,None]})
        self.max    = size

    def __sizeof(self,structure):
        try:
            if(type(structure)==OrderedDict):
                o,s,_ = tuple(list(structure.items())[-1][1])
                return o+s
            elif(type(structure)==CStructure):
                o,s,_ = tuple(list(structure.data.items())[-1][1])
                return o+s
        except:return -1

    def __add(self,name,structure,flag='auto'):
        if(type(structure)==OrderedDict):
            self.__structure.update({name:structure})
        elif(type(structure)==CStructure):
            self.__structure.update({name:structure.data})
        else:
            return
        if(flag=='auto'):
            self.max = max(self.__sizeof(structure),self.max)
            self.__data.update({"data":[0,self.max,None]})

    def add(self,name,structure=None,flag='auto'):
        if(type(name)==dict or type(name)==OrderedDict):
            for k,v in name.items():
                self.__add(k,v,flag)
        else:
            self.__add(name,structure,flag)

    def drop(self,name,mode=0):
        if(mode==0):
            return self.__structure.pop(name)
        else:
            for k in self.__structure.copy():
                if(self.__structure.get(k)==name):
                    return self.__structure.pop(name,None)
        return None

    @property
    def data(self):
        return self.__data.get("data")
    
    @data.setter
    def data(self,union):      
        if(len(self.__structure)==0):
            return False
        _temp = bytearray(union)
        
        if(len(_temp)<self.max):
            zpadd = bytearray(self.max-len(_temp))
            _temp+=zpadd
        try:
            for k,v in self.__structure.items():
                for key,value in v.items():
                    value[2] = bytes(_temp[value[0]:value[0]+value[1]])
            self.__data["data"] = union
            return True
        except:return False

class StructureReader(object):
    #!/Author : Gibartes
    Offset = 0
    Size   = 1
    Value  = 2

    BYTE   = 1
    WORD   = 2
    DWORD  = 4
    QWORD  = 8

    UINT8  = 1
    UINT16 = 2
    UINT32 = 4
    UINT64 = 8

    enable  = 1
    disable = 0

    def __init__(self):
        self.__current = None     # Current Structure
        self.__fd      = -1
        self.__sfd     = None
        self.__wfd     = None
        self.__bcusror = 0
        self.__flag    = True
        self.__size    = (0,0)

    def __del__(self):
        self.cleanup()

    def __enter__(self):
        return self

    def __exit__(self):
        self.cleanup()

    """ Static methods """
    @staticmethod
    def version():
        print("Structure Reader 1.0.0 - Created by Gibartes")
        return "1.0.0"

    @staticmethod
    def byte2int(data,order='little'):
        try:return int.from_bytes(data,byteorder=order)
        except:return _StructureReaderConstant.EINVAL_FILE

    @staticmethod
    def ascii2int(ascii,base=8):
        _str = ''
        for i in ascii:
            if(int(i)==0):
                break
            _str+=chr(i)
        return int(_str,base)

    @staticmethod
    def align(data,word):
        return 0 if ((data%word)==0) else (word-data%word)

    @staticmethod
    def sizeof(structure):
        try:
            o,s,_ = tuple(list(structure.items())[-1][1])
            return o+s
        except:return _StructureReaderConstant.EINVAL_FILE

    @staticmethod
    def read_value(structure,field):
        try:return structure.get(field)[2]
        except:return None

    @staticmethod
    def read_field_size(structure,field):
        try:return structure.get(field)[1]
        except:return None

    @staticmethod
    def read_field_offset(structure,field):
        try:return structure.get(field)[0]
        except:return None

    @staticmethod
    def generate(field,offset,size):
        if(len(field)!=len(offset) and len(field)!=len(size)):
            return _StructureReaderConstant.EINVAL_ATTRIBUTE
        if( type(field)  not in (list,tuple,set) or
            type(offset) not in (list,tuple,set) or
            type(size)   not in (list,tuple)):
            return _StructureReaderConstant.EINVAL_ATTRIBUTE
        value = [None]*len(field)
        return OrderedDict((z[0],list(z[1:])) for z in zip(field,offset,size,value))

    @staticmethod
    def sprint(structure,endian='little'):
        print("{0:>16} | {1:>6} | {2:>24}".format("Field","Size","Value"))
        print("-"*52)
        try:
            for key,value in structure.items():
                if(type(value[2])==bytes):
                    print("{0:>16} | {1:>6} | {2:>24}".format(key,value[1],hex(StructureReader.byte2int(value[2],endian))))
                else:print("{0:>16} | {1:>6} | {2:>24}".format(key,value[1],hex(value[2])))
        except:pass

    @staticmethod
    def parse_as_byte(structure,text,offset=0,order='big'):
        if(type(text) not in [bytes,bytearray]):
            return _StructureReaderConstant.EINVAL_TYPE
        struct = structure.copy()
        try:
            last_field = list(structure.items())[-1][1]
            temp       = text[offset: \
                              offset+last_field[0]+last_field[1]]
            for key,value in struct.items():
                value[2] = \
                        temp[value[0]:value[0]+value[1]]
            return struct
        except:
            return False

    @staticmethod
    def parse_as_int(structure,text,offset=0,order='big'):
        if(type(text) not in [bytes,bytearray]):
            return _StructureReaderConstant.EINVAL_TYPE
        struct = structure.copy()
        try:
            last_field = list(structure.items())[-1][1]
            temp       = text[offset: \
                              offset+last_field[0]+last_field[1]]
            for key,value in struct.items():
                value[2] = \
                        int.from_bytes(temp[value[0]:value[0]+value[1]], \
                                    byteorder=order)
            return struct
        except:
            return False

    @staticmethod
    def __parse_as_defined_byte(structure,text,offset=0,order='big'):
        if(type(text) not in [bytes,bytearray]):
            return _StructureReaderConstant.EINVAL_TYPE
        try:
            last_field = list(structure.items())[-1][1]
            temp       = text[offset: \
                              offset+last_field[0]+last_field[1]]
            for key,value in structure.items():
                value[2] = \
                        temp[value[0]:value[0]+value[1]]
            return structure
        except:
            return False

    @staticmethod
    def __parse_as_defined_int(structure,text,offset=0,order='big'):
        if(type(text) not in [bytes,bytearray]):
            return _StructureReaderConstant.EINVAL_TYPE
        try:
            last_field = list(structure.items())[-1][1]
            temp       = text[offset: \
                              offset+last_field[0]+last_field[1]]
            for key,value in structure.items():
                value[2] = \
                        int.from_bytes(temp[value[0]:value[0]+value[1]], \
                                    byteorder=order)
            return structure
        except:
            return False

    # pair = [header.MFTEntryHeader,cursor,flag]
    # StructureReader.parse(pair,buffer,cursor,'int')
    @staticmethod
    def parse(structure,text,offset=0,option='byte',order='big'):
        if(type(structure)!=list or len(structure)!=3):
            return _StructureReaderConstant.EINVAL_TYPE
        
        basket = structure[0]
        if(option=='byte'):
            StructureReader.__parse_as_defined_byte(structure[0],text,offset,order) 
        else:
            StructureReader.__parse_as_defined_int(structure[0],text,offset,order)
        if(structure[0] not in (False,_StructureReaderConstant.EINVAL_TYPE)):
            structure[1]+=structure[1]+StructureReader.sizeof(structure[0])
            structure[2]=True
        else:
            structure[0]=basket
            structure[2]=False
        return structure

    @staticmethod
    def take(structure,text,offset=0,option='byte',order='big'):
        if(option=='byte'):
            return StructureReader.parse_as_byte(structure,text,offset,order)
        elif(option=='int'):
            return StructureReader.parse_as_int(structure,text,offset,order)
        else:return None

    """ General type methods """


    def bomb(self):
        del self.__current
        self.__current = None

    def cleanup(self):
        if(self.__fd>0):
            try:os.close(self.__fd)
            except:pass
            self.__fd = 0
        if(self.__sfd!=None):
            try:self.__sfd.close()
            except:pass
            self.__sfd = None
        if(self.__wfd!=None):
            try:self.__wfd.close()
            except:pass
            self.__wfd = None         
        self.__bcusror = 0
        self.bomb()

    def rclose(self,mode):
        if(mode==0):
            if(self.__fd>0):
                try:os.close(self.__fd)
                except:pass
                self.__fd = 0
        elif(mode==2):
            if(self.__sfd!=None):
                try:self.__sfd.close()
                except:pass
                self.__sfd = None

    def print(self,endian='little'):
        print("{0:>16} | {1:>6} | {2:>24}".format("Field","Size","Value"))
        print("-"*52)
        try:
            for key,value in self.__current.items():
                if(type(value[2])==bytes):
                    print("{0:>16} | {1:>6} | {2:>24}".format(key,value[1],hex(StructureReader.byte2int(value[2],endian))))
                else:
                    print("{0:>16} | {1:>6} | {2:>24}".format(key,value[1],hex(value[2])))
        except:
            pass

    def structure(self):         # Get type of the current structure
        return type(self.__current)

    def get_size(self):
        o,s,_ = tuple(list(self.__current.items())[-1][1])
        return o+s

    def get_file_handle(self,path,base=0,mode=0):
        if(mode==0):
            try:
                self.__fd = os.open(path,os.O_RDONLY)
            except:
                return _StructureReaderConstant.EINVAL_FILE
            os.lseek(self.__fd,0,os.SEEK_SET)
            return _StructureReaderConstant.SUCCESS
        elif(mode==1):
            try:
                self.__sfd = open(path,'rb')
            except:
                return _StructureReaderConstant.EINVAL_FILE
            self.__sfd.seek(0,os.SEEK_SET)
            return _StructureReaderConstant.SUCCESS
        elif(mode==2):
            try:
                self.__wfd = open(path,'rb+')
            except:
                return _StructureReaderConstant.EINVAL_FILE
            self.__wfd.seek(0,os.SEEK_SET)
            return _StructureReaderConstant.SUCCESS            

    """ Regular """

    def read_as_byte(self,offset=0,mode=os.SEEK_CUR):
        if(mode==os.SEEK_SET):
            os.lseek(self.__fd,offset,os.SEEK_SET)
        try:
            last_field = list(self.__current.items())[-1][1]
            temp       = os.read(self.__fd,last_field[0]+last_field[1])
            for key,value in self.__current.items():
                value[2] = \
                        temp[value[0]:value[0]+value[1]]
            self.stream = temp
            self.__flag = True
            return True
        except:
            self.__flag = False
            return False

    def read_as_int(self,offset=0,mode=os.SEEK_CUR,order='big'):
        if(mode==os.SEEK_SET):
            os.lseek(self.__fd,offset,os.SEEK_SET)
        try:
            last_field = list(self.__current.items())[-1][1]
            temp       = os.read(self.__fd,last_field[0]+last_field[1])
            for key,value in self.__current.items():
                value[2] = \
                        int.from_bytes(temp[value[0]:value[0]+value[1]], \
                                    byteorder=order)
            self.stream = temp
            self.__flag = True
            return True
        except:
            self.__flag = False
            return False

    def read_raw(self,offset,size,mode=os.SEEK_CUR,order='big'):
        if(size<1 or self.__fd==None):
            return False
        if(mode==os.SEEK_SET):
            os.lseek(self.__fd,offset,os.SEEK_SET)
        try:
            buffer = os.read(self.__fd,size)
            self.__flag = True if len(buffer)!=0 else False
            return buffer
        except:
            self.__flag = False
            return False

    def tell(self):
        return os.lseek(self.__fd,0x0,os.SEEK_CUR)

    def goto(self,offset=0,whence=os.SEEK_CUR):
        return os.lseek(self.__fd,offset,whence)

    @property
    def flag(self):
        return self.__flag

    """ Binary """

    def bread_as_byte(self,offset=0,mode=os.SEEK_CUR):
        if(mode==os.SEEK_SET):
            self.__sfd.seek(offset,os.SEEK_SET)
        try:
            last_field = list(self.__current.items())[-1][1]
            temp       = self.__sfd.read(last_field[0]+last_field[1])
            for key,value in self.__current.items():
                value[2] = \
                        temp[value[0]:value[0]+value[1]]
            self.stream = temp
            self.__flag = True
            return True
        except:
            self.__flag = False
            return False

    def bread_as_int(self,offset=0,mode=os.SEEK_CUR,order='big'):
        if(mode==os.SEEK_SET):
            self.__sfd.seek(offset,os.SEEK_SET)
        try:
            last_field = list(self.__current.items())[-1][1]
            temp       = self.__sfd.read(last_field[0]+last_field[1])
            for key,value in self.__current.items():
                value[2] = \
                        int.from_bytes(temp[value[0]:value[0]+value[1]], \
                                    byteorder=order)
            self.stream = temp
            self.__flag = True
            return True
        except:
            self.__flag = False
            return False

    def bread_raw(self,offset,size,mode=os.SEEK_CUR,order='big'):
        if(size<1 or self.__sfd==None):
            return False
        if(mode==os.SEEK_SET):
            self.__sfd.seek(offset,os.SEEK_SET)
        try:
            buffer = self.__sfd.read(size)
            self.__flag = True if len(buffer)!=0 else False
            return buffer
        except:
            self.__flag = False
            return False

    def btell(self):
        return self.__sfd.seek(0x00,os.SEEK_CUR)

    def bgoto(self,offset=0,whence=os.SEEK_CUR):
        return self.__sfd.seek(offset,whence)


    def set(self,structure):
        self.__current = structure

    def get(self):
        return self.__current

    def get_value(self,field):
        try:return self.__current.get(field)[2]
        except:return None

    def get_field_size(self,field):
        try:return self.__current.get(field)[1]
        except:return None

    def get_field_offset(self,field):
        try:return self.__current.get(field)[0]
        except:return None

    def copy(self):
        return self.__current.copy()

    # Data from the current opened file
    def execute(self,structure,option='byte',offset=0,mode=os.SEEK_SET,order='big',dup=_StructureReaderConstant.disable):
        self.set(structure)
        if(option=='byte'):
            self.read_as_byte(offset,mode)
        elif(option=='int'):
            self.read_as_int(offset,mode,order)
        else:return None
        if(dup==_StructureReaderConstant.disable):
            return self.get()
        return self.copy()

    def bexecute(self,structure,option='byte',offset=0,mode=os.SEEK_SET,order='big',dup=_StructureReaderConstant.disable):
        self.set(structure)
        if(option=='byte'):
            self.bread_as_byte(offset,mode)
        elif(option=='int'):
            self.bread_as_int(offset,mode,order)
        else:return None
        if(dup==_StructureReaderConstant.disable):
            return self.get()
        return self.copy()

    # Read data from files or byte streams
    def read(self,structure,option='byte',offset=0,mode=os.SEEK_SET,order='big',dup=_StructureReaderConstant.disable):
        if(self.__fd>0):
            return self.execute(structure,option,offset,mode,order,dup)
        elif(self.__sfd!=None):
            return self.bexecute(structure,option,offset,mode,order,dup)
        return False

    @property
    def size(self):
        return self.__size
    
    def fsize(self):
        size = [0,0]
        if(self.__fd>0):
            current = self.__fd.seek(0,os.SEEK_CUR)
            self.goto(0,os.SEEK_END)
            size[0]=self.tell()
            self.goto(current,os.SEEK_SET)
        if(self.__sfd!=None):
            current = self.__sfd.seek(0,os.SEEK_CUR)
            self.bgoto(0,os.SEEK_END)
            size[1]=self.btell()
            self.bgoto(current,os.SEEK_SET)
        self.__size = tuple(size)

    # Write a structure on the specific file.
    @staticmethod
    def __determine(size):
        if(size==0x01):
            return 'B'
        if(size==0x02):
            return 'H'
        if(size==0x04):
            return 'L'
        if(size==0x08):
            return 'Q'
        return 'x'

    def wclose(self):
        try:self.__wfd.close()
        except:pass

    def wflash(self):
        try:self.__wfd.flush()
        except:pass

    def wgoto(self,offset,whence=os.SEEK_CUR):
        self.__wfd.seek(offset,whence)

    def wset(self,field,data):
        size = self.__current.get(field,None)
        if(size==None):
            return False
        if(type(data)==bytes):
            if(len(data)<=size[1]):
                size[2]=data
            self.__current.update({field:size})
            return True
        return False

    def write(self,offset,whence=os.SEEK_CUR,option='byte',order='little'):
        if(self.__wfd==None):
            return False
        self.__wfd.seek(offset,whence)
        if(option=='byte'):
            for i in self.__current.keys():
                try:self.__wfd.write(self.__current.get(i)[2])
                except:return False
        else:
            for i in self.__current.keys():
                inx = self.__current.get(i)
                try:
                    if(order=='little'):
                        self.__wfd.write(struct.pack('<{0}'.format(self.__determine(inx[1])),inx[2]))
                    else:
                        self.__wfd.write(struct.pack('>{0}'.format(self.__determine(inx[1])),inx[2]))
                except:return False
        return True

    @staticmethod
    def s_wset(structure,field,data):
        size = structure.get(field,None)
        if(size==None):
            return False
        if(type(data)==bytes):
            if(len(data)<=size[1]):
                size[2]=data
            structure.update({field:size})
            return True
        return False

    @staticmethod
    def s_wbin(structure,option='byte',order='little'):
        bin = b''
        if(option=='byte'):
            for i in structure.keys():
                try:bin+=structure.get(i)[2]
                except:return False
        else:
            for i in structure.keys():
                inx = structure.get(i)
                try:
                    if(order=='little'):
                        bin+=struct.pack('<{0}'.format(self.__determine(inx[1])),inx[2])
                    else:
                        bin+=struct.pack('>{0}'.format(self.__determine(inx[1])),inx[2])
                except:return False
        return bin

class LoadInt(object):
    @classmethod
    def dos_time(stamp):
        sec, stamp = stamp & 0x1F, stamp >> 5
        mn,  stamp = stamp & 0x3F, stamp >> 6
        hr,  stamp = stamp & 0x1F, stamp >> 5
        day, stamp = stamp & 0x1F, stamp >> 5
        mon, stamp = stamp & 0x0F, stamp >> 4
        yr = (stamp & 0x7F) + 1980
        return (yr,mon,day,hr,mn,sec * 2)
    @classmethod
    def vint(buf,pos):
        """Load variable-size int."""
        limit = min(pos+11,len(buf))
        res = ofs = 0
        while pos<limit:
            b = int(buf[pos])
            res += ((b&0x7F)<<ofs)
            pos += 1
            ofs += 7
            if b < 0x80:
                return res,pos
        return (0,-1)
    @classmethod
    def byte(buf,pos):
        end = pos + 1
        if(end>len(buf)):
            return (0,-1)
        return Struct('<B').unpack_from(buf,pos)[0],end
    @classmethod
    def le32(buf,pos):
        end = pos + 4
        if(end>len(buf)):
            return (0,-1)
        return Struct('<L').unpack_from(buf,pos)[0],pos+4
    @classmethod
    def be32(buf,pos):
        end = pos + 4
        if(end>len(buf)):
            return (0,-1)
        return Struct('>L').unpack_from(buf,pos)[0],pos+4
    @classmethod
    def bytes(buf,num,pos):
        end = pos+num
        if(end>len(buf)):
            return (0,-1)
        return buf[pos:end],end
    @classmethod
    def vstr(buf,pos):
        slen,pos = load_vint(buf,pos)
        return load_bytes(buf,slen,pos)
    @classmethod
    def dostime(buf,pos):
        stamp, pos = LoadInt.le32(buf,pos)
        tup = LoadInt.parse_dos_time(stamp)
        return to_datetime(tup),pos
    @classmethod
    def unixtime(buf,pos,utc=0):
        secs,pos = LoadInt.le32(buf,pos)
        dt = datetime.fromtimestamp(secs,utc)
        return dt,pos
    @classmethod
    def windowstime(buf,pos,utc=0):
        # unix epoch (1970) in seconds from windows epoch (1601)
        unix_epoch = 11644473600
        val1,pos = LoadInt.le32(buf,pos)
        val2,pos = LoadInt.le32(buf,pos)
        secs,n1secs = divmod((val2<<32)|val1,10000000)
        dt = datetime.fromtimestamp(secs-unix_epoch,utc)
        dt = dt.replace(microsecond=n1secs//10)
        return dt, pos
