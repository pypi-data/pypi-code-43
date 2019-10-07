#
# Some of the code in this file was derived from the Python package 
# pfile-tools project, https://github.com/njvack/pfile-tools
# and as such we have included their BSD statement in this file.
#
# Copyright (c) 2012, Board of Regents of the University of Wisconsin
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this list
#   of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
# * Neither the name of the University of Wisconsin nor the names of its 
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Python modules
from __future__ import division

import sys
import csv
import ctypes


# Our Modules
import vespa.common.ge_util as utilge
import vespa.common.ge_pfile_mapper as pfile_mapper

from ctypes import *
from collections import namedtuple

StructInfo = namedtuple("StructInfo", ["label", "depth", "value", "field_type", "size", "offset"])



class UnknownPfile(RuntimeError):
    pass


class RevisionNumLittle(LittleEndianStructure):

    @property
    def major(self):
        return int(self.revision)

    _pack_   = 1
    _fields_ = [ ('revision', c_float) ]

class RevisionNumBig(BigEndianStructure):

    @property
    def major(self):
        return int(self.revision)

    _pack_   = 1
    _fields_ = [ ('revision', c_float) ]



class Pfile(object):
    """
    This class was based on the style of code from the pfile-tools 
    package written by Nathan Vack in that we use ctypes to organize 
    the reading of binary structures into a Python readable class
    instance. We have also incorporated code from their struct
    utilities modules as part of our class in order to dump out the
    header information to the stdout or as a list of strings.

    We use a subset of header variables that are sufficient to read the
    data from P-files in which we are interested. The structure for these
    variables was adapted from similar code found in the UCSF Sivic project.
    

    """
    def __init__(self, fname):
    
        self.file_name  = fname
        self.version    = 0
        self.hdr        = None
        self.map        = None
        self.endian     = 'little'  # def for version >= 11
        
        self.read_header()
        
        if not self.is_ge_file:
            raise UnknownPfile("Not a known GE Pfile - fname = %s" % fname)
        
        self.map_data()
        
    # Properties --------------------------------------------------

    @property
    def is_ge_file(self):
        if self.version < 12:
            if "GE" in self.hdr.rhr_rh_logo:
                return True
            else:
                return False
        else:
            offset = self.hdr.rhr_rdb_hdr_off_data
            if ( offset == 61464  or        # bjs from matlap script for ver = 9 
                 offset == 66072  or 
                 offset == 145908 or 
                 offset == 149788 or
                 offset == 150336 or
                 offset == 157276 or        # v24 empirical
                 offset == 213684 ):        # v26 empirical
                return True
            else:
                return False


    @property
    def is_svs(self):
        
        if self.map is None: 
            return False
        else:
            return self.map.is_svs     


    @property
    def get_mapper(self):
        
        if self.hdr is None: 
            return None
            
        psd = self.hdr.rhi_psdname.lower()
        
        if psd == 'probe-p':
            mapper = pfile_mapper.PfileMapper
        elif psd == 'oslaser':
            mapper = pfile_mapper.PfileMapperSlaser
        elif psd == 'presscsi':
            mapper = pfile_mapper.PfileMapper
        elif psd == 'fidcsi':
            # bjs - added for Pom's fidcsi 13C data
            mapper = pfile_mapper.PfileMapper
        elif psd == 'ia/stable/fidcsi':
            # bjs - added for Kearny's 13C data
            mapper = pfile_mapper.PfileMapper
        elif psd == 'presscsi_nfl':
            # bjs - added for Govind's SVS data off v25
            mapper = pfile_mapper.PfileMapper
        elif psd == 'epsi_3d_24':
            # bjs - added for soher check of MIDAS Browndyke data
            mapper = pfile_mapper.PfileMapper
        else:
            raise UnknownPfile("No Pfile mapper for pulse sequence = %s" % psd)
        
        return mapper


        
    def read_header(self):

        filelike = open(self.file_name, 'rb')

        # determine version number of this header from revision of rdbm.h
        version = self._major_version(filelike)
        if version == 0:
            raise UnknownPfile("Pfile not supported for version %s" % version)    
  
        # Here we dynamically configure the ctypes structures into which the
        # binary file will be read, based on the revision number
        #
        # Note. Determined empirically that I cannot declare the XxxHeader
        # class at the top level of the module with an attribute ._fields_ = [] 
        # and then append into it. I have to create a list and then assign 
        # _fields_ attribute to that list in one step.  Don't know why.
        #
        # Note 2. Had to move Class definition into this function so that the
        # class can be reconstituted more than once for multiple GE file reads.
        # At the top level of the module, the _fields_ attribute could be 
        # created once dynamically, but afterwards would stick around and
        # could not then be changed. 
        
        if version < 11:  # data taken on SGI - big endian
            class PfileHeaderBig(BigEndianStructure):
                """
                Contains the ctypes Structure for a GE P-file rdb header.
                Dynamically allocate the ctypes _fields_ list later depending on revision
                """
                _pack_   = 1            
                _fields_ = utilge.get_pfile_hdr_fields(version)
            hdr = PfileHeaderBig()
            self.endian = 'big'
        else:
            class PfileHeaderLittle(LittleEndianStructure):
                """
                Contains the ctypes Structure for a GE P-file rdb header.
                Dynamically allocate the ctypes _fields_ list later depending on revision
                """
                _pack_   = 1
                _fields_ = utilge.get_pfile_hdr_fields(version)
            hdr = PfileHeaderLittle()
            self.endian = 'little'
  
        try:
            # read  header information from start of file
            filelike.seek(0)
            filelike.readinto(hdr)
            filelike.close()
        except:
            filelike.close()
            raise UnknownPfile("Trouble reading file into header structure for version %s" % version)
        
        self.version = version
        self.hdr = hdr


    def map_data(self):
        """
        Select appropriate mapper class using the pulse sequence name string,
        instantiate and read the data from the file into the 'map' attribute
        
        """
        mapper = self.get_mapper
        self.map = mapper(self.file_name, self.hdr, self.version, self.endian)
        self.map.read_data()
        
        

    def _major_version(self, filelike):
        """
        Get the rdbm.h revision number from first 4 bytes. Then map the rdbm 
        revision to a platform number (e.g. 11.x, 12.x, etc.)
        
        """
        rev_little = RevisionNumLittle()
        rev_big    = RevisionNumBig()
        filelike.seek(0)
        filelike.readinto(rev_little)
        filelike.seek(0)
        filelike.readinto(rev_big)
        
        rev_little = rev_little.major
        rev_big    = rev_big.major
        
        version = 0

        if (rev_little > 6.95 and rev_little < 8.0) or (rev_big > 6.95 and rev_big < 8.0):
            version = 9.0; 
        elif ( rev_little == 9.0  or rev_big == 9.0  ): 
            version = 11.0;
        elif ( rev_little == 11.0 or rev_big == 11.0 ): 
            version = 12.0;
        elif ( rev_little == 14 or rev_big == 14 ): 
            version = 14.0;
        elif ( rev_little == 15 or rev_big == 15 ): 
            version = 15.0;
        elif ( rev_little == 16 or rev_big == 16 ): 
            version = 16.0;
        elif ( rev_little == 20 or rev_big == 20 ): 
            version = 20.0;
        elif ( rev_little == 21 or rev_big == 21 ): 
            version = 21.0;
        elif ( rev_little == 23 or rev_big == 23 ): 
            version = 21.0;
        elif ( rev_little == 24 or rev_big == 24 ): 
            version = 24.0;
        elif ( rev_little == 26 or rev_big == 26 ): 
            version = 26.0;
        else:
            raise UnknownPfile("Unknown header structure for revision %s" % rev_little)

        return version; 


    def dump_header_strarr(self):

        dumped = self._dump_struct(self.hdr)
        strarr = []
        for info in dumped:
            if (info.label.find("pad") == 0):
                continue
            # needed this because Gregor's UID values had some odd chars which
            # caused errors on the import of Probep data 
            try:
                val = info.value
                # needed this because Pom's UID values were causing errors
                # when VIFF was read back in
                if info.label == 'rhe_study_uid':    val = ' '
                if info.label == 'rhs_series_uid':   val = ' '
                if info.label == 'rhs_landmark_uid': val = ' '
                if info.label == 'rhi_image_uid':    val = ' '
                val = unicode(val)
            except:
                val = ' '
            strarr.append(unicode(info.label)+'        '+val)
            
        return strarr
        

    def dump_header(self):

        dumped = self._dump_struct(self.hdr)
        writer = csv.writer(sys.stdout, delimiter="\t")
        writer.writerow(["\n\nHeader All  -  field", "value"])
        for info in dumped:
            if (info.label.find("pad") == 0):
                continue
            writer.writerow([info.label, unicode(info.value)])


    def _dump_struct(self, struct, include_structs=False):
        """
        Recursively travels through a ctypes.Structure and returns a list of
        namedtuples, containing label, depth, value, size, and offset.
        If include_structs is true, output will include lines for individual
        structures and their sizes and offsets -- not just non-structure fields.
        """
        output = []
        self._dump_struct_rec(struct, output, include_structs)
        return output
    
    
    def _dump_struct_rec(self, struct, output, include_structs=False, prefix='', depth=0, base_offset=0):
        """
        Internal recursive method for dumping structures.
        Appends to the "output" parameter.
        
        """
        struct_class = type(struct)
        if include_structs:
            output.append(StructInfo(
                "%s (%s)" % (prefix, struct_class.__name__),
                depth, '', unicode(struct_class), ctypes.sizeof(struct_class), base_offset))
        for f in struct._fields_:
            name = f[0]
            field_type = f[1]
            field_meta = getattr(struct_class, name)
            field = getattr(struct, name)
            cur_prefix = "%s%s." % (prefix, name)
            field_offset = base_offset + field_meta.offset
            if isinstance(field, ctypes.Structure):
                self._dump_struct_rec(field, output, include_structs, cur_prefix,depth+1, field_offset)
            else:
                label = prefix+name
                output.append(StructInfo(label, depth, field, field_type.__name__, field_meta.size, field_offset))
    


#----------------------------------------------------------
# Test routines
#----------------------------------------------------------



def main():

    # v16 data - 1 chan
    fname = 'C:\\Users\\bsoher\\code\\repository_svn\\sample_data\\example_ge_svs_1ch_pom\\P29184.7'
    
    # v11 data - 8 chan
#    fname = 'C:\\Users\\bsoher\\code\\repository_svn\\sample_data\\example_ge_pom_multi-channel\\P01024.7'

    # v20 data - 32 chan
#    fname = 'C:\\Users\\bsoher\\code\\repository_svn\\sample_data\\example_ge_svs_32ch_gregor\\P32256.7'

    hdr = Pfile(fname)
    hdr.dump_header()

    bob = 10
    bob += 1




if __name__ == '__main__':

    main()

