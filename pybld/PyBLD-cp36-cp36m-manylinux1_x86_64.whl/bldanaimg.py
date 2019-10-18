#Analyze image Class for BLD
# Copyright (C) 2000-2018 Hiroshi Watabe watabe@cyric.tohoku.ac.jp
#$Id: bldanaimg.py,v 31447644c79c 2019/07/17 23:43:07 watabe $
import numpy
from pybld import numpyio
from pybld import bldanaimgc
import os
import sys
import signal
import tempfile
from pybld import qconv
import re
import string
try:
        import matplotlib.pyplot as plt
except ImportError:
        pass

# global variables:
OPEN_MAX = 64 # copied from C header file sys/syslimits.h ###
TYPE_IMG_B =2
TYPE_IMG_S = 4
TYPE_IMG_I = 8
TYPE_IMG_F = 16
TYPE_IMG_D = 64
TYPE_IMG_C = 32 #complex
TYPE_IMG_RGB = 128 #rgb

def header_name(fname):
    """get file name for header"""
    #check fname has .img or .hdr
    if re.search(r'.*(\.hdr$)', fname):
        return fname
    elif re.search(r'.*(\.img$)', fname):
        i = fname.rindex(".")
        return fname[0:i] + ".hdr"
    else:
        return fname + ".hdr"
    
def image_name(fname):
    """get file name for image"""
    #check fname has .img or .hdr
    if re.search(r'.*(\.img$)', fname):
        return fname
    elif re.search(r'.*(\.hdr$)', fname):
        i = fname.rindex(".")
        return fname[0:i] + ".img"
    else:
        return fname + ".img"
    
def frame_size(hdr):
    """get frame size from header"""
    if hdr.dim[4]>1: #4 dimension
        fr_size = int((float(hdr.dim[1])*hdr.dim[2]*hdr.bitpix + 7)/8) * hdr.dim[3]*hdr.dim[4]
        return(fr_size)
    else:
        fr_size = int((float(hdr.dim[1])*hdr.dim[2]*hdr.bitpix + 7)/8) * hdr.dim[3]
        return(fr_size)

def match_hdr(img):
    """do match type and match size"""
    match_size(img)
    match_type(img)
def match_size(img):
    """matching size image and header type"""
    s = img.img.shape
    j = len(s)
    for i in range(len(s)):
        j = j - 1
        img.hdr.dim[i + 1] =s[j]
    if len(s)==3 and img.hdr.dim[4]!=1:#tdim is not reset
        img.hdr.dim[4] = 1
    img.tdim = img.hdr.dim[4]
    img.zdim = img.hdr.dim[3]
    img.ydim = img.hdr.dim[2]
    img.xdim = img.hdr.dim[1]
    img.pxdim = img.hdr.pixdim[1]
    img.pydim = img.hdr.pixdim[2]
    img.pzdim = img.hdr.pixdim[3]
    img.ptdim = img.hdr.pixdim[4]

def match_type(img):
    """matching between image type and header type"""
    if img.img.dtype == numpy.byte: #unsigned char
        img.hdr.datatype = TYPE_IMG_B
        img.hdr.bitpix = 8
    if img.img.dtype == numpy.short: #short
        img.hdr.datatype = TYPE_IMG_S
        img.hdr.bitpix = 16
    if img.img.dtype == numpy.int: #int
        img.hdr.datatype = TYPE_IMG_I
        img.hdr.bitpix = 32
    if img.img.dtype == numpy.float32: #float
        img.hdr.datatype = TYPE_IMG_F
        img.hdr.bitpix = 32
    if img.img.dtype == numpy.double: #double
        img.hdr.datatype = TYPE_IMG_D
        img.hdr.bitpix = 64
    if img.img.dtype == numpy.complex: #complex
        img.hdr.datatype = TYPE_IMG_C
        img.hdr.bitpix = 64
    
class GpetviewProcess:
    def __init__(self,zoom=1,width=750,height=550,color=0,seq='',title='',number=1,timestamp=12345,amax=0):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        (fd_r, fd_w) = os.pipe()
        os.set_inheritable(fd_w,True)
        os.set_inheritable(fd_r,True)
        self.pid = os.fork()
        if self.pid == 0:
            try:
                for i in range(OPEN_MAX):
                    # close everything except stdin, stdout, stderr
                    # and the read part of the pipe
                    if i not in (fd_r,0,1,2):
                        try:
                            os.close(i)
                        except OSError:
                            pass
                if amax>0:
                    try:
                        os.execvp('gpetview', ('gpetview','-a','%g 0' % (amax),'-z','%g' % zoom,'-w','%d' % width,'%d' % height,'-l','%d' % color,'-q','%s' % seq,'-b','%s' % title,'-t','%s' % timestamp,'-n','%d' % number,'-p',repr(fd_r)))
                    except:
                        # we have to be careful in the child process.  We
                        # don't want to throw an exception because that would
                        # allow two threads to continue running.
                        sys.stderr.write('GpetviewProcess: Could not start gpetview\n')
                        os._exit(1) # exit this forked process but not the parent
                else:
                    try:
                        os.execvp('gpetview', ('gpetview','-z','%g' % zoom,'-w','%d' % width,'%d' % height,'-l','%d' % color,'-q','%s' % seq,'-b','%s' % title,'-t','%s' % timestamp,'-n','%d' % number,'-p',repr(fd_r)))
                    except:
                        # we have to be careful in the child process.  We
                        # don't want to throw an exception because that would
                        # allow two threads to continue running.
                        sys.stderr.write('GpetviewProcess: Could not start gpetview\n')
                        os._exit(1) # exit this forked process but not the parent
            except:
                sys.stderr.write('Unexpected exception in child!\n')
                os._exit(2) # exit child but not parent

        # We are the parent -> keep only the writeable side of the pipe
        os.close(fd_r)
        self.pipe = os.fdopen(fd_w, 'wb',-1)
    def __call__(self,img):
        img.hdr.fd_write(self.pipe)
        self.pipe.flush()
        nfr = frame_size(img.hdr)
        if img.hdr.datatype == TYPE_IMG_B: #unsigned char
            numpyio.fwrite(self.pipe,nfr,img.img,'uint8',img.hdr.swap)
        if img.hdr.datatype == TYPE_IMG_S: #signed short
            numpyio.fwrite(self.pipe,nfr/2,img.img,'s',img.hdr.swap)
        if img.hdr.datatype == TYPE_IMG_I: #signed int
            numpyio.fwrite(self.pipe,nfr/4,img.img,'i',img.hdr.swap)
        if img.hdr.datatype == TYPE_IMG_F: #float
            if img.hdr.swap==1:
                a = img.img.copy()
                a = numpyio.bswap(a)
                numpyio.fwrite(self.pipe,nfr/4,a,'f',0)
            else:
                numpyio.fwrite(self.pipe,nfr/4,img.img,'f',0)
                
        if img.hdr.datatype == TYPE_IMG_D: #double
            if img.hdr.swap==1:
                a = img.img.copy()
                a = numpyio.bswap(a)
                numpyio.fwrite(self.pipe,nfr/8,a,'d',0)
            else:
                numpyio.fwrite(self.pipe,nfr/8,img.img,'d',0)
        self.pipe.flush()

                
class HDR:
    def __init__(self,xdim=0,ydim=0,zdim=0,px=0.0,py=0.0,pz=0.0,tdim=1,datatype=TYPE_IMG_B,bitpix=8):
        self.size_of_hdr = 348
        self.data_type = "\0\0\0\0\0\0\0\0\0\0"
        self.db_name = "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
        self.extents = 0
        self.session_error = 0
        self.regular = 'r'
        self.hkey_un0 = "\0"
        self.dim = numpy.zeros(8,dtype=numpy.short)
        self.dim[0] = 1
        self.dim[1] = xdim
        self.dim[2] = ydim
        self.dim[3] = zdim
        self.dim[4] = tdim
        self.vox_units = "\0\0\0\0"
        self.cal_units = "\0\0\0\0\0\0\0\0"
        self.unused1 = 0
        self.datatype = datatype
        self.bitpix = bitpix
        self.dim_un0 = 0
        self.pixdim = numpy.zeros(8,dtype=numpy.float)
        self.pixdim[1] = px
        self.pixdim[2] = py
        self.pixdim[3] = pz
        self.vox_offset = 0.0
        self.funused1 = 0.0
        self.funused2 = 0.0
        self.funused3 = 0.0
        self.cal_max = 0.0
        self.cal_min = 0.0
        self.compressed = 0
        self.verified = 0
        self.glmax = 0
        self.glmin = 0
        self.descrip = "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
        self.aux_file = "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
        self.orient = "\0"
        self.origin = numpy.zeros(5,dtype=numpy.short) #SPM redefine originator as short[5]
        self.generated = "\0\0\0\0\0\0\0\0\0\0"
        self.scannum = "\0\0\0\0\0\0\0\0\0\0"
        self.patient_id = "\0\0\0\0\0\0\0\0\0\0"
        self.exp_date = "\0\0\0\0\0\0\0\0\0\0"
        self.exp_time = "\0\0\0\0\0\0\0\0\0\0"
        self.hist_un0 = "\0\0\0"
        self.views = 0
        self.vols_added = 0
        self.start_field = 0
        self.field_skip = 0
        self.omax = 0
        self.omin = 0
        self.smax = 0
        self.smin = 0
        self.swap = 0 #need swap or not

    def read(self,fname):
        """ read header structure from a file"""
        fname = header_name(fname)
        try:
            fd = open(fname,'rb')
        except IOError:
            raise IOError("Could not open %s" % str(fname))
            return
        fd.seek(0,2)
        fsize = fd.tell()
        if fsize != self.size_of_hdr: #failed to open header
            fd.close()
            return 0
        fd.seek(0)
        self.size_of_hdr = numpyio.fread(fd,1,'i')[0]
        if self.size_of_hdr != fsize: #need swap
            self.swap = 1
            self.size_of_hdr = 348
        self.data_type = numpyio.fread(fd,10,'c',self.swap)
        self.data_type = str(self.data_type.tostring(),'utf8')
        self.db_name = numpyio.fread(fd,18,'c',self.swap)
        self.db_name = str(self.db_name.tostring(),'utf8')
        self.extents = numpyio.fread(fd,1,'i',self.swap)[0]
        self.session_error = numpyio.fread(fd,1,'int16',self.swap)[0]
        self.regular = numpyio.fread(fd,1,'b',self.swap)[0]
        self.hkey_un0 = numpyio.fread(fd,1,'c',self.swap)[0]
        if len(self.hkey_un0)==0:
            self.hkey_un0 = '\0'
        self.dim = numpyio.fread(fd,8,'int16',self.swap)
        self.vox_units = numpyio.fread(fd,4,'c',self.swap)
        self.vox_units = str(self.vox_units.tostring(),'utf8')
        self.cal_units = numpyio.fread(fd,8,'c',self.swap)
        self.cal_units = str(self.cal_units.tostring(),'utf8')
        self.unused1 = numpyio.fread(fd,1,'int16',self.swap)[0]
        self.datatype =  numpyio.fread(fd,1,'int16',self.swap)[0]
        self.bitpix =  numpyio.fread(fd,1,'int16',self.swap)[0]
        self.dim_un0 =  numpyio.fread(fd,1,'int16',self.swap)[0]
        #debug watabe self.pixdim = numpyio.fread(fd,8,'f','f',self.swap)
        self.pixdim = numpyio.fread(fd,8,'f',0)
        if self.swap==1:
            self.pixdim = numpyio.bswap(self.pixdim)
        a = numpyio.fread(fd,1,'f',0)
        if self.swap==1:
            a = numpyio.bswap(a)
        self.vox_offset = a[0]
        a = numpyio.fread(fd,1,'f',0)
        if self.swap==1:
            a = numpyio.bswap(a)
        self.funused1 = a[0]
        a = numpyio.fread(fd,1,'f',0)
        if self.swap==1:
            a = numpyio.bswap(a)
        self.funused2 = a[0]
        a = numpyio.fread(fd,1,'f',0)
        if self.swap==1:
            a = numpyio.bswap(a)
        self.funused3 = a[0]
        a = numpyio.fread(fd,1,'f',0)
        if self.swap==1:
            a = numpyio.bswap(a)
        self.cal_max = a[0]
        a = numpyio.fread(fd,1,'f',0)
        if self.swap==1:
            a = numpyio.bswap(a)
        self.cal_min = a[0]
        self.compressed = numpyio.fread(fd,1,'i',self.swap)[0]
        self.verified = numpyio.fread(fd,1,'i',self.swap)[0]
        self.glmax = numpyio.fread(fd,1,'i',self.swap)[0]
        self.glmin = numpyio.fread(fd,1,'i',self.swap)[0]
        self.descrip = numpyio.fread(fd,80,'c',self.swap)
        self.descrip = str(self.descrip.tostring(),'utf8')
        self.aux_file = numpyio.fread(fd,24,'c',self.swap)
        self.aux_file = str(self.aux_file.tostring(),'utf8')
        self.orient =  numpyio.fread(fd,1,'c',self.swap)[0]
        if len(self.orient)==0:
            self.orient = '\0'
#        self.originator =  numpyio.fread(fd,10,'c','c',self.swap)
#        self.originator = self.originator.tostring()
        self.origin =  numpyio.fread(fd,5,'int16',self.swap)
        self.generated =  numpyio.fread(fd,10,'uint8',self.swap)
        self.generated = self.generated.tostring()
        self.scannum =  numpyio.fread(fd,10,'uint8',self.swap)
        self.scannum = self.scannum.tostring()
        self.patient_id =  numpyio.fread(fd,10,'c',self.swap)
        self.patient_id = self.patient_id.tostring()
        self.exp_date =  numpyio.fread(fd,10,'uint8',self.swap)
        self.exp_date = self.exp_date.tostring()
        self.exp_time =  numpyio.fread(fd,10,'uint8',self.swap)
        self.exp_time = self.exp_time.tostring()
        self.hist_un0 =  numpyio.fread(fd,3,'c',self.swap)
        self.hist_un0 = self.hist_un0.tostring()
        self.views = numpyio.fread(fd,1,'i',self.swap)[0]
        self.vols_added = numpyio.fread(fd,1,'i',self.swap)[0]
        self.start_field = numpyio.fread(fd,1,'i',self.swap)[0]
        self.field_skip = numpyio.fread(fd,1,'i',self.swap)[0]
        self.omax = numpyio.fread(fd,1,'i',self.swap)[0]
        self.omin = numpyio.fread(fd,1,'i',self.swap)[0]
        self.smax = numpyio.fread(fd,1,'i',self.swap)[0]
        self.smin = numpyio.fread(fd,1,'i',self.swap)[0]
        fd.close()
        return

    def write(self,fname):
        """ write header structure into a file"""
        fname = header_name(fname)
        fd = open(fname,'wb')
        self.fd_write(fd)
        fd.close()
        return

    def fd_write(self,fd):
        """write header into file descriptor fd"""
        numpyio.fwrite(fd,1,numpy.array(self.size_of_hdr,dtype='i'),'i',self.swap)
        fd.write(numpy.array(bytes(self.data_type,'utf8')).tobytes())
        fd.write(numpy.array(bytes(self.db_name,'utf8')).tobytes())
        numpyio.fwrite(fd,1,numpy.array(self.extents,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.session_error,dtype='int16'),'int16',self.swap)
        try:
                numpyio.fwrite(fd,1,numpy.array(self.regular,dtype='b'),'b',self.swap)
        except:
                numpyio.fwrite(fd,1,numpy.array(self.regular,dtype='c'),'c',self.swap)
                
        fd.write(numpy.array(bytes(self.hkey_un0,'utf8')).tobytes())
        numpyio.fwrite(fd,8,numpy.array(self.dim,dtype='int16'),'int16',self.swap)
        fd.write(numpy.array(bytes(self.vox_units,'utf8')).tobytes())
        fd.write(numpy.array(bytes(self.cal_units,'utf8')).tobytes())
        numpyio.fwrite(fd,1,numpy.array(self.unused1,dtype='int16'),'int16',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.datatype,dtype='int16'),'int16',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.bitpix,dtype='int16'),'int16',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.dim_un0,dtype='int16'),'int16',self.swap)
        if self.swap==1:
            a = numpy.array(self.pixdim[:],'f')
            a = numpyio.bswap(a)
            numpyio.fwrite(fd,8,numpy.array(a,dtype='f'),'f',0)
        else:
            numpyio.fwrite(fd,8,numpy.array(self.pixdim,dtype='f'),'f',0)
        if self.swap==1:
            a = numpy.array([self.vox_offset],'f')
            numpyio.fwrite(fd,1,a,'f',0)
        else:
            numpyio.fwrite(fd,1,numpy.array(self.vox_offset,dtype='f'),'f',0)
        if self.swap==1:
            a = numpy.array([self.funused1],'f')
            a = numpyio.bswap(a)
            numpyio.fwrite(fd,1,a,'f',0)
        else:
            numpyio.fwrite(fd,1,numpy.array(self.funused1,dtype='f'),'f',0)
        if self.swap==1:
            a = numpy.array([self.funused2],'f')
            a = numpyio.bswap(a)
            numpyio.fwrite(fd,1,a,'f',0)
        else:
            numpyio.fwrite(fd,1,numpy.array(self.funused2,dtype='f'),'f',0)
        if self.swap==1:
            a = numpy.array([self.funused3],'f')
            a = numpyio.bswap(a)
            numpyio.fwrite(fd,1,a,'f',0)
        else:
            numpyio.fwrite(fd,1,numpy.array(self.funused3,dtype='f'),'f',0)
        if self.swap==1:
            a = numpy.array([self.cal_max],'f')
            a = numpyio.bswap(a)
            numpyio.fwrite(fd,1,a,'f',0)
        else:
            numpyio.fwrite(fd,1,numpy.array(self.cal_max,dtype='f'),'f',0)
        if self.swap==1:
            a = numpy.array([self.cal_min],'f')
            a = numpyio.bswap(a)
            numpyio.fwrite(fd,1,a,'f',0)
        else:
            numpyio.fwrite(fd,1,numpy.array(self.cal_min,dtype='f'),'f',0)
        numpyio.fwrite(fd,1,numpy.array(self.compressed,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.verified,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.glmax,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.glmin,dtype='i'),'i',self.swap)

        fd.write(numpy.array(bytes(self.descrip,'utf8')).tobytes())
        fd.write(numpy.array(bytes(self.aux_file,'utf8')).tobytes())
        fd.write(numpy.array(bytes(self.orient,'utf8')).tobytes())
#        nnumpy.array(self.originator).tobytes())tofile(fd)
        numpyio.fwrite(fd,5,numpy.array(self.origin,dtype='int16'),'int16',self.swap)
        try:
                fd.write(numpy.array(bytes(self.generated,'utf8')).tobytes())
        except:
                fd.write(numpy.array(self.generated).tobytes())
        try:
                fd.write(numpy.array(bytes(self.scannum,'utf8')).tobytes())
        except:
                fd.write(numpy.array(self.scannum).tobytes())
        try:
                fd.write(numpy.array(bytes(self.patient_id,'utf8')).tobytes())
        except:
                fd.write(numpy.array((self.patient_id)).tobytes())
        try:
                fd.write(numpy.array(bytes(self.exp_date,'utf8')).tobytes())
        except:
                fd.write(numpy.array((self.exp_date)).tobytes())
        try:
                fd.write(numpy.array(bytes(self.exp_time,'utf8')).tobytes())
        except:
                fd.write(numpy.array((self.exp_time)).tobytes())
        try:
                fd.write(numpy.array(bytes(self.hist_un0,'utf8')).tobytes())
        except:
                fd.write(numpy.array((self.hist_un0)).tobytes())
        numpyio.fwrite(fd,1,numpy.array(self.views,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.vols_added,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.start_field,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.field_skip,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.omax,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.omin,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.smax,dtype='i'),'i',self.swap)
        numpyio.fwrite(fd,1,numpy.array(self.smin,dtype='i'),'i',self.swap)
        return
    
    def show(self):
        """show header"""
        print("size_of_hdr ",self.size_of_hdr)
        print("data_type ", self.data_type)
        print("db_name ", self.db_name)
        print("extents ", self.extents)
        print("session_error ", self.session_error)
        print("regular ", self.regular)
        print("hkey_un0 ", self.hkey_un0)
        print("dim ", self.dim)
        print("vox_units ", self.vox_units)
        print("cal_units ", self.cal_units)
        print("unused1 ", self.unused1)
        print("datatype ", self.datatype)
        print("bitpix ", self.bitpix)
        print("dim_un0 ", self.dim_un0)
        print("pixdim ", self.pixdim)
        print("vox_offset ", self.vox_offset)
        print("funused1 ", self.funused1)
        print("funused2 ", self.funused2)
        print("funused3 ", self.funused3)
        print("cal_max ", self.cal_max)
        print("cal_min ", self.cal_min)
        print("compressed ", self.compressed)
        print("verified ", self.verified)
        print("glmax ", self.glmax)
        print("glmin ", self.glmin)
        print("descrip ", self.descrip)
        print("aux_file ", self.aux_file)
        print("orient ", self.orient)
        print("origin ", self.origin)
#        print "originator ", self.originator
        print("generated ", self.generated)
        print("scannum ", self.scannum)
        print("patient_id ", self.patient_id)
        print("exp_date ", self.exp_date)
        print("exp_time ", self.exp_time)
        print("hist_un0 ", self.hist_un0)
        print("views ", self.views)
        print("vols_added ", self.vols_added)
        print("start_field ", self.start_field)
        print("field_skip ", self.field_skip)
        print("omax ", self.omax)
        print("omin ", self.omin)
        print("smax ", self.smax)
        print("smin ", self.smin)
        print("swap ", self.swap)
        return
    def __call__(self): #for copy header we will call this class
        hdr = HDR()
        hdr.size_of_hdr = self.size_of_hdr
        hdr.data_type = self.data_type
        hdr.db_name = self.db_name
        hdr.extents = self.extents
        hdr.session_error = self.session_error
        hdr.regular = self.regular
        hdr.hkey_un0 = self.hkey_un0
        hdr.dim = numpy.array(self.dim)
        hdr.dim[1] = self.dim[1]
        hdr.dim[2] = self.dim[2]
        hdr.dim[3] = self.dim[3]
        hdr.dim[4] = self.dim[4]
        hdr.vox_units = self.vox_units
        hdr.cal_units = self.cal_units
        hdr.unused1 = self.unused1
        hdr.datatype = self.datatype
        hdr.bitpix = self.bitpix
        hdr.dim_un0 = self.dim_un0
        hdr.pixdim = numpy.array(self.pixdim)
        hdr.vox_offset = self.vox_offset
        hdr.funused1 = self.funused1
        hdr.funused2 = self.funused2
        hdr.funused3 = self.funused3
        hdr.cal_max = self.cal_max
        hdr.cal_min = self.cal_min
        hdr.compressed = self.compressed
        hdr.verified = self.verified
        hdr.glmax = self.glmax
        hdr.glmin = self.glmin
        hdr.descrip = self.descrip
        hdr.aux_file = self.aux_file
        hdr.orient = self.orient
#        hdr.originator = self.originator
        hdr.origin = self.origin
        hdr.generated = self.generated
        hdr.scannum = self.scannum
        hdr.patient_id = self.patient_id
        hdr.exp_date = self.exp_date
        hdr.exp_time = self.exp_time
        hdr.hist_un0 = self.hist_un0
        hdr.views = self.views
        hdr.vols_added = self.vols_added
        hdr.start_field = self.start_field
        hdr.field_skip = self.field_skip
        hdr.omax = self.omax
        hdr.omin = self.omin
        hdr.smax = self.smax
        hdr.smin = self.smin
        hdr.swap = self.swap
        return hdr

class ANAIMG:
    """ Class for manipulating Analyze image
        read() - Read Analyze image
        read_raw() - Read Raw image
        write() - Write Analyze image
        view() - view image by gpetview
        match_hdr() - match type and size of image in header
        match_type() - match type of image in header
        match_size() - match size of image in header
        max() - print max value of image
        min() - print min value of image
        scale() - scale image
        transform() - transform image using Affine matrix (4x4)
        zoom() - zooming image
        rotate_x() - rotate image along x axis
        rotate_y() - rotate image along y axis
        rotate_z() - rotate image along z axis
        hdr() - copy header
        show_hdr() - show header
        zeros() - prepare matrix according to header infomation

        TYPE_IMG_B =2
        TYPE_IMG_S = 4
        TYPE_IMG_I = 8
        TYPE_IMG_F = 16
        TYPE_IMG_C = 32
        TYPE_IMG_D = 64
        TYPE_IMG_RGB = 128
    """
    def __init__(self,xdim=0,ydim=0,zdim=0,tdim=1,px=0.0,py=0.0,pz=0.0,type=TYPE_IMG_B,view_cmd='matplot'):
        if type==TYPE_IMG_B:
            bitpix = 8
        if type==TYPE_IMG_S:
            bitpix = 16
        if type==TYPE_IMG_I:
            bitpix = 32
        if type==TYPE_IMG_F:
            bitpix = 32
        if type==TYPE_IMG_D:
            bitpix = 64
        if type==TYPE_IMG_C:
            bitpix = 64
        if type==TYPE_IMG_RGB:
            bitpix = 8
        self.hdr = HDR(xdim=xdim,ydim=ydim,zdim=zdim,tdim=tdim,px=px,py=py,pz=pz,datatype=type,bitpix=bitpix)
        self.img = None
        self.fname = None
        self.pid = None #for gpetview
        self.xdim = xdim
        self.ydim = ydim
        self.zdim = zdim
        self.tdim = tdim
        self.pxdim = px
        self.pydim = py
        self.pzdim = pz
        self.ptdim = 1
        self.view_cmd = view_cmd
        
    def read(self,fname):
        """ read image data from fname"""
        self.fname = fname
        ret = self.hdr.read(fname)
        if ret==0:
            print("Failed to open header file of %s" % (fname))
            return

        fname = image_name(fname)
        try:
            fd = open(fname,'rb')
        except IOError:
            raise IOError("Could not open %s" % fname)
            return
	#consider offset
        if self.hdr.vox_offset>0.0:
            fd.seek(int(self.hdr.vox_offset),0)
        self.img = self.read_raw(fd)
        fd.close()
        self.xdim = self.hdr.dim[1]
        self.ydim = self.hdr.dim[2]
        self.zdim = self.hdr.dim[3]
        self.tdim = self.hdr.dim[4]
        self.pxdim = self.hdr.pixdim[1]
        self.pydim = self.hdr.pixdim[2]
        self.pzdim = self.hdr.pixdim[3]
        self.ptdim = self.hdr.pixdim[4]

    def read_raw(self,fd):
        """read raw data from file description fd"""
        nfr = frame_size(self.hdr)
        if self.hdr.datatype == TYPE_IMG_B: #unsigned char
            self.img = numpyio.fread(fd,nfr,'uint8',self.hdr.swap)
        if self.hdr.datatype == TYPE_IMG_S: #signed short
            self.img = numpyio.fread(fd,nfr/2,'int16',self.hdr.swap)
        if self.hdr.datatype == TYPE_IMG_I: #signed int
            self.img = numpyio.fread(fd,nfr/4,'i',self.hdr.swap)
        if self.hdr.datatype == TYPE_IMG_RGB: #3 unsigned char
            self.img = numpyio.fread(fd,nfr,'uint8',self.hdr.swap)
        if self.hdr.datatype == TYPE_IMG_F: #float
            self.img = numpyio.fread(fd,nfr/4,'f',self.hdr.swap)
        if self.hdr.datatype == TYPE_IMG_D: #double
            self.img = numpyio.fread(fd,nfr/8,'d',self.hdr.swap)
        if self.hdr.datatype == TYPE_IMG_C: #complex
            self.img = numpyio.fread(fd,nfr/8,'F',self.hdr.swap)
        if self.hdr.dim[4]>1:#4 dimension
            ret = numpy.reshape(self.img,(self.hdr.dim[4],self.hdr.dim[3],self.hdr.dim[2],self.hdr.dim[1]))
            return ret
        else:
            ret = numpy.reshape(self.img,(self.hdr.dim[3],self.hdr.dim[2],self.hdr.dim[1]))
            return ret
        
    def write(self,fname,type=None,swap=None):
        """ write Analyze image into a file fname"""
        self.fname = fname
        if type is None:
            match_type(self)
            match_size(self)
        if swap!=None:
            self.hdr.swap = swap
        if type!=None:
            if type==TYPE_IMG_B:
                self.hdr.datatype = type;
                self.hdr.bitpix = 8
                #get rid of negative value
                self.img = (1 - numpy.less(self.img,0))*self.img
                #find max
                maxv = max(numpy.reshape(self.img,(frame_size(self.hdr),)))
                self.img = self.img*255.0/maxv; #normalized 
                self.img = self.img.astype('uint8')

            if type==TYPE_IMG_S:
                self.hdr.datatype = type;
                self.hdr.bitpix = 16
                self.img = self.img.astype('short')
                
            if type==TYPE_IMG_I:
                self.hdr.datatype = type;
                self.hdr.bitpix = 32
                self.img = self.img.astype('int32')
                
            if type==TYPE_IMG_F:
                self.hdr.datatype = type;
                self.hdr.bitpix = 32
                self.img = self.img.astype('float32')
                
            if type==TYPE_IMG_D:
                self.hdr.datatype = type;
                self.hdr.bitpix = 64
                self.img = self.img.astype('double')
            if type==TYPE_IMG_C:
                self.hdr.datatype = type;
                self.hdr.bitpix = 64
                self.img = self.img.astype('complex')
            if type==TYPE_IMG_RGB:
                self.hdr.datatype = type;
                self.hdr.bitpix = 8
                self.img = self.img.astype('uint8')
#
        self.hdr.write(fname)
        fname = image_name(fname)
        fd = open(fname,'wb')
	#consider offset
        if self.hdr.vox_offset>0.0:
            fd.seek(int(self.hdr.vox_offset),0)
        nfr = frame_size(self.hdr)
        if self.hdr.datatype == TYPE_IMG_B: #unsigned char
            numpyio.fwrite(fd,nfr,self.img,'uint8',0)
        if self.hdr.datatype == TYPE_IMG_RGB: #RGB
            numpyio.fwrite(fd,nfr,self.img,'uint8',0)
        if self.hdr.datatype == TYPE_IMG_S: #signed short
            numpyio.fwrite(fd,nfr/2,self.img,'int16',self.hdr.swap)
        if self.hdr.datatype == TYPE_IMG_I: #signed int
            numpyio.fwrite(fd,nfr/4,self.img,'i',self.hdr.swap)
        if self.hdr.datatype == TYPE_IMG_F: #float
            if self.hdr.swap==1:
                a = self.img.copy()
                a = numpyio.bswap(a)
                numpyio.fwrite(fd,nfr/4,a,'f',0)
            else:
                numpyio.fwrite(fd,nfr/4,self.img,'f',0)
        if self.hdr.datatype == TYPE_IMG_D: #double
            if self.hdr.swap==1:
                a = self.img.copy()
                a = numpyio.bswap(a)
                numpyio.fwrite(fd,nfr/8,a,'d',0)
            else:
                numpyio.fwrite(fd,nfr/8,self.img,'d',0)
        if self.hdr.datatype == TYPE_IMG_C: #complex
            if self.hdr.swap==1:
                a = self.img.copy()
                a = numpyio.bswap(a)
                numpyio.fwrite(fd,nfr/8,a,'F',0)
            else:
                numpyio.fwrite(fd,nfr/8,self.img,'F',0)
        fd.close()
        
            
    def change_type(self,type):
        """ change type of image """
        if type==TYPE_IMG_B:
            self.hdr.datatype = type;
            self.hdr.bitpix = 8

        if type==TYPE_IMG_RGB:
            self.hdr.datatype = type;
            self.hdr.bitpix = 8

        if type==TYPE_IMG_S:
            self.hdr.datatype = type;
            self.hdr.bitpix = 16
                
        if type==TYPE_IMG_I:
            self.hdr.datatype = type;
            self.hdr.bitpix = 32

        if type==TYPE_IMG_F:
            self.hdr.datatype = type;
            self.hdr.bitpix = 32
                
        if type==TYPE_IMG_D:
            self.hdr.datatype = type;
            self.hdr.bitpix = 64

        if type==TYPE_IMG_C:
            self.hdr.datatype = type;
            self.hdr.bitpix = 64

        return

    def view(self,zoom=1,width=750,height=550,color=0,timestamp='',seq='',title='',number=1,amax=0,slice_no=0):
        """view iamge. slice_no for showing slice (matplot)"""
        if self.view_cmd=='gpetview':
            self.gpetview(zoom=zoom,width=width,height=height,color=color,timestamp=timestamp,seq=seq,title=title,number=number,amax=amax)
        if self.view_cmd=='matplot':
            fig = plt.figure()
            fig.suptitle("%s" % title)
            axs = fig.add_subplot(111)
            axs.imshow(self.img[slice_no,:,:])
#            fig.figimage(self.img[slice_no,:,:])
            plt.show(block=True)

    def gpetview(self,zoom=1,width=750,height=550,color=0,timestamp='',seq='',title='',number=1,amax=0):
        """view image by gpetview. You can use options zoom,width,height,color,seq,title,number. If you give amax, scale to max to amax"""

        if os.name == 'posix':
            if amax>0:
                g = GpetviewProcess(zoom=zoom,width=width,height=height,color=color,timestamp=timestamp,title=title,seq=seq,number=number,amax=amax)
            else:
                g = GpetviewProcess(zoom=zoom,width=width,height=height,color=color,timestamp=timestamp,title=title,seq=seq,number=number)
            g(self)
            return g
        else: #for windows
            tmpname = tempfile.mktemp()
            self.write(tmpname)
            if amax>0:
                os.system('gpetview -z %g -w %d %d -l %d -t %s -q %s -b %s -n %d -a %f 0 %s' % (zoom,width,height,color,timestamp,seq,title,number,tmpname,amax))
            else:
                os.system('gpetview -z %g -w %d %d -l %d -t %s -q %s -b %s -n %d %s' % (zoom,width,height,color,timestamp,seq,title,number,tmpname))
            os.remove(tmpname+'.hdr')
            os.remove(tmpname+'.img')
            return
    def match_hdr(self):
        """ adjust header type and size to image"""
        match_hdr(self)
    def match_type(self):
        """ adjust header type"""
        match_type(self)
    def match_size(self):
        """ adjust header size"""
        match_size(self)
    def max(self):
        """ show max value of image"""
        if self.hdr.funused1>0:
            return self.img.max()*self.hdr.funused1
        else:
            return self.img.max()


    def min(self):
        """ show min value of image"""
        return self.img.min()
    def scale(self):
        """ scaling image with hdr.funused1 and convert to float image """
        if self.hdr.funused1 == 0:
            self.img = self.img.astype('f')
            self.hdr.funused1 = 1.0
            match_type(self)
            return
        else:
            self.img = (self.hdr.funused1*self.img).astype('f')
            self.hdr.funused1 = 1.0
            match_type(self)
            return
    def zeros(self):
        """ prepare array of zeros according to header"""
        if self.hdr.datatype == TYPE_IMG_B:
            dtype = numpy.ubyte
        if self.hdr.datatype == TYPE_IMG_RGB:
            dtype = numpy.ubyte
        if self.hdr.datatype == TYPE_IMG_S:
            dtype = numpy.short #short
        if self.hdr.datatype == TYPE_IMG_I:
            dtype = numpy.int #int
        if self.hdr.datatype == TYPE_IMG_F:
            dtype = numpy.float32 #float
        if self.hdr.datatype == TYPE_IMG_D:
            dtype = numpy.double
        if self.hdr.datatype == TYPE_IMG_C:
            dtype = numpy.complex
        if self.hdr.dim[4]>1:
            self.img = numpy.zeros((self.hdr.dim[4],self.hdr.dim[3],self.hdr.dim[2],self.hdr.dim[1]),dtype=dtype)
        else:
            if self.hdr.datatype == TYPE_IMG_RGB:
                self.img = numpy.zeros((self.hdr.dim[3],self.hdr.dim[2],self.hdr.dim[1],3),dtype=dtype)
            else:
                self.img = numpy.zeros((self.hdr.dim[3],self.hdr.dim[2],self.hdr.dim[1]),dtype=dtype)
        return

    def transform(self,transmat):
        """transform image using Affine matrix (4x4)"""
        pixmat = numpy.array([abs(self.hdr.pixdim[1]),abs(self.hdr.pixdim[2]),abs(self.hdr.pixdim[3])],'f')
        if pixmat[0]<=0 or pixmat[1]<=0 or pixmat[2]<=0:
            print("please specify pixel size")
            return
        #to avoid sparse sampling we rather do reslice on resliced coordinate
        invtrmat = numpy.reshape(numpy.linalg.inv(transmat),(16,)).astype('f')
#        self.img = bldanaimgc.transform(self.img,pixmat,invtrmat).astype(origtype)
        self.img = bldanaimgc.transform(self.img,pixmat,invtrmat)
        self.match_type()
        return
    def zoom(self,zoom_factor,xzoom_factor=1,yzoom_factor=1,zzoom_factor=1,center_x=0,center_y=0,center_z=0):
        """zooming image with center of (center_x,center_y,center_z). Default center is (0,0,0)
        if you want to zoom particular direction, you rather give xzoom_factor,yzoom_factor,zzoom_factor
        """
        origtype = self.img.dtype
        pixmat = numpy.array([abs(self.hdr.pixdim[1]),abs(self.hdr.pixdim[2]),abs(self.hdr.pixdim[3])],'f')
        pixdim = numpy.array([abs(self.hdr.dim[1]),abs(self.hdr.dim[2]),abs(self.hdr.dim[3])],'f')
        if pixmat[0]<=0 or pixmat[1]<=0 or pixmat[2]<=0:
            print("please specify pixel size")
            return
#        xcenter = 0.5*pixdim[0]*pixmat[0]*zoom_factor
#        ycenter = 0.5*pixdim[1]*pixmat[1]*zoom_factor
#        zcenter = 0.5*pixdim[2]*pixmat[2]*zoom_factor
        xcenter = center_x
        ycenter = center_y
        zcenter = center_z
        tranmat = numpy.array([[zoom_factor*xzoom_factor,0,0,zoom_factor*xzoom_factor*xcenter],[0,zoom_factor*yzoom_factor,0,zoom_factor*yzoom_factor*ycenter],[0,0,zoom_factor*zzoom_factor,zoom_factor*zzoom_factor*zcenter],[0,0,0,1]],'f')
        self.transform(tranmat)
        self.img = self.img.astype(origtype)
        
    def rotate_z(self,deg,origin_x,origin_y):
        """rotate image along z axis. Give origin_x and origin_y"""
        pixmat = numpy.array([abs(self.hdr.pixdim[1]),abs(self.hdr.pixdim[2]),abs(self.hdr.pixdim[3])],'f')
        xdim = self.hdr.dim[1]
        ydim = self.hdr.dim[2]
        e = numpy.array([0,0,numpy.pi/180.*deg])
        m3 = qconv.etom3(e)
        trmat = numpy.zeros((4,4),'f')
        trmat[3,3] = 1
        trmat[0:3,0:3] = m3[:,:].astype('f')
        shiftmat = numpy.zeros((4,4,),'f')
        shiftmat[0,0] = 1
        shiftmat[1,1] = 1
        shiftmat[2,2] = 1
        shiftmat[3,3] = 1
        shiftmat[0,3] = origin_x
        shiftmat[1,3] = origin_y
        trmat = numpy.dot(shiftmat,numpy.dot(trmat,numpy.linalg.inv(shiftmat)))
        shiftmat2 = numpy.zeros((4,4,),'f')
        shiftmat2[0,0] = 1
        shiftmat2[1,1] = 1
        shiftmat2[2,2] = 1
        shiftmat2[3,3] = 1
        shiftmat2[0,3] = (xdim/2.0 - 0.5)*pixmat[0] - origin_x
        shiftmat2[1,3] = (ydim/2.0 - 0.5)*pixmat[1] - origin_y
        trmat = numpy.dot(shiftmat2,trmat)
        self.transform(trmat)

    def rotate_x(self,deg,origin_y,origin_z):
        """rotate image along x axis. Give origin_y and origin_z in mm"""
        pixmat = numpy.array([abs(self.hdr.pixdim[1]),abs(self.hdr.pixdim[2]),abs(self.hdr.pixdim[3])],'f')
        ydim = self.hdr.dim[2]
        zdim = self.hdr.dim[3]
        e = numpy.array([numpy.pi/180.*deg,0,0])
        m3 = qconv.etom3(e)
        trmat = numpy.zeros((4,4),'f')
        trmat[3,3] = 1
        trmat[0:3,0:3] = m3[:,:].astype('f')
        shiftmat = numpy.zeros((4,4,),'f')
        shiftmat[0,0] = 1
        shiftmat[1,1] = 1
        shiftmat[2,2] = 1
        shiftmat[3,3] = 1
        shiftmat[1,3] = origin_y
        shiftmat[2,3] = origin_z
        trmat = numpy.dot(shiftmat,numpy.dot(trmat,numpy.linalg.inv(shiftmat)))
        shiftmat2 = numpy.zeros((4,4,),'f')
        shiftmat2[0,0] = 1
        shiftmat2[1,1] = 1
        shiftmat2[2,2] = 1
        shiftmat2[3,3] = 1
        shiftmat2[1,3] = (ydim/2.0 - 0.5)*pixmat[1] - origin_y
        shiftmat2[2,3] = (zdim/2.0 - 0.5)*pixmat[2] - origin_z
        trmat = numpy.dot(shiftmat2,trmat)
        self.transform(trmat)

    def rotate_y(self,deg,origin_x,origin_z):
        """rotate image along y axis. Give origin_x and origin_z"""
        pixmat = numpy.array([abs(self.hdr.pixdim[1]),abs(self.hdr.pixdim[2]),abs(self.hdr.pixdim[3])],'f')
        xdim = self.hdr.dim[1]
        zdim = self.hdr.dim[3]
        e = numpy.array([0,numpy.pi/180.*deg,0])
        m3 = qconv.etom3(e)
        trmat = numpy.zeros((4,4),'f')
        trmat[3,3] = 1
        trmat[0:3,0:3] = m3[:,:].astype('f')
        shiftmat = numpy.zeros((4,4,),'f')
        shiftmat[0,0] = 1
        shiftmat[1,1] = 1
        shiftmat[2,2] = 1
        shiftmat[3,3] = 1
        shiftmat[0,3] = origin_x
        shiftmat[2,3] = origin_z
        trmat = numpy.dot(shiftmat,numpy.dot(trmat,numpy.linalg.inv(shiftmat)))
        shiftmat2 = numpy.zeros((4,4,),'f')
        shiftmat2[0,0] = 1
        shiftmat2[1,1] = 1
        shiftmat2[2,2] = 1
        shiftmat2[3,3] = 1
        shiftmat2[0,3] = (xdim/2.0 - 0.5)*pixmat[0] - origin_x
        shiftmat2[2,3] = (zdim/2.0 - 0.5)*pixmat[2] - origin_z
        trmat = numpy.dot(shiftmat2,trmat)
        self.transform(trmat)

    def show_hdr(self):
        """Show Header of Image"""
        self.hdr.show()
            
