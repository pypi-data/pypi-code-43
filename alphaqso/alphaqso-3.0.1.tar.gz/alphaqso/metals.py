import sys,os,re,numpy,operator
import matplotlib.pyplot as plt
import matplotlib as mpl
from .utils import getcoddam,env,atominfo

def getinfo(instrument,fitdir):
    """
    Store information regarding metals in multiple arrays.

    Notes
    -----
    This method doesn't take or return any arguments. Instead, the
    relevant information is extracted from and inserted in the setup
    object initialised in the settings method.

    The 4 data arrays that are stored in the setup object are the
    followings: infoatom, which store unique atomic data from all the
    transitions present in the selected sample; infosys, which contains
    the store the contrast for each system; infoleg, which store the
    minimum and maximum q-coefficient for each contrast, and infometal,
    which store all the atomic data for each system.
    """
    publist   = getcoddam('publist')
    curlist   = getcoddam('curlist')
    infoatom  = numpy.empty((0,6),dtype=object)  # List of all transitions used in sample [atomID,wavelength]
    infosys   = numpy.empty((0,4),dtype=object)  # List of absorption redshift and q variability [zabs,qvar]
    infoleg   = numpy.empty((0,3),dtype=object)  # List for legend in qvariability plot [qvar,qmin,qmax]
    infometal = numpy.empty((0,7),dtype=object)  # List of all metals used in sample [args.atom[index,:]+[zabs]]
    for system in publist['system']:
        qso    = system.split('/')[0]
        zabs   = float(system.split('/')[1])
        sample = system.split('/')[2]
        idx    = numpy.where(curlist['system']==system)[0][0]
        model  = curlist['jak12'][idx]
        if os.path.exists('%s/%s/model-%s/model/header.dat'%(fitdir,system,model))==False:
            pass
        elif (instrument==None or instrument.upper() in sample) and system not in env('outliers'):
            infohead = numpy.empty((0,7),dtype=object)
            line13 = numpy.loadtxt('%s/%s/model-%s/model/header.dat'%(fitdir,system,model),
                                   dtype='str',delimiter='\n')
            for k in range (len(line13)):
                if line13[k].split()[0][0]!='!' and 'external' not in line13[k].split():
                    atomID    = line13[k].split()[0]
                    component = atominfo(atomID)
                    infohead  = numpy.vstack((infohead ,component+[zabs,atomID]))
                    infometal = numpy.vstack((infometal,component+[zabs,atomID]))
                if atomID not in infoatom[:,-1]:
                    infoatom  = numpy.vstack((infoatom,component+[atomID]))
            qmin = min([float(k) for k in infohead[:,-3]])
            qmax = max([float(k) for k in infohead[:,-3]])
            qvar = abs(qmax-qmin)
            imin = numpy.where(infohead[:,-3]=='%i'%qmin)[0][0]
            imax = numpy.where(infohead[:,-3]=='%i'%qmax)[0][0]
            qmin = '%s%i'%(infohead[imin,0],float(infohead[imin,1]))
            qmax = '%s%i'%(infohead[imax,0],float(infohead[imax,1]))
            if qvar not in infoleg[:,0]:
                info = numpy.array([qvar,qmin,qmax],dtype=object)
                infoleg = numpy.vstack((infoleg,info))
            sys     = numpy.array([zabs,qvar,'',sample],dtype=object)
            infosys = numpy.vstack((infosys,sys))
    return numpy.array(sorted(infoatom,key=operator.itemgetter(1))),infosys,\
        numpy.array(sorted(infoleg,key=operator.itemgetter(0),reverse=True)),infometal

def plot_sample():
    """
    Plot redshift vs. rest-wavelength for every transitions
    """
    getinfo(instrument,fitdir)
    os.chdir(args.home+'/results/metals/')
    qcoeff  = numpy.array(args.infometal[:,-3],dtype=float)
    lamrest = numpy.array(args.infometal[:, 1],dtype=float)
    redabs  = numpy.array(args.infometal[:,-2],dtype=float)
    obswave = lamrest*(redabs+1)
    print('min / max observed wavelength: %.2f / %.2f'%(min(obswave),max(obswave)))
    fig = figure(figsize=(11.69,8.27))
    plt.subplots_adjust(left=0.07, right=0.87, bottom=0.1, top=0.95, hspace=0, wspace=0)
    ax = subplot(111)
    xlim(1300,3500)
    ylim(0,max(redabs)+1)
    ypos = max(redabs)+0.6
    for i in range (len(args.infoatom)):
        wave  = float(args.infoatom[i,1])
        trans = args.infoatom[i,-1].replace('_',' ')
        vlines(x=wave,ymin=-1,ymax=ypos,color='black',linestyles='dotted',zorder=3,lw=0.1)
        text(wave,ypos,trans,ha='left',fontsize=5)
        ypos -= 0.05
    scatter(lamrest,redabs,marker='o',s=10,edgecolors='none',zorder=3,\
            c=qcoeff,cmap=mpl.cm.cool,vmin=min(qcoeff),vmax=max(qcoeff))
    xlabel('Transition rest-frame wavelength',fontsize=12)
    ylabel('Redshift',fontsize=12)
    ax1  = fig.add_axes([0.87,0.1,0.04,0.85])
    cmap = mpl.cm.cool
    norm = mpl.colors.Normalize(vmin=min(qcoeff),vmax=max(qcoeff))
    cb1  = mpl.colorbar.ColorbarBase(ax1,cmap=cmap,norm=norm)
    cb1.set_label('q-coefficient',fontsize=12)
    name = 'metals_murphy' if instrument=='hires' else 'metals_king'
    savefig(name+'.pdf') if args.tbs else plt.show()
    plt.close(fig)

def qlist(instrument=None,fitdir='/Users/vincent/Documents/systems/',save_name=None):
    """
    Plot q-coefficient vs. rest-wavelength and frequency
    """
    infoatom,infosys,infoleg,infometal = getinfo(instrument,fitdir)
    qarray = numpy.empty((0,5),dtype=object)
    for i in range(len(infometal)):
        trans = infometal[i,-1]
        lrest = infometal[i, 1]
        qcoef = infometal[i,-3]
        zabs  = infometal[i,-2]
        if trans not in qarray[:,0]:
            qarray = numpy.vstack((qarray,[trans,lrest,qcoef,float(zabs),1]))
        else:
            idx = numpy.where(qarray[:,0]==trans)[0][0]
            qarray[idx,-2] = float(qarray[idx,-2]) + float(zabs)
            qarray[idx,-1] = int(qarray[idx,-1]) + 1
    x = numpy.array([i for i in qarray[:,1]],dtype=float)
    y = numpy.array([i for i in qarray[:,2]],dtype=float)
    n = numpy.array([i for i in qarray[:,4]],dtype=float)
    z = numpy.array([float(trans[3])/float(trans[4]) for trans in qarray],dtype=float)
    fig = plt.figure(figsize=(12,8))
    plt.style.use('seaborn')
    plt.subplots_adjust(left=0.08, right=0.88, bottom=0.1, top=0.87, hspace=0, wspace=0)
    ax1 = plt.subplot(111,xlim=[1300,3000],ylim=[-2000,3000])
    ax1.scatter(x,y,marker='o',s=40*n,edgecolors='none',alpha=0.6,c=z,
                cmap=mpl.cm.rainbow,vmin=min(z),vmax=max(z),zorder=2)
    plt.xlabel('rest-wavelength',fontsize=15)
    plt.ylabel('q-coefficient',fontsize=15)
    l1 = plt.scatter([],[], s=40*1, edgecolors='none')
    l2 = plt.scatter([],[], s=40*10, edgecolors='none')
    l3 = plt.scatter([],[], s=40*50, edgecolors='none')
    l4 = plt.scatter([],[], s=40*100, edgecolors='none')
    leg = plt.legend([l1,l2,l3,l4],["1","10","50","100"],ncol=4,frameon=False,fontsize=12,
                     handlelength=3, loc=8, borderpad = 0, fancybox=False,
                     bbox_to_anchor=[0.5,1.06],columnspacing=5,
                     handletextpad=1.5, scatterpoints = 1)
    for point in leg.legendHandles:
        point.set_color('#eaeaf2')
    ax1  = fig.add_axes([0.88,0.1,0.04,0.77])
    cmap = mpl.cm.rainbow
    vmin = 1.0 #min(z)
    vmax = 2.6 #max(z)
    norm = mpl.colors.Normalize(vmin=vmin,vmax=vmax)
    cb1  = mpl.colorbar.ColorbarBase(ax1,cmap=cmap,norm=norm)
    cb1.set_label('redshift',fontsize=15)
    name = 'qlist_murphy' if instrument=='hires' else 'qlist_king' if instrument=='uves' else 'qlist_all'
    plt.show() if save_name==None else plt.savefig(save_name)
    plt.close(fig)

def qvar():
    """
    Plot contrast against redshift for every absorber
    """
    getinfo(instrument,fitdir)
    os.chdir(args.home+'/results/metals/')
    fig = figure(figsize=(12,8))
    plt.subplots_adjust(left=0.07, right=0.95, bottom=0.1, top=0.95, hspace=0, wspace=0)
    xmax = 4.3
    ymax = max(args.infosys[:,1])+50
    qcoeff = args.infosys[:,1]
    ax1 = subplot(111,xlim=[0,xmax],ylim=[0,ymax])
    ax1.scatter(args.infosys[:,0],args.infosys[:,1],marker='o',s=50,edgecolors='none',
                alpha=0.8,c=qcoeff,cmap=mpl.cm.cool,vmin=min(qcoeff),vmax=max(qcoeff),zorder=2)
    ax1.yaxis.set_major_locator(plt.FixedLocator(numpy.arange(0,ymax,500)))
    xlabel('Redshift',fontsize=10)
    ylabel('q variability',fontsize=10)
    print(str(len(args.infosys)),'absorbers')
    for i in range (len(args.infoleg)):
        num  = len(numpy.where(args.infosys[:,1]==args.infoleg[i,0])[0])
        print('{:>5} : {:>10} - {:<10} : {:<5}'.format('%i'%args.infoleg[i,0],
                                                       args.infoleg[i,1],
                                                       args.infoleg[i,2],'%i'%num))
    divider = make_axes_locatable(ax1)
    ax2 = divider.append_axes("top",1.2,xlim=[0,xmax],pad='2%')
    ax2.hist(args.infosys[:,0],bins=100,histtype='stepfilled',color='r',alpha=0.5,lw=0.2)
    setp(ax2.get_xticklabels(), visible=False)
    name = 'qvar_murphy' if instrument=='hires' else 'qvar_king' if instrument=='uves' else 'qvar_all'
    savefig(name+'.pdf') if args.tbs else plt.show()
    plt.close(fig)
    
def mgfe(fitdir='/Users/vincent/Documents/systems/',save_name=None):
    '''
    Distribution of FeII and MgII transitions.
    '''
    publist = getcoddam('publist')
    plt.rc('font', size=2, family='sans-serif')
    plt.rc('axes', labelsize=8, linewidth=1)
    plt.rc('legend', fontsize=2, handlelength=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)
    plt.rc('lines', lw=1, mew=0.2)
    plt.rc('grid', linewidth=1)
    # List absorption systems to study
    mgii_ther = []
    mgii_turb = []
    feii_ther = []
    feii_turb = []
    for system in publist['system']:
        test = 'v10_chisq1E-06' if 'HIRES' in system else 'v10_chisq1E-06_all'
        distpath = fitdir+'/'+system+'/model-2.1/runs/'+test+'/0.000/'
        if system not in env('outliers') and os.path.exists(distpath+'thermal/thermal_fit.13'):
            therfortloc = distpath+'/thermal/thermal_fit.13'
            if os.path.exists(therfortloc)==True:
                i,flag  = 0,0
                fort = [line.replace('\n','') for line in open(therfortloc,'r')]
                while i < len(fort):
                    if '*' in fort[i]:
                        i,flag = i+1,flag+1
                    if flag==2:
                        coldens = re.compile(r'[^\d.-]+').sub('',fort[i].split()[1])
                        if fort[i].split()[0]=='MgII':
                            mgii_ther.append(float(coldens))
                        if fort[i].split()[0]=='FeII':
                            feii_ther.append(float(coldens))
                    i += 1
            turbfortloc = distpath+'/turbulent/turbulent_fit.13'
            if os.path.exists(turbfortloc)==True:
                i,flag  = 0,0
                fort = [line.replace('\n','') for line in open(turbfortloc,'r')]
                while i < len(fort):
                    if '*' in fort[i]:
                        i,flag = i+1,flag+1
                    if flag==2:
                        coldens = re.compile(r'[^\d.-]+').sub('',fort[i].split()[1])
                        if fort[i].split()[0]=='MgII':
                            mgii_turb.append(float(coldens))
                        if fort[i].split()[0]=='FeII':
                            feii_turb.append(float(coldens))
                    i += 1
    fig = plt.figure(figsize=(12,8),dpi=150)
    plt.style.use('seaborn')
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, hspace=0.15, wspace=0.2)
    ax = plt.subplot(2,2,1)
    n, bins, patches = ax.hist(feii_turb, 20, histtype='step', stacked=True, fill=True,alpha=0.5)
    ax.set_title('FeII turbulent',fontsize=10)
    ax = plt.subplot(2,2,2)
    n, bins, patches = ax.hist(feii_ther, 20, histtype='step', stacked=True, fill=True,alpha=0.5)
    ax.set_title('FeII thermal',fontsize=10)
    ax = plt.subplot(2,2,3)
    n, bins, patches = ax.hist(mgii_turb, 20, histtype='step', stacked=True, fill=True,alpha=0.5)
    ax.set_title('MgII turbulent',fontsize=10)
    ax = plt.subplot(2,2,4)
    n, bins, patches = ax.hist(mgii_ther, 20, histtype='step', stacked=True, fill=True,alpha=0.5)
    ax.set_title('MgII thermal',fontsize=10)
    plt.show() if save_name==None else plt.savefig(save_name)
    plt.close(fig)
