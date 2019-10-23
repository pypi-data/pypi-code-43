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
def timing():
    
    rep = '%s_%s'%(setup.start,setup.end)
    os.system('mkdir -p %s'%rep)
    os.chdir(rep)
    #----------------------------------------------------------
    # Extract magnetic field data
    #----------------------------------------------------------
    # Get NURI data
    path = '/Users/vincent/ASTRO/data/NURI/timing/run%i/station2/'%setup.run
    nuri = magfield(setup.start,setup.end,rep=path)
    nuri_pulse = (max(nuri[:,1])+min(nuri[:,1]))/2.
    # Get GNOME data
    path = '/Users/vincent/ASTRO/data/GNOME/timing/'
    gnome = gnomedata('Berkeley02',setup.start,setup.end,rep=path)
    gnome_pulse = (max(gnome[:,1])+min(gnome[:,1]))/2.
    # Get start and ending timestamps
    if setup.sample==False or setup.rescale:
        tmin = max(nuri[0,0],gnome[0,0])
        tmax = min(nuri[-1,0],gnome[-1,0])
    else:
        start,tmin,end,tmax = time_edge(setup.start,setup.end)
    #----------------------------------------------------------
    # Identify timestamps of every pulse for every station
    #----------------------------------------------------------
    for n in range(2):
        if n==0: magdata,pulse = nuri,nuri_pulse
        if n==1: magdata,pulse = gnome,gnome_pulse
        flag,data = 0,[]
        for i in range(1,len(magdata)-1):
            pulse_up   = magdata[i-1,1] < pulse <= magdata[i,1]
            pulse_down = magdata[i+1,1] < pulse <= magdata[i,1]
            if tmin < magdata[i,0] and flag==0 and pulse_up:
                data.append(magdata[i,0])
                flag = 1
            if tmin < magdata[i,0] and flag==1 and pulse_down:
                flag = 0
        if n==0: pulses_nuri  = data
        if n==1: pulses_gnome = data
    #----------------------------------------------------------
    # Calculate pulse delay between for NURI and GNOME data
    #----------------------------------------------------------
    diff_nuri = diff_gnome = delay = np.empty((0,2))
    imax = min(len(pulses_nuri),len(pulses_gnome))
    for i in range(1,imax):
        x = pulses_nuri[i]-tmin
        y = pulses_nuri[i]-pulses_nuri[i-1]
        diff_nuri = np.vstack((diff_nuri,[x,y]))
        x = pulses_gnome[i]-tmin
        y = pulses_gnome[i]-pulses_gnome[i-1]
        diff_gnome = np.vstack((diff_gnome,[x,y]))
        x = pulses_nuri[i]-tmin
        y = pulses_nuri[i]-pulses_gnome[i]
        delay = np.vstack((delay,[x,y]))
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
    diffs  = [(diff_nuri[:,1]-1)*1e6,(diff_gnome[:,1]-1)*1e6]
    labels = ['NURI','GNOME']
    xmin   = min([min(diffs[i]) for i in range(2)])
    xmax   = max([max(diffs[i]) for i in range(2)])
    offset = (xmax-xmin)/10
    xmin   = xmin-offset
    xmax   = xmax+offset
    fig = figure(figsize=(12,6))
    fig.suptitle('Time separation between pulses\n%s'%label1,
                 fontsize=14, fontweight='bold')
    plt.subplots_adjust(left=0.1, right=0.95,
                        bottom=0.1, top=0.85,
                        hspace=0.1, wspace=0)
    ax = plt.subplot(111,xlim=[xmin,xmax])
    ax.hist(diffs,bins=50,fill=True,alpha=0.4,
            edgecolor="black",range=[xmin,xmax],align='left',label=labels)
    ax.legend(loc='center',bbox_to_anchor=[0.5,1.04],
              ncol=2)
    print(np.average(diffs[0]))
    print(np.average(diffs[1]))
    ax.set_xlabel('Pulse delay relative to 1 second [us]')
    ax.set_yscale('log')
    ax.set_ylim(ymin=0.1)
    savefig('histogram_pulses.png')
    clf()
    #----------------------------------------------------------
    # Plot pulses separations and delay
    #----------------------------------------------------------
    fig = figure(figsize=(15,10))
    plt.subplots_adjust(left=0.1,right=0.95,
                        bottom=0.05,top=0.97,
                        hspace=0.1,wspace=0)
    # Plot NURI pulse difference
    ymin,ymax = min(diff_nuri[:,1]),max(diff_nuri[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax1 = subplot(311,xlim=[0,tmax-tmin],ylim=[ymin,ymax])
    ax1.scatter(diff_nuri[:,0],diff_nuri[:,1],lw=0,s=20,c='#4e73ae')
    ax1.set_ylabel('NURI Pulse separation [secs]')
    plt.setp(ax1.get_xticklabels(),visible=False)
    # Plot GNOME pulse difference
    ymin,ymax = min(diff_gnome[:,1]),max(diff_gnome[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax2 = subplot(312,sharex=ax1,sharey=ax1)
    ax2.scatter(diff_gnome[:,0],diff_gnome[:,1],lw=0,s=20,c='#4e73ae')
    ax2.set_ylabel('GNOME Pulse separation [secs]')
    ax2.set_ylim([ymin,ymax])
    plt.setp(ax2.get_xticklabels(),visible=False)
    # Plot NURI/GNOME pulse delay
    ymin,ymax = min(delay[:,1]),max(delay[:,1])
    offset    = (ymax-ymin)/10
    ymin,ymax = ymin-offset,ymax+offset
    ax3 = subplot(313,sharex=ax1)
    ax3.scatter(delay[:,0],delay[:,1],lw=0,s=20,c='#4e73ae')
    ax3.set_ylabel('Pulse delay [secs]')
    ax3.set_xlim([0,tmax-tmin]) 
    ax3.set_ylim([ymin,ymax])
    ax3.set_xlabel(label1)
    # Save figure
    plt.savefig('pulses.png')
    plt.close()
    #----------------------------------------------------------
    # Create time series movie
    #----------------------------------------------------------
    os.system('mkdir -p video')
    tstep = 1. #2*tdiff
    t0,t1 = tmin-setup.tdiff,tmin+setup.tdiff
    while t1<min(nuri[-1,0],gnome[-1,0]):
        tmid = (t0+t1)/2
        fig = figure(figsize=(15,7))
        plt.subplots_adjust(left=0.08,right=0.95,
                            bottom=0.1,top=0.97,
                            hspace=0.1,wspace=0)
        # Identify first and last indexes in NURI data
        imin = abs(nuri[:,0]-t0).argmin()-2
        imax = abs(nuri[:,0]-t1).argmin()+2
        # Plot NURI time series
        ax1 = subplot(211)
        ax1.plot((nuri[imin:imax,0]-tmid)*1000.,nuri[imin:imax,1])
        ax1.set_ylim(min(nuri[:,1]),max(nuri[:,1]))
        ax1.set_ylabel('NURI Magnetic Field [uT]')
        plt.setp(ax1.get_xticklabels(),visible=False)
        # Identify first and last indexes in GNOME data
        imin = abs(gnome[:,0]-t0).argmin()-2
        imax = abs(gnome[:,0]-t1).argmin()+2
        # Plot GNOME time series
        ax2 = subplot(212,sharex=ax1)
        ax2.plot((gnome[imin:imax,0]-tmid)*1000.,gnome[imin:imax,1])
        ax2.set_ylim(min(gnome[:,1]),max(gnome[:,1]))
        ax2.set_ylabel('GNOME Magnetic Field [uT]')
        # Set x axis limit and label
        ax2.set_xlim((t0-tmid)*1000.,(t1-tmid)*1000.) 
        date = datetime.fromtimestamp(tmid).strftime('%Y-%m-%d %H:%M:%S.%f')
        ax2.set_xlabel('Time series around %s UTC time [ms]'%(date))
        # Save and close figure
        plt.savefig('video/%s-%s.png'%(t0,t1))
        plt.close()
        t0 += tstep
        t1 += tstep
