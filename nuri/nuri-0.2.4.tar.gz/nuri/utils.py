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

import sys,numpy,time
from datetime import datetime
from gwpy.timeseries import TimeSeries

def is_float(a):
    try:
        float(a)
        return True
    except ValueError:
        return False

def biomed_read():

    setup.down    = 1
    setup.rescale = True
    #setup.sample  = False
    #setup.start   = '2016-9-15-6'
    #setup.end     = '2016-9-15-7'
    # Get start and ending timestamps
    start,tmin,end,tmax = time_edge(setup.start,setup.end)
    # Get NURI data
    path  = '/Users/vincent/ASTRO/data/DAQ_NURI1/'
    data  = magfield(setup.start,setup.end,rep=path)
    quit()
    # Create x axis time label
    tbeg = datetime.fromtimestamp(tmin)
    tend = datetime.fromtimestamp(tmax)
    sbeg = tbeg.strftime('%Y-%m-%d %H:%M:%S.%f')
    send = tend.strftime('%Y-%m-%d %H:%M:%S.%f')
    label1 = 'UTC time from %s to %s [secs]'%(sbeg,send)
    label2 = '%s-%s.png'%(int(tmin),int(tmax))
    # Plot pulse delay only
    fig = figure(figsize=(10,6))
    plt.subplots_adjust(left=0.1, right=0.95,
                        bottom=0.1, top=0.95,
                        hspace=0.1, wspace=0)
    ax = plt.subplot(111)
    print(min(data[:,1]),max(data[:,1]))
    ax.plot(data[:,0],data[:,1])
    ax.set_xlabel(label1)
    savefig(label2)
    clf()

def make_video():
    
    os.system('ls *.png > list.dat')
    filelist = sorted(numpy.loadtxt('list.dat',dtype=str))
    for i in range(len(filelist)):
        newpath = 'series%04i.png'%(i+1)
        if os.path.exists(newpath)==False:
            os.system('cp %s %s'%(filelist[i],newpath))
    os.system('ffmpeg -framerate 30 -i series%04d.png  -start_number 1 -c:v libx264 -r 30 -pix_fmt yuv420p ../video.mp4')
    os.system('rm list.dat series*')
    
def str2timestamp(*times):
    """
    Create mask for user-defined time range.
    """
    time_list = []
    for dt in times:
        # Split date by dashes
        dt = numpy.array(dt.split('-'),dtype=int)
        # Include day 1 if no day provided
        dt = dt if len(dt)>2 else numpy.hstack((dt,1))
        # Convert string to datetime format
        dt = datetime(*dt)
        # Convert start date into timestamp
        dt = time.mktime(dt.timetuple())+dt.microsecond/1e6
        # Convert timestamp back local datetime
        now = datetime.fromtimestamp(dt)
        # Convert timestamp to UTC datetime
        utc_now = datetime.utcfromtimestamp(dt)
        # Calculate local difference with UTC time
        utc2local = (now-utc_now).total_seconds()
        # Remove UTC offset from timestamp
        dt += utc2local
        time_list.append(dt)
    return tuple(time_list) if len(time_list)>1 else time_list[0]

def str2datetime(*dates):
    '''
    Convert input string date to datetime format.
    '''
    date_list = []
    for date in dates:
        dstr = ['%Y','%m','%d','%H','%M','%S','%f']
        dsplit = '-'.join(dstr[:date.count('-')+1])
        date = datetime.strptime(date,dsplit)
        date_list.append(date)
    return tuple(date_list) if len(date_list)>1 else date_list[0]

def get_scalar(data):
    '''
    Calculate scalar signal from each directional magnetic field data.

    Parameters
    ----------
    data : numpy.array
      Timestamps and directional magnetic field signals
    
    Return
    ------
    data : numpy.array
      Return modified data array with scalar values
    '''
    scalar = numpy.sqrt(numpy.sum(abs(data[:,1:])**2,axis=1,dtype=float))
    return numpy.vstack((data[:,0],scalar)).T

