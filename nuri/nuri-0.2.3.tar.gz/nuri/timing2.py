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
def timing2():

    rep = '%s_%s'%(setup.start,setup.end)
    os.system('mkdir -p %s'%rep)
    os.chdir(rep)
    #----------------------------------------------------------
    # Extract magnetic field data
    #----------------------------------------------------------
    # Get NURI data
    path  = '/Users/vincent/ASTRO/data/NURI/timing/run%i/station1/'%setup.run
    nuri1 = magfield(setup.start,setup.end,rep=path)
    nuri1_pulse = (max(nuri1[:,1])+min(nuri1[:,1]))/2.
    print(nuri1_pulse)
    # Get NURI data
    path  = '/Users/vincent/ASTRO/data/NURI/timing/run%i/station2/'%setup.run
    nuri2 = magfield(setup.start,setup.end,rep=path)
    nuri2_pulse = (max(nuri2[:,1])+min(nuri2[:,1]))/2.
    # Get GNOME data
    path  = '/Users/vincent/ASTRO/data/GNOME/timing/'
    gnome1 = gnomedata('Berkeley02',setup.start,setup.end,rep=path)
    gnome1_pulse = (max(gnome1[:,1])+min(gnome1[:,1]))/2.
    # Get GNOME data
    path  = '/Users/vincent/ASTRO/data/GNOME/timing/'
    gnome2 = gnomedata('Berkeley02',setup.start,setup.end,rep=path,
                      setname='Pump_PID')
    gnome2_pulse = (max(gnome2[:,1])+min(gnome2[:,1]))/2.
    #----------------------------------------------------------
    # Get start and ending timestamps
    #----------------------------------------------------------
    if setup.sample==False or setup.rescale:
        tmin = max(nuri1[0,0],nuri2[0,0],gnome1[0,0],gnome2[0,0])
        tmax = min(nuri1[-1,0],nuri2[-1,0],gnome1[-1,0],gnome2[-1,0])
    else:
        start,tmin,end,tmax = time_edge(setup.start,setup.end)
    #----------------------------------------------------------
    # Identify timestamps of every pulse for every station
    #----------------------------------------------------------
    for n in range(4):
        if n==0: magdata,pulse = nuri1,nuri1_pulse
        if n==1: magdata,pulse = nuri2,nuri2_pulse
        if n==2: magdata,pulse = gnome1,gnome1_pulse
        if n==3: magdata,pulse = gnome2,gnome2_pulse
        #below = np.where(magdata[:,1]<pulse)[0]
        #above = np.where(pulse<=magdata[:,1])[0]
        #print len(above)
        #print 'a'
        #data = []
        #for i in above:
        #    if i-1 in below: data.append(magdata[i,0])
        ##data  = [magdata[i,0] for i in above if i-1 in below]
        #print 'b'
        flag,data = 0,[]
        for i in range(1,len(magdata)-1): 
            pulse_up   = magdata[i-1,1] < pulse <= magdata[i,1]
            pulse_down = magdata[i+1,1] < pulse <= magdata[i,1]
            if tmin < magdata[i,0] and flag==0 and pulse_up:
                data.append(magdata[i,0])
                flag = 1
            if tmin < magdata[i,0] and flag==1 and pulse_down:
                flag = 0
        if n==0: station1_pulse_nuri  = data
        if n==1: station2_pulse_nuri  = data
        if n==2: station1_pulse_gnome = data
        if n==3: station2_pulse_gnome = data
    #----------------------------------------------------------
    # Calculate pulse delay between for NURI and GNOME data
    #----------------------------------------------------------
    station1_diff_nuri  = station2_diff_nuri  = np.empty((0,2))
    station1_diff_gnome = station2_diff_gnome = np.empty((0,2))
    station1_delay      = station2_delay      = np.empty((0,2))
    imax = min(len(station1_pulse_nuri),len(station1_pulse_gnome),
               len(station2_pulse_nuri),len(station2_pulse_gnome))
    for i in range(1,imax):
        x = station1_pulse_nuri[i]-tmin
        y = station1_pulse_nuri[i]-station1_pulse_nuri[i-1]
        station1_diff_nuri = np.vstack((station1_diff_nuri,[x,y]))
        x = station1_pulse_gnome[i]-tmin
        y = station1_pulse_gnome[i]-station1_pulse_gnome[i-1]
        station1_diff_gnome = np.vstack((station1_diff_gnome,[x,y]))
        x = station1_pulse_nuri[i]-tmin
        y = station1_pulse_nuri[i]-station1_pulse_gnome[i]
        station1_delay = np.vstack((station1_delay,[x,y]))
        x = station2_pulse_nuri[i]-tmin
        y = station2_pulse_nuri[i]-station2_pulse_nuri[i-1]
        station2_diff_nuri = np.vstack((station2_diff_nuri,[x,y]))
        x = station2_pulse_gnome[i]-tmin
        y = station2_pulse_gnome[i]-station2_pulse_gnome[i-1]
        station2_diff_gnome = np.vstack((station2_diff_gnome,[x,y]))
        x = station2_pulse_nuri[i]-tmin
        y = station2_pulse_nuri[i]-station2_pulse_gnome[i]
        station2_delay = np.vstack((station2_delay,[x,y]))
    #----------------------------------------------------------
    # Create x axis time label
    #----------------------------------------------------------
    tbeg = datetime.fromtimestamp(tmin)
    tend = datetime.fromtimestamp(tmax)
    sbeg = tbeg.strftime('%Y-%m-%d %H:%M:%S.%f')
    send = tend.strftime('%Y-%m-%d %H:%M:%S.%f')
    label1 = 'UTC time from %s to %s [secs]'%(sbeg,send)
    label2 = '%s-%s.png'%(int(tmin),int(tmax))
    #----------------------------------------------------------
    # Histogram of pulse separation
    #----------------------------------------------------------
    diffs = [(station1_diff_nuri[:,1]-1)*1e6,
             (station1_diff_gnome[:,1]-1)*1e6,
             (station2_diff_nuri[:,1]-1)*1e6,
             (station2_diff_gnome[:,1]-1)*1e6]
    labels = ['NURI station 1','GNOME station 1',
              'NURI station 2','GNOME station 2']
    xmin = min([min(diffs[i]) for i in range(4)])
    xmax = max([max(diffs[i]) for i in range(4)])
    fig = figure(figsize=(12,6))
    fig.suptitle('Time separation between pulses\n%s'%label1,
                 fontsize=14, fontweight='bold')
    plt.subplots_adjust(left=0.1, right=0.95,
                        bottom=0.1, top=0.9,
                        hspace=0.1, wspace=0)
    ax = plt.subplot(111,xlim=[xmin,xmax])
    ax.hist(diffs,bins=100,stacked=True,fill=True,alpha=0.4,
            edgecolor="black",range=[xmin,xmax],align='left',
            label=labels)
    legend = ax.legend(loc='upper right')
    print(np.average(diffs[0]))
    print(np.average(diffs[1]))
    print(np.average(diffs[2]))
    print(np.average(diffs[3]))
    ax.set_xlabel('Pulse delay relative to 1 second [us]')
    ax.set_yscale('log', nonposy='clip')
    savefig('histogram_pulses.png')
    clf()
    #----------------------------------------------------------
    # Plot pulses separations and delay
    #----------------------------------------------------------
    fig = figure(figsize=(15,10))
    plt.subplots_adjust(left=0.08,right=0.95,
                        bottom=0.07,top=0.95,
                        hspace=0.1,wspace=0.15)
    # Plot NURI pulse difference
    ymin,ymax = min(station1_diff_nuri[:,1]), \
                max(station1_diff_nuri[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax1 = subplot(321,xlim=[0,tmax-tmin])
    ax1.scatter(station1_diff_nuri[:,0],
                station1_diff_nuri[:,1],
                lw=0,s=20,c='#4e73ae')
    ax1.set_ylabel('NURI Pulse separation [secs]')
    ax1.set_ylim([ymin,ymax])
    ax1.set_title('Station 1')
    plt.setp(ax1.get_xticklabels(),visible=False)
    # Plot GNOME pulse difference
    ymin,ymax = min(station1_diff_gnome[:,1]), \
                max(station1_diff_gnome[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax2 = subplot(323,sharex=ax1)
    ax2.scatter(station1_diff_gnome[:,0],
                station1_diff_gnome[:,1],
                lw=0,s=20,c='#4e73ae')
    ax2.set_ylim([ymin,ymax])
    ax2.set_ylabel('GNOME Pulse separation [secs]')
    plt.setp(ax2.get_xticklabels(),visible=False)
    # Plot NURI/GNOME pulse delay
    ymin,ymax = min(station1_delay[:,1]), \
                max(station1_delay[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax3 = subplot(325,sharex=ax1)
    ax3.scatter(station1_delay[:,0],
                station1_delay[:,1],
                lw=0,s=20,c='#4e73ae')
    ax3.set_ylim([ymin,ymax])
    ax3.set_ylabel('Pulse delay [secs]')
    ax3.set_xlabel(label1)
    # Plot NURI pulse difference
    ymin,ymax = min(station2_diff_nuri[:,1]), \
                max(station2_diff_nuri[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax4 = subplot(322,sharex=ax1)
    ax4.scatter(station2_diff_nuri[:,0],
                station2_diff_nuri[:,1],
                lw=0,s=20,c='#4e73ae')
    ax4.set_ylim([ymin,ymax])
    ax4.set_ylabel('NURI Pulse separation [secs]')
    ax4.set_title('Station 2')
    plt.setp(ax4.get_xticklabels(),visible=False)
    # Plot GNOME pulse difference
    ymin,ymax = min(station2_diff_gnome[:,1]), \
                max(station2_diff_gnome[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax5 = subplot(324,sharex=ax1)
    ax5.scatter(station2_diff_gnome[:,0],
                station2_diff_gnome[:,1],
                lw=0,s=20,c='#4e73ae')
    ax5.set_ylim([ymin,ymax])
    ax5.set_ylabel('GNOME Pulse separation [secs]')
    ax5.set_ylim(ymin,ymax)
    plt.setp(ax5.get_xticklabels(),visible=False)
    # Plot NURI/GNOME pulse delay
    ymin,ymax = min(station2_delay[:,1]), \
                max(station2_delay[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax6 = subplot(326,sharex=ax1)
    ax6.scatter(station2_delay[:,0],
                station2_delay[:,1],
                lw=0,s=20,c='#4e73ae')
    ax6.set_ylim([ymin,ymax])
    ax6.set_ylabel('Pulse delay [secs]')
    ax6.set_xlim([0,tmax-tmin])
    ax6.set_xlabel(label1)
    # Save figure
    plt.savefig('pulses.png')
    plt.close()
    #----------------------------------------------------------
    # Create time series movie
    #----------------------------------------------------------
    os.system('mkdir -p video')
    tstep = 1.0 #2*tdiff
    tdiff = 0.5 #1./60.*30 #0.5
    t0,t1 = tmin-tdiff,tmin+tdiff
    while t1<min(nuri1[-1,0],nuri2[-1,0],gnome1[-1,0],gnome2[-1,0]):
        tmid = (t0+t1)/2
        fig = figure(figsize=(15,10))
        plt.subplots_adjust(left=0.1, right=0.95,
                            bottom=0.1, top=0.95,
                            hspace=0.1, wspace=0)
        # NURI1 - Identify first and last indexes
        imin = abs(nuri1[:,0]-t0).argmin()-2
        imax = abs(nuri1[:,0]-t1).argmin()+2
        # NURI1 - Plot time series
        ax1 = subplot(411)
        ax1.plot((nuri1[imin:imax,0]-tmid)*1000.,nuri1[imin:imax,1])
        ax1.set_ylim(min(nuri1[:,1]),max(nuri1[:,1]))
        ax1.set_ylim(-5,10)
        ax1.set_ylabel('NURI 1 Magnetic Field [uT]')
        plt.setp(ax1.get_xticklabels(),visible=False)
        # NURI2 - Identify first and last indexes
        imin = abs(nuri2[:,0]-t0).argmin()-2
        imax = abs(nuri2[:,0]-t1).argmin()+2
        # NURI2 - Plot time series
        ax2 = subplot(412,sharex=ax1)
        ax2.plot((nuri2[imin:imax,0]-tmid)*1000.,nuri2[imin:imax,1])
        ax2.set_ylim(min(nuri2[:,1]),max(nuri2[:,1]))
        ax2.set_ylabel('NURI 2 Magnetic Field [uT]')
        plt.setp(ax2.get_xticklabels(),visible=False)
        # GNOME1 - Identify first and last indexes
        imin = abs(gnome1[:,0]-t0).argmin()-2
        imax = abs(gnome1[:,0]-t1).argmin()+2
        # GNOME1 - Plot time series
        ax3 = subplot(413,sharex=ax1)
        ax3.plot((gnome1[imin:imax,0]-tmid)*1000.,gnome1[imin:imax,1])
        ax3.set_ylim(min(gnome1[:,1]),max(gnome1[:,1]))
        ax3.set_ylabel('GNOME 1 Magnetic Field [uT]')
        plt.setp(ax3.get_xticklabels(),visible=False)
        # GNOME2 - Identify first and last indexes
        imin = abs(gnome2[:,0]-t0).argmin()-2
        imax = abs(gnome2[:,0]-t1).argmin()+2
        # GNOME2 - Plot time series
        ax4 = subplot(414,sharex=ax1)
        ax4.plot((gnome2[imin:imax,0]-tmid)*1000.,gnome2[imin:imax,1])
        ax4.set_ylim(min(gnome2[:,1]),max(gnome2[:,1]))
        ax4.set_ylabel('GNOME 2 Magnetic Field [uT]')
        # Set x axis limit and label
        ax4.set_xlim((t0-tmid)*1000.,(t1-tmid)*1000.) 
        date = datetime.fromtimestamp(tmid).strftime('%Y-%m-%d %H:%M:%S.%f')
        ax4.set_xlabel('Time series around %s UTC time [ms]'%(date))
        # Save and close figure
        plt.savefig('video/%s-%s.png'%(t0,t1))
        plt.close()
        t0 += tstep
        t1 += tstep
