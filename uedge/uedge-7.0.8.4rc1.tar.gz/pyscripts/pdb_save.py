
import numpy as np
import pact.pdb as pdb
from uedge import bbb



def pdb_save(file):
    """
        Write a pdb file from Uedge. Thist puts
        the 6 standard variables into the correct format.
    """
    try:
        fp = pdb.open(file,'w')
    except:
        print "Couldn't open pdb file ",file
    try:
        fp.write("ngs@bbb",bbb.ngs.reshape(bbb.ngs.shape[::-1]).transpose().tolist(),ind=bbb.ngs.shape)
    except:
        print "Couldn't write ngs to  ",file
    try:
        fp.write('nis@bbb',bbb.nis.transpose().tolist(),ind=bbb.nis.shape)
    except:
        print "Couldn't write nis to  ",file
    try:
        fp.write('phis@bbb',bbb.phis.tolist())
    except:
        print "Couldn't write phis to  ",file
    try:
        fp.write('tes@bbb',bbb.tes.tolist())
    except:
        print "Couldn't write tes to  ",file
    try:
        fp.write('tis@bbb',bbb.tis.tolist())
    except:
        print "Couldn't write tis to  ",file
    try:
        fp.write('ups@bbb',bbb.ups.tolist())
    except:
        print "Couldn't write ups to  ",file
    try:
        fp.write('tgs@bbb',bbb.tgs.tolist())
    except:
        print "Couldn't write tgs to  ",file

    fp.close()


