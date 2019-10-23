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
import sys,os,numpy
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime,timedelta

def get_activity(year,month):
    """
    This operation will display the active periods for which data are
    available from every sensors.
    
    Parameters
    ----------
    year : int
      Year to display activity from.
    month : int
      Month to display activity from.

    Examples
    --------
      >>> nuri active -y 2017 -m 10
    """
    # List all the months
    dates = numpy.empty((0,5))
    y0    = int(year)
    m0    = int(month)
    d0    = datetime(y0,m0,1)
    y1    = y0   if m0<12 else y0+1
    m1    = m0+1 if m0<12 else 1
    d1    = datetime(y1,m1,1)-timedelta(hours=1)
    dt    = timedelta(hours=1)
    dates = numpy.arange(d0,d1,dt)
    # Download metadata from Google Drive
    sys.stderr.write('Retrieve information from Google Drive...')
    os.system('skicka ls -r /MagneticFieldData/%s/%s/ > data'%(y0,m0))
    data = numpy.loadtxt('data',dtype=str,delimiter='\n')
    print(sys.stderr,' done!')
    # List file path for each date and each station
    sys.stderr.write('Select active hours for each station...')
    st0,st1,st2,st3,st4 = [],[],[],[],[]
    for d in dates:
        year  = d.astype(object).year
        month = d.astype(object).month
        day   = d.astype(object).day
        hour  = d.astype(object).hour
        path  = 'MagneticFieldData/%i/%i/%i/%i/'%(year,month,day,hour)
        fname = '%i-%i-%i_%i-xx.zip'%(year,month,day,hour)
        st0.append(path+'NURI-station/'   +fname)
        st1.append(path+'NURI-station-01/'+fname)
        st2.append(path+'NURI-station-02/'+fname)
        st3.append(path+'NURI-station-03/'+fname)
        st4.append(path+'NURI-station-04/'+fname)
    st0 = numpy.array([1 if path in data else 0 for path in st0])
    st1 = numpy.array([1 if path in data else 0 for path in st1])
    st2 = numpy.array([1 if path in data else 0 for path in st2])
    st3 = numpy.array([1 if path in data else 0 for path in st3])
    st4 = numpy.array([1 if path in data else 0 for path in st4])
    print(sys.stderr,' done!')
    # Write down information in text file
    print('Save information in ASCII file...')
    o = open('%i-%02i.txt'%(y0,m0),'w')
    for d in dates:
        year  = d.astype(object).year
        month = d.astype(object).month
        day   = d.astype(object).day
        hour  = d.astype(object).hour
        path  = 'MagneticFieldData/%i/%i/%i/%i/'%(year,month,day,hour)
        fname = '%i-%i-%i_%i-xx.zip'%(year,month,day,hour)
        o.write('%i-%02i-%02i_%02i'%(year,month,day,hour))
        for i in range(5):
            station = 'NURI-station-%02i'%i if i>0 else 'NURI-station'
            text = station if path+station+'/'+fname in data else '-'
            o.write('  {:<15}'.format(text))
        o.write('\n')
    o.close()
    dates = [d.astype(object) for d in dates]
    plt.rc('font', size=2, family='serif')
    plt.rc('axes', labelsize=10, linewidth=0.2)
    plt.rc('legend', fontsize=2, handlelength=10)
    plt.rc('xtick', labelsize=7)
    plt.rc('ytick', labelsize=7)
    plt.rc('lines', lw=0.2, mew=0.2)
    plt.rc('grid', linewidth=0.2)
    fig = plt.figure(figsize=(10,6))
    plt.subplots_adjust(left=0.07, right=0.95, bottom=0.1, top=0.96, hspace=0.2, wspace=0)
    print('Plot active time for station 1...')
    ax1 = fig.add_subplot(511)
    ax1.bar(dates,st1,width=1/24.,edgecolor='none')
    ax1.tick_params(direction='in')
    ax1.set_ylabel('Station 1')
    ax1.xaxis_date()
    plt.yticks([])
    ax1.grid()
    print('Plot active time for station 2...')
    ax = fig.add_subplot(512,sharex=ax1,sharey=ax1)
    ax.bar(dates,st2,width=1/24.,edgecolor='none')
    ax.tick_params(direction='in')
    ax.set_ylabel('Station 2')
    ax.xaxis_date()
    plt.yticks([])
    ax.grid()
    print('Plot active time for station 3...')
    ax = fig.add_subplot(513,sharex=ax1,sharey=ax1)
    ax.bar(dates,st3,width=1/24.,edgecolor='none')
    ax.tick_params(direction='in')
    ax.set_ylabel('Station 3')
    ax.xaxis_date()
    plt.yticks([])
    ax.grid()
    print('Plot active time for station 4...')
    ax = fig.add_subplot(514,sharex=ax1,sharey=ax1)
    ax.bar(dates,st4,width=1/24.,edgecolor='none')
    ax.tick_params(direction='in')
    ax.set_ylabel('Station 4')
    ax.xaxis_date()
    plt.yticks([])
    ax.grid(False)
    print('Plot active time for station 0...')
    ax = fig.add_subplot(515,sharex=ax1,sharey=ax1)
    ax.bar(dates,st0,width=1/24.,edgecolor='none')
    ax.tick_params(direction='in')
    ax.set_ylabel('Unnamed')
    ax.xaxis_date()
    plt.yticks([])
    ax.grid(False)
    ax.set_xlabel(r'Hourly activity in %s %i (UTC)'%(d0.strftime("%B"),y0))
    ax1.xaxis.set_major_formatter(md.DateFormatter('%d'))
    ax1.xaxis.set_major_locator(md.DayLocator())
    ax1.set_xlim(d0,d1)
    ax1.set_ylim(0,1)
    plt.savefig('%i-%02i'%(y0,m0),transparent=True,dpi=300)
    
def check24hrs(t0,t1,station):
    """
    This operation will display the active periods for which data are
    available from every sensors.

    Parameters
    ----------

    date : str
      Year and month to display activity from. The format shoud be YYYY-MM.
    """
    # Download metadata from Google Drive
    sys.stderr.write('Retrieve information from Google Drive...')
    os.system('skicka ls -r /MagneticFieldData/ > data')
    data = numpy.loadtxt('data',dtype=str,delimiter='\n')
    print(sys.stderr,' done!')
    # Get date list
    t0 = datetime(*numpy.array(t0.split('-'),dtype=int))
    t1 = datetime(*numpy.array(t1.split('-'),dtype=int))
    dt = timedelta(hours=1)
    dates = numpy.arange(t0,t1,dt)
    # List file path for each date and each station
    tick = 0
    for d in dates:
        year  = d.astype(object).year
        month = d.astype(object).month
        day   = d.astype(object).day
        hour  = d.astype(object).hour
        path  = 'MagneticFieldData/%i/%i/%i/%i/'%(year,month,day,hour)
        fname = '%i-%i-%i_%i-xx.zip'%(year,month,day,hour)
        if path+'NURI-station-%02i/'%station+fname in data:
            tick+=1
        if tick==24:
            print(year,month,day,hour)
        if hour==23:
            tick = 0
    os.system('rm data')

def download(period,date,length,station):
    """
    Download data for specific period. The default period downloaded will
    be the last 24 hours.

    Parameters
    ----------
    period : array
      Starting and ending dates of selected period
    date : str
      Starting date
    length : float
      Time length in seconds
    station : float
      Station number. Default is all stations.

    Examples
    --------
    >>> nuri download --start 2016-03-20 --end 2016-03-21 --station 4
    """
    # Convert start and end date into datetime object
    if period==None and date==None:
        print('You must defined either a period or a date and length. Abort.')
        quit()
    if period!=None:
        d0 = datetime(*numpy.array(period[0].split('-'),dtype=int))
        d1 = datetime(*numpy.array(period[1].split('-'),dtype=int))
    else:
        d0 = datetime(*numpy.array(date.split('-'),dtype=int))
        d1 = d0 + timedelta(seconds=float(length))
    # Store data for current month
    y0,m0 = d0.year,d0.month
    os.system('skicka ls -r /MagneticFieldData/%s/%s/ > data'%(y0,m0))
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
                os.system('rm '+fzip)
    os.system('rm data')

def notification():
    '''
    Check list of files on server and notify station if missing data.
    This operation will check if station are uploading data properly
    and will notify the relevant station's owner if missing data are
    being detected.
    '''
    os.chdir(setup.home+'/analysis/nuri/activetime/')
    sys.stderr.write('Retrieve information from Google Drive...')
    os.system('skicka ls -r /MagneticFieldData/ > data')
    data = np.loadtxt('data',dtype=str,delimiter='\n')
    print(sys.stderr,' done!')
    for station in [1,2,3,4]:
        missing = []
        target  = datetime.utcnow()-timedelta(days=1)
        for hr in range(24):
            target = datetime(target.year,target.month,target.day,hr)
            str1   = target.strftime('%Y/%-m/%-d/%-H')
            str2   = target.strftime('%Y-%-m-%-d_%-H')
            if 'MagneticFieldData/%s/NURI-station-%02i/%s-xx.zip'%(str1,station,str2) not in data:
                missing.append(hr)
        if len(missing)>0:
            yesterday   = (date.today()-timedelta(1)).strftime('%A, %B %d, %Y')
            EMAIL_FROM  = 'vincentdumont11@gmail.com'
            EMAIL_TO    = ['bale@ssl.berkeley.edu'] if station==1 else \
                          ['vdumont@berkeley.edu']  if station==2 else \
                          ['wurtele@berkeley.edu']  if station==3 else \
                          ['dbudker@gmail.com']
            EMAIL_SPACE = ', '
            hrs = EMAIL_SPACE.join(['%i'%hr for hr in missing])
            msg ="Dear Station's owner,\n"
            msg+='\n'
            msg+='%i out of 24 data files are found missing from yesterday:\n'%len(missing)
            msg+='%s\n'%yesterday
            msg+='\n'
            msg+='The missing hours are the following:\n'
            msg+='%s\n'%hrs
            msg+='\n'
            msg+='Please check your station and make sure the computer is turned on\n'
            msg+='and all the USB cables are properly connected.\n'
            msg+='\n'
            msg+='Here are the instructions to reset the station:\n'
            msg+='\n'
            msg+='1. Disconnect each USB cable;\n'
            msg+='2. Shut down the computer;\n'
            msg+='3. Reconnect the cables;\n'
            msg+='4. Turn on the computer;\n'
            msg+='5. Open the data grabber application (available from the Desktop)\n'
            msg+='6. Click the "refresh" button for the GPS to make sure it identifies\n'
            msg+='the correct port;\n'
            msg+='7. Hit the "open" button. If the connection works properly, you should\n'
            msg+='see a text highlighted in green mentioning the UTC time. If the text\n'
            msg+='says "No Data", then there is a problem with the USB connection, try\n'
            msg+='re-connecting the cable on a different port and refresh.\n'
            msg+='8. Click the "refresh" button for the sensor to make sure it identifies\n'
            msg+='the correct port;\n'
            msg+='9. Hit "record", you should start seeing the data streaming on the screen;\n'
            msg+='\n'
            msg+="Do not close the application! The laptop's lid can be closed though.\n"
            msg+='As long as the computer is still turned on, data should be streaming\n'
            msg+='and uploading without any problem.\n'
            msg+='\n'
            msg+='Many thanks!\n'
            msg+='Vincent'
            msg = MIMEText(msg)
            msg['Subject'] = 'NURI Automatic Notification - Missing data from station %i...'%station
            msg['From']    = EMAIL_FROM
            msg['To']      = EMAIL_SPACE.join(EMAIL_TO)
            smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtpObj.login(EMAIL_FROM, 'newaknlsgkwehexe')
            smtpObj.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            smtpObj.quit()
    os.system('rm data')
    
