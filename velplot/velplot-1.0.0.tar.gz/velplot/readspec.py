import os,numpy
import astropy.io.fits as fits

def read_spec(i,table1):
    '''
    Read spectrum and extract wavelength and flux dataset.
    '''
    specfile = table1[i][0]
    datatype = specfile.split('.')[-1]
    wavefile = specfile.replace('.fits','.wav.fits')
    if datatype=='fits' and os.path.exists(wavefile)==True:
        fh = fits.open(wavefile)
        hd = fh[0].header
        specwa = fh[0].data
        fh = fits.open(specfile)
        hd = fh[0].header
        specfl = fh[0].data        
    elif datatype=='fits':
        fh = fits.open(specfile)
        hd = fh[0].header
        d  = fh[0].data
        if ('CTYPE1' in hd and hd['CTYPE1'] in ['LAMBDA','LINEAR']) or ('DC-FLAG' in hd and hd['DC-FLAG']=='0'):
            specwa = hd['CRVAL1'] + (hd['CRPIX1'] - 1 + numpy.arange(hd['NAXIS1']))*hd['CDELT1']
        else:
            specwa = 10**(hd['CRVAL1'] + (hd['CRPIX1'] - 1 + numpy.arange(hd['NAXIS1']))*hd['CDELT1'])
        if len(d.shape)==1:
            specfl = d[:]
        else:
            specfl = d[0,:]
    else:
        d = numpy.loadtxt(specfile,comments='!')
        specwa = d[:,0]
        specfl = d[:,1]
    return specwa,specfl
