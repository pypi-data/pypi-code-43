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

def transform():
    
    if '--help' in sys.argv or '-h' in sys.argv:
        
        print("""
              "-------------------------------------------------------------------------"
              ""
              "description:"
              ""
              "  This operation will plot the Fourier transform of given time series."
              "  The time series and FFT are shown interactively so the user can select"
              "  a desired time slot and get the FFT from that region."
              ""
              "required arguments:"
              ""
              "   --start          Starting date to retrieve data from."
              "   --end            Ending date to retrieve data from."
              "   --station        Station name"
              ""
              "optional arguments:"
              ""
              "   --discard        Discard first selected seconds"
              "   --fmin           Minimum frequency to display"
              "   --fmax           Maximum frequency to display"
              "   --nogps          No GPS provided, create time array using sample rate"
              "   --orientation    Orientation to extract if single (all by default)"
              "   --path           Custom repository where data are stored."
              "   --sample         Specify the data to be field sample, not regular."
              "   --scale          Rescale y axis"
              "   --unit           Time unit for plot."
              ""
              "example:"
              ""
              "  nuri transform --start 2017-03-09-15-58 --end 2017-03-10 \ "
              "                 --path /Users/vincent/ASTRO/data/others/sample1_background_noise/ \ "
              "                 --station magnet --sample --unit secs --nogps \ "
              "                 --discard 1 --fmin 1 --down 12 --seaborn"
              ""
              "-------------------------------------------------------------------------"
              """)
        quit()
        
    data = magfield(setup.start,setup.end,rep=setup.path)
    # Get start and ending timestamps
    if setup.start!=None and setup.end!=None:
        start,tmin,end,tmax = time_edge(setup.start,setup.end) 
    else:
        tmin,tmax = data[0,0],data[-1,0]
    # Convert every timing points to scale (hr,min,sec) units
    s = 1. if setup.unit=='secs' else 60. if setup.unit=='mins' else 3600.
    data[:,0] = (data[:,0]-data[0,0])/s
    # Create x axis time label
    tbeg = datetime.fromtimestamp(tmin)
    tend = datetime.fromtimestamp(tmax)
    sbeg = tbeg.strftime('%Y-%m-%d %H:%M:%S.%f')
    send = tend.strftime('%Y-%m-%d %H:%M:%S.%f')
    label1 = 'UTC time from %s to %s [%s]'%(sbeg,send,setup.unit)
    label2 = '%s-%s.png'%(int(tmin),int(tmax))
    # Initialise axis
    fig = figure(figsize=(15,10))
    plt.subplots_adjust(left=0.07,right=0.95,
                        bottom=0.1,top=0.95,
                        hspace=0.2,wspace=0.1)
    # Plot time series
    ax1 = subplot(231)
    ax1.plot(data[:,0],data[:,1]-np.average(data[:,1]))
    ax1.set_ylabel('Magnetic field [uT]')
    ax1.set_title('X field')
    ax2 = subplot(232,sharex=ax1,sharey=ax1)
    ax2.plot(data[:,0],data[:,2]-np.average(data[:,2]))
    ax2.set_xlabel(label1)
    ax2.set_title('Y field')
    plt.setp(ax2.get_yticklabels(),visible=False)
    ax3 = subplot(233,sharex=ax1,sharey=ax1)
    ax3.plot(data[:,0],data[:,3]-np.average(data[:,3]))
    ax3.set_xlim([data[0,0],data[-1,0]])
    ax3.set_title('Z field')
    plt.setp(ax3.get_yticklabels(),visible=False)
    # Create FFT of data
    N = len(data)
    T = 1.0 / (setup.rate/setup.down)
    f = np.linspace(0.0, 1.0/(2.0*T), N/2)
    i1 = abs(f-setup.fmin).argmin()
    i2 = len(f) if setup.fmax==None else abs(f-setup.fmax).argmin()
    f = f[i1:i2]
    x,y,z = data[:,1],data[:,2],data[:,3]
    x = 2.0/N * np.abs(fft(x)[:N//2])[i1:i2]
    y = 2.0/N * np.abs(fft(y)[:N//2])[i1:i2]
    z = 2.0/N * np.abs(fft(z)[:N//2])[i1:i2]
    # Plot FFT for x direction
    ax4 = subplot(234)
    ax4.plot(f,x,'k')
    ax4.set_ylabel('|Y(f)|')
    # Plot FFT for y direction
    ax5 = subplot(235,sharex=ax4,sharey=ax4)
    ax5.plot(f,y,'k')
    ax5.set_xlabel('Frequency [Hz]')
    plt.setp(ax5.get_yticklabels(),visible=False)
    # Plot FFT for z direction
    ax6 = subplot(236,sharex=ax4,sharey=ax4)
    ax6.plot(f,z,'k')
    ax6.set_xlim(1,f[-1])
    ax6.set_ylim(0,max(np.hstack((x,y,z)))/setup.scale)
    plt.setp(ax6.get_yticklabels(),visible=False)
    # Save figure
    plt.savefig(label2)
    plt.close(fig)
