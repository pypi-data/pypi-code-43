###############################################################################
# Copyright (c) 2018, Urban Magnetometry Group.
#
# Produced at the University of California at Berkeley.
#
# Written by V. Dumont (vincentdumont11@gmail.com).
#
# All rights reserved.
#
# This file is part of NURI.
#
# For details, see github.com/vincentdumont/nuri.
#
# For details about use and distribution, please read NURI/LICENSE.
###############################################################################
import nuri,os,numpy
from datetime import datetime,timedelta

def make_hour_spec(t0,t1,station=None):
    """
    Download data for specific period. The default period downloaded will
    be the last 24 hours.

    Parameters
    ----------
    station : float
      Station number. Default is all stations.
    start : str
      Starting date of the data to be retrieved, YYYY-MM-DD-HH
    end : Ending date of the data to be retrieved, YYYY-MM-DD-HH

    Examples
    --------
    >>> nuri_download --start 2016-03-20 --end 2016-03-21 --station 4
    """
    # Convert start and end date into datetime object
    d0 = datetime(*numpy.array(t0.split('-'),dtype=int)) if t0!=None else datetime(2015,11,1)
    d1 = datetime(*numpy.array(t1.split('-'),dtype=int)) if t1!=None else datetime.now()+timedelta(days=1)
    # Store data for current month
    os.system('skicka ls -r /MagneticFieldData/ > data')
    data = numpy.loadtxt('data',dtype=str,delimiter='\n')
    # Loop through every hour
    for d in numpy.arange(d0,d1,timedelta(hours=1)):
        # Extract individual parameters from datetime object
        year  = d.astype(object).year
        month = d.astype(object).month
        day   = d.astype(object).day
        hour  = d.astype(object).hour
        # Define remote path to and filename of the compressed archive
        path  = 'MagneticFieldData/%i/%i/%i/%i/'%(year,month,day,hour)
        fzip  = '%i-%i-%i_%i-xx.zip'%(year,month,day,hour)
        # Loop through each station
        for i in range(4):
            # Define full path to archive
            fullpath = path+'NURI-station-%02i/'%(i+1)+fzip
            # Check if station is targeted and remote path exists
            if (station==None or int(station)==i+1) and fullpath in data:
                # Download, uncompress and store data
                os.system('mkdir -p ./NURI-station-%02i/'%(i+1))
                os.system('skicka download /%sNURI-station-%02i/%s ./'%(path,i+1,fzip))
                os.system('unzip '+fzip)
                os.system('mv %i-%i-%i_%i-xx_* NURI-station-%02i'%(year,month,day,hour,i+1))
                t0 = '%i-%i-%i-%i'%(year,month,day,hour)
                dnext = d.astype(object)+timedelta(hours=1)
                t1 = '%i-%i-%i-%i'%(dnext.year,dnext.month,dnext.day,dnext.hour)
                mag_data = get_data(t0,t1,downfactor=3960,station=i+1,rep='./')
                tmin,tmax = str2timestamp(d.astype(object),dnext)
                fname = 'NURI-station-%02i/%i-%02i-%02i_%02i'%(i+1,year,month,day,hour)
                plot_spectrogram(mag_data,tmin,tmax,fscale='mHz',scale='mins',tbs=True,fname=fname)
                os.system('rm %s NURI-station-%02i/%i-%i-%i_%i-xx_*'%(fzip,i+1,year,month,day,hour))
    os.system('rm data')
