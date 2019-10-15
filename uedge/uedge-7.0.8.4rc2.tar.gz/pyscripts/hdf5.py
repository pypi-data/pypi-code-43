
import numpy as np
import h5py
from uedge import bbb
from uedge_lists import *
import time


def hdf5_restore(file):
    """
        Read a hdf5 file previously written from Uedge. This reads the file and puts
        the 6 standard variables into the correct format.
    """
    try:
        hf = h5py.File(file, 'r')
    except ValueError as error:
        print "Couldn't open hdf5 file ", file
        print(error)
    except:
        print "Couldn't open hdf5 file ", file
        return

    try:
        dummy = hf['bbb']   # force an exception if the group not there
        hfg = hf.get('bbb')
        print "New style hdf5 file"
        try:
            bbb.ngs[...] = np.array(hfg.get('ngs'))
        except ValueError as error:
            print "Couldn't read ngs from  ", file
            print(error)
        except:
            print "Couldn't read ngs from  ", file
        try:
            bbb.nis[...] = np.array(hfg.get('nis'))
        except ValueError as error:
            print "Couldn't read nis from  ", file
            print(error)
        except:
            print "Couldn't read nis from  ", file
        try:
            bbb.phis[...] = np.array(hfg.get('phis'))
        except ValueError as error:
            print "Couldn't read phis from  ", file
            print(error)
        except:
            print "Couldn't read phis from  ", file
        try:
            bbb.tes[...] = np.array(hfg.get('tes'))
        except ValueError as error:
            print "Couldn't read tes from  ", file
            print(error)
        except:
            print "Couldn't read tes from  ", file
        try:
            bbb.tis[...] = np.array(hfg.get('tis'))
        except ValueError as error:
            print "Couldn't read tis from  ", file
            print(error)
        except:
            print "Couldn't read tis from  ", file
        try:
            bbb.ups[...] = np.array(hfg.get('ups'))
        except ValueError as error:
            print "Couldn't read ups from  ", file
            print(error)
        except:
            print "Couldn't read ups from  ", file
        try:
            bbb.tgs[...] = np.array(hfg.get('tgs'))
        except ValueError as error:
            print "Couldn't read tgs from  ", file
            print(error)
        except:
            print "Couldn't read tgs from  ", file

    except:
        print "Old style hdf5 file"
        try:
            bbb.ngs[...] = np.array(hf.get('ngs@bbb'))
        except ValueError as error:
            print "Couldn't read ngs from  ", file
            print(error)
        except:
            print "Couldn't read ngs from  ", file
        try:
            bbb.nis[...] = np.array(hf.get('nis@bbb'))
        except ValueError as error:
            print "Couldn't read nis from  ", file
            print(error)
        except:
            print "Couldn't read nis from  ", file
        try:
            bbb.phis[...] = np.array(hf.get('phis@bbb'))
        except ValueError as error:
            print "Couldn't read phis from  ", file
            print(error)
        except:
            print "Couldn't read phis from  ", file
        try:
            bbb.tes[...] = np.array(hf.get('tes@bbb'))
        except ValueError as error:
            print "Couldn't read tes from  ", file
            print(error)
        except:
            print "Couldn't read tes from  ", file
        try:
            bbb.tis[...] = np.array(hf.get('tis@bbb'))
        except ValueError as error:
            print "Couldn't read tis from  ", file
            print(error)
        except:
            print "Couldn't read tis from  ", file
        try:
            bbb.ups[...] = np.array(hf.get('ups@bbb'))
        except ValueError as error:
            print "Couldn't read ups from  ", file
            print(error)
        except:
            print "Couldn't read ups from  ", file
        try:
            bbb.tgs[...] = np.array(hf.get('tgs@bbb'))
        except ValueError as error:
            print "Couldn't read tgs from  ", file
            print(error)
        except:
            print "Couldn't read tgs from  ", file

    hf.close()


def hdf5_save(file):
    """
        Write the 6 standard variables into an hdf5 file.
    """
    try:
        hf = h5py.File(file, 'w')
        hfg = hf.create_group('bbb')
        hfg.attrs['time'] = time.time()
        hfg.attrs['ctime'] = time.ctime()
        hfg.attrs['code'] = 'UEDGE'
        hfg.attrs['ver'] = bbb.uedge_ver
    except ValueError as error:
        print "Couldn't open hdf5 file ", file
        print(error)
    except:
        print "Couldn't open hdf5 file ", file
        raise
    try:
        d = hfg.create_dataset('ngs', data=bbb.ngs)
        d.attrs['units'] = bbb.getvarunit('ngs')
        d.attrs['comment'] = bbb.getvardoc('ngs')
    except ValueError as error:
        print "Couldn't write ngs to  ", file
        print(error)
    except:
        print "Couldn't write ngs to  ", file
    try:
        d = hfg.create_dataset('nis', data=bbb.nis)
        d.attrs['units'] = bbb.getvarunit('nis')
        d.attrs['comment'] = bbb.getvardoc('nis')
    except ValueError as error:
        print "Couldn't write nis to  ", file
        print(error)
    except:
        print "Couldn't write nis to  ", file
    try:
        d = hfg.create_dataset('phis', data=bbb.phis)
        d.attrs['units'] = bbb.getvarunit('phis')
        d.attrs['comment'] = bbb.getvardoc('phis')
    except ValueError as error:
        print "Couldn't write phis to  ", file
        print(error)
    except:
        print "Couldn't write phis to  ", file
    try:
        d = hfg.create_dataset('tes', data=bbb.tes)
        d.attrs['units'] = bbb.getvarunit('tes')
        d.attrs['comment'] = bbb.getvardoc('tes')
    except ValueError as error:
        print "Couldn't write tes to  ", file
        print(error)
    except:
        print "Couldn't write tes to  ", file
    try:
        d = hfg.create_dataset('tis', data=bbb.tis)
        d.attrs['units'] = bbb.getvarunit('tis')
        d.attrs['comment'] = bbb.getvardoc('tis')
    except ValueError as error:
        print "Couldn't write tis to  ", file
        print(error)
    except:
        print "Couldn't write tis to  ", file
    try:
        d = hfg.create_dataset('ups', data=bbb.ups)
        d.attrs['units'] = bbb.getvarunit('ups')
        d.attrs['comment'] = bbb.getvardoc('ups')
    except ValueError as error:
        print "Couldn't write ups to  ", file
        print(error)
    except:
        print "Couldn't write ups to  ", file
    try:
        d = hfg.create_dataset('tgs', data=bbb.tgs)
        d.attrs['units'] = bbb.getvarunit('tgs')
        d.attrs['comment'] = bbb.getvardoc('tgs')
    except ValueError as error:
        print "Couldn't write tgs to  ", file
        print(error)
    except:
        print "Couldn't write tgs to  ", file

    hf.close()


def hdf5_dump(file, packages=list_packages(objects=1)):
    """
       Dump all variables from a list of package objects into a file.
       Default packages are output of uedge.uedge_lists.list_packages() 
    """
    try:
        hf = h5py.File(file, 'w')
    except ValueError as error:
        print "Couldn't open hdf5 file ", file
        print(error)
    except:
        print "Couldn't open hdf5 file ", file
    for p in packages:
        hfg = hf.create_group(p.name())
        hfg.attrs['time'] = time.time()
        hfg.attrs['ctime'] = time.ctime()
        hfg.attrs['code'] = 'UEDGE'
        hfg.attrs['ver'] = bbb.uedge_ver
        for v in list_package_variables(p):
            if p.allocated(v):
                try:
                    d = hfg.create_dataset(v, data=p.getpyobject(v))
                    d.attrs['units'] = bbb.getvarunit(v)
                    d.attrs['comment'] = bbb.getvardoc(v)
                except ValueError as error:
                    print "Couldn't write out: "+p.name()+'.'+v
                    print(error)
                except:
                    print "Couldn't write out: "+p.name()+'.'+v
            else:
                print p.name()+'.'+v+" is not allocated"
    hf.close()
