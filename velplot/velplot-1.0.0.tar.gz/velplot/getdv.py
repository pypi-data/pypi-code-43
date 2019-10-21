import numpy
from .constants import *

def get_dv(dvplot,zmid,header,table1,comment):
    '''
    Calculate central redshift and velocity dispersion.
    '''
    # Calculate mid-redshift among all fitting regions
    if zmid==None:
        zreg = numpy.empty((0,2))
        for j in range (len(table1)):
            text_comment = comment[j,0].split()
            if 'external' not in text_comment:
                zmin = float(table1[j][2])/float(header[j,1])-1
                zmax = float(table1[j][3])/float(header[j,1])-1
            else:
                # Get redshit edges of the external fitting region
                wref = float(atominfo(comment[0])[1])
                wmin = table1[j][2]
                wmax = table1[j][3]
                zmin = float(wmin)/wref-1
                zmax = float(wmax)/wref-1
                # Get wavelength edges of the associated tied region
                wref = float(atominfo(comment[2])[1])
                wmin = wref*(zmin+1)
                wmax = wref*(zmax+1)
                # Get redshift edges of the corresponding overlapping region
                wref = float(atominfo(get_trans(comment[2]))[1])
                zmin = float(wmin)/wref-1
                zmax = float(wmax)/wref-1
            zreg = numpy.vstack([zreg,[zmin,zmax]])
        zmid = (min(zreg[:,0])+max(zreg[:,1]))/2.
    # Calculate maximum velocity dispersions
    dv = 0
    for j in range (len(header)):
        text_comment = comment[j,0].split()
        if 'external' in text_comment:
            wref  = float(header[j,1])
            # Wavelength at zmid in the overlapping region
            reg   = float(atominfo(get_trans(comment[2]))[1])*(zmid+1)
            # Transition wavelength of the overlapping element
            atom  = float(atominfo(comment[2])[1])
            # Central wavelength of external tied transition for the overlapped system
            wamid = wref*(reg/atom)
            text  = comment[0]+' at z='+str(round(wamid/float(header[j,1])-1,6))
            dvmin = abs(2*(table1[j][2]-wamid)/(table1[j][2]+wamid))*c
            dvmax = abs(2*(table1[j][3]-wamid)/(table1[j][3]+wamid))*c
            dv    = max(dv,dvmin,dvmax)
        elif 'overlap' in text_comment:
            wamid = float(header[j,1])*(zmid+1)
            text  = comment[2]+' at z='+str(round(wamid/float(atominfo(comment[2])[1])-1,6))
            dvmin = abs(2*(table1[j][2]-wamid)/(table1[j][2]+wamid))*c
            dvmax = abs(2*(table1[j][3]-wamid)/(table1[j][3]+wamid))*c
            dv    = max(dv,dvmin,dvmax)
        else:
            wamid = float(header[j,1])*(zmid+1)
            text  = '-'
            dvmin = abs(2*(table1[j][2]-wamid)/(table1[j][2]+wamid))*c
            dvmax = abs(2*(table1[j][3]-wamid)/(table1[j][3]+wamid))*c
            dv    = max(dv,dvmin,dvmax)
        comment[j,1:] = [text,wamid]
    dv = dvplot if dvplot!=None else 150 if dv<150 else dv
    return dv,zmid

def get_trans(overlaptrans):
    '''
    Find transition part of overlap system, if existing.
    '''
    for k in range (len(comment)):
        headline = comment[k,0].split()
        if 'overlap' in headline and headline[2]==overlaptrans:
            break
    return headline[0]
