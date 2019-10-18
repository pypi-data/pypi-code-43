#numpyio implemented by H. Watabe
#$Id: numpyio.py,v d8276cbaa869 2016/07/06 00:22:34 watabe $ 2016 copyright by H. Watabe watabe@cyric.tohoku.ac.jp
import numpy

def fwrite(fp,nfr,ar,dtype,swap_flag):
    array1d = ar.reshape((int(nfr),))
    if swap_flag==1:
        array1d = array1d.byteswap()
    fp.write(array1d.tobytes())
#    array1d.tofile(fp)
    return

def bswap(ar):
	return ar.byteswap()

def fread(fp,nfr,dtype,swap_flag = 0):
    array1d = numpy.fromfile(fp,dtype=dtype,count=int(nfr))
    if swap_flag==1:
        array1d = array1d.byteswap()
    return array1d
