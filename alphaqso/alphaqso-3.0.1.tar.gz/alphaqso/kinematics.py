import matplotlib,os,sys,re,math,datetime,operator,random,ctypes,binascii
import numpy                         as np
import matplotlib                    as mpl
import matplotlib.dates              as mdates
import matplotlib.pyplot             as plt
from matplotlib.pyplot               import *
from pylab                           import *
from matplotlib                      import rc
from matplotlib._png                 import read_png
from matplotlib.offsetbox            import AnnotationBbox, OffsetImage
from mpl_toolkits.axes_grid1         import make_axes_locatable
from scipy                           import optimize,stats
from scipy.optimize                  import curve_fit
from matplotlib.backends.backend_pdf import PdfPages
from time                            import clock
from scipy.ndimage                   import gaussian_filter1d
import pandas                        as pd
import theano.tensor                 as t
from astropy.io                      import fits
from mpl_toolkits.basemap            import Basemap

def getmetals():
    data = np.empty((0,7),dtype=float)
    metals = np.array([['MgII' ,np.empty((0,1),dtype=str),np.empty((0,5),dtype=float)],
                       ['FeII' ,np.empty((0,1),dtype=str),np.empty((0,5),dtype=float)],
                       ['SiII' ,np.empty((0,1),dtype=str),np.empty((0,5),dtype=float)],
                       ['NiII' ,np.empty((0,1),dtype=str),np.empty((0,5),dtype=float)],
                       ['CrII' ,np.empty((0,1),dtype=str),np.empty((0,5),dtype=float)],
                       ['AlII' ,np.empty((0,1),dtype=str),np.empty((0,5),dtype=float)],
                       ['AlIII',np.empty((0,1),dtype=str),np.empty((0,5),dtype=float)],
                       ['MnII' ,np.empty((0,1),dtype=str),np.empty((0,5),dtype=float)]],dtype=object)
    for system in np.loadtxt(self.pathdata+'metallist.dat',dtype=str):
        self.quasar   = system.split('/')[0]
        self.zabs     = float(system.split('/')[1])
        self.sample   = system.split('/')[2]
        self.distpath = './pubsys/'+system+'/'
        if os.path.exists(self.distpath+'chunks/vpfit_chunk001.txt')==True:
            dv   = []
            k    = 0
            tied = 0
            flag = 0
            
            header = np.loadtxt(self.distpath+'header.dat',dtype=str,delimiter='\n')
            fort13 = np.loadtxt(self.distpath+'turbulent.13',dtype=str,delimiter='\n')
            for line in fort13:
                vals = line.split()
                flag = 1 if '*' in line and flag==0 else 2 if '*' in line and flag==1 else flag
                if len(vals)==0:
                    break
                if flag==1 and '*' not in line:
                    if 'external' not in header[k]:
                        trans = header[k].split()[0]
                        wmid  = self.atominfo(trans)[1]
                        dv.append(2*(float(vals[3])-float(vals[2]))/(float(vals[2])+float(vals[3]))*self.c)
                    k += 1
                if flag==2 and '*' not in line:
                    alpha = vals[4] if len(vals[0])==1 else vals[3]
                    zabs  = vals[3] if len(vals[0])==1 else vals[2]
                    zabs  = float(zabs[:-2]+re.compile(r'[^\d.-]+').sub('',zabs[-2:]))
                    tied  = tied + 1 if alpha[-1].islower()==True and abs(zabs-self.zabs)<0.003 else tied
                    ion   = vals[0]+vals[1] if len(vals[0])==1 else vals[0]
                    if ion in metals[:,0] and alpha[-1].isdigit()==False and abs(zabs-self.zabs)<0.003:
                        i = np.where(metals[:,0]==ion)[0][0]
                        if system not in metals[i,1]:
                            metals[i,1] = np.vstack((metals[i,1],[str(system)]))
                            metals[i,2] = np.vstack((metals[i,2],[1,0,self.zabs,0,0]))
                        else:
                            j = np.where(metals[i,1]==system)[0][0]
                            metals[i,2][j,0] += 1
                            
            os.system('ls '+self.distpath+'chunks/ > list')
            chunks = np.loadtxt('list',dtype=str)
            noise,ewidth = [],[]
            for n in range(len(chunks)):
                ion   = header[n].split()[0].split('_')[0]
                chunk = np.loadtxt(self.distpath+'chunks/'+chunks[n],comments='!')
                chunk = np.delete(chunk,np.where(chunk[:,2]==0)[0],0)
                width = sum([(1-chunk[i,-1])*(chunk[i+1,0]-chunk[i,0])/(self.zabs+1) for i in range(len(chunk)-1)])
                snr   = np.average(chunk[:,1]/chunk[:,2])
                if 'external' not in header[n] and ion in metals[:,0]:
                    i = np.where(metals[:,0]==ion)[0][0]
                    if system in metals[i,1]:
                        j = np.where(metals[i,1]==system)[0][0]
                        metals[i,2][j,1] += width
                        metals[i,2][j,3] += snr
                        metals[i,2][j,4] += 1.
                ewidth.append(width)
                noise.append(snr)
                
            for i in range(len(metals)):
                if system in metals[i,1]:
                    j = np.where(metals[i,1]==system)[0][0]
                    if metals[i,2][j,1]>0:
                        metals[i,2][j,1] = metals[i,2][j,1] / metals[i,2][j,4]
                        metals[i,2][j,4] = 1
                
            data = np.vstack((data,np.array([float(tied),
                                             np.mean(ewidth),
                                             np.std(ewidth),
                                             self.zabs,
                                             np.mean(noise),
                                             np.mean(dv),
                                             np.std(dv)],dtype=float)))
            
    os.system('rm list')
    
    ''' Bin data '''
    
    k = 1
    data = np.array(sorted(data,key=lambda col: col[3]))
    bindata = np.empty((0,7))
    for i in range(0,len(data),self.binning):
        ilim  = i+self.binning if i+self.binning<=len(data) else len(data)
        print '\nbin',k,'\n'
        for j in range(i,ilim):
            print 'z={0:<8}  |  {1:>5}  |  {2:>5} +/- {3:<6}  |  {4:<8}'.format('%.5f'%data[j,3],'%i'%data[j,0],'%.2f'%data[j,1],'%.2f'%data[j,2],'%.2f'%data[j,4])
        zabs  = np.average([float(data[j,3]) for j in range(i,ilim)])
        tied  = np.average([float(data[j,0]) for j in range(i,ilim)])
        snr   = np.average([float(data[j,4]) for j in range(i,ilim)])
        width = sum([float(data[j,1])/float(data[j,2])**2 for j in range(i,ilim)]) / sum([1/float(data[j,2])**2 for j in range(i,ilim)])
        error = 1 / np.sqrt(sum(1/float(data[j,2])**2 for j in range(i,ilim)))
        dv    = sum([float(data[j,5])/float(data[j,6])**2 for j in range(i,ilim)]) / sum([1/float(data[j,6])**2 for j in range(i,ilim)])
        dverr = 1 / np.sqrt(sum(1/float(data[j,6])**2 for j in range(i,ilim)))
        print '----------  |  -----  |  ----------------  |  --------'
        print 'z={0:<8}  |  {1:>5}  |  {2:>5} +/- {3:<6}  |  {4:<8}'.format('%.5f'%zabs,'%i'%tied,'%.2f'%width,'%.2f'%error,'%.2f'%snr)
        bindata   = np.vstack((bindata,[tied,width,error,zabs,snr,dv,dverr]))
        k += 1

    return bindata,metals

def isfloat(value):
    try:
      float(value)
      return True
    except ValueError:
      return False

#==================================================================================================================

def makeatomlist(atompath):     # Store data from atom.dat

    atom   = np.empty((0,6))
    atomdat     = np.loadtxt(atompath,dtype='str',delimiter='\n')
    for element in atomdat:
        l       = element.split()
        i       = 0      if len(l[0])>1 else 1
        species = l[0]   if len(l[0])>1 else l[0]+l[1]
        wave    = 0 if len(l)<i+2 else 0 if isfloat(l[i+1])==False else l[i+1]
        f       = 0 if len(l)<i+3 else 0 if isfloat(l[i+2])==False else l[i+2]
        gamma   = 0 if len(l)<i+4 else 0 if isfloat(l[i+3])==False else l[i+3]
        mass    = 0 if len(l)<i+5 else 0 if isfloat(l[i+4])==False else l[i+4]
        alpha   = 0 if len(l)<i+6 else 0 if isfloat(l[i+5])==False else l[i+5]
        if species not in ['>>','<<','<>','__']:
            atom = np.vstack((atom,[species,wave,f,gamma,mass,alpha]))
    return atom
            
#==================================================================================================================

def atominfo(atomID):     # Get atomic data from selected atomID

    target = [0,0,0,0,0]
    atomID = atomID.split('_')
    for i in range(len(self.atom)):
        element     = self.atom[i,0]
        wavelength  = self.atom[i,1]
        oscillator  = self.atom[i,2]
        gammavalue  = self.atom[i,3]
        qcoeff      = self.atom[i,5]
        if (len(atomID)>1 and element==atomID[0] and abs(float(wavelength)-float(atomID[1]))<abs(float(target[1])-float(atomID[1]))) \
           or (len(atomID)==1 and element==atomID[0]):
           target = [element,wavelength,oscillator,gammavalue,qcoeff] 
    if target==[0,0,0,0,0]:
        print atomID,'not identifiable...'
        quit()
    return target

#==================================================================================================================

def plotwidth():

    def func(x,a,b):
        return a + b*x
        
    bindata,metals = getmetals()


    ''' ----------------------------------------------------- '''
    ''' Plot Average Equivalent Width vs. Velocity Dispersion '''
    ''' ----------------------------------------------------- '''


    x    = bindata[:,5]
    xerr = bindata[:,6]
    y    = bindata[:,1]
    yerr = bindata[:,2]
    zabs = bindata[:,3]

    xmax = 1.1*max(x)
    ymax = 0.2#1.1*max(y)
    
    fig = figure(figsize=(7,6))
    plt.subplots_adjust(left=0.1, right=0.87, bottom=0.1, top=0.95, hspace=0, wspace=0)

    ax = subplot(111,xlim=[0,xmax],ylim=[0,ymax])
    ax.scatter(x,y,marker='o',s=50,edgecolors='none',zorder=3,\
            c=zabs,cmap=mpl.cm.cool,vmin=min(zabs),vmax=max(zabs))
    errorbar(x,y,yerr=yerr,fmt='o',ms=0,c='0.7',zorder=1)
    xlabel('Average velocity dispersion',fontsize=12)
    ylabel('Average equivalent width',fontsize=12)
    axhline(y=0,ls='dotted',color='black')
    axvline(x=0,ls='dotted',color='black')
    
    xfit = np.arange(0,xmax,0.01)
    coeffs,matcov = curve_fit(func,x,y)
    yfit = func(xfit,coeffs[0],coeffs[1])
    ax.plot(xfit,yfit,color='black',lw=3,ls='dotted',
            label=r'Unweighted fit: $%.6f \pm %.6f$ '%(coeffs[1],np.sqrt(matcov[1][1])))
    
    xfit = np.arange(0,xmax,0.01)
    coeffs,matcov = curve_fit(func,x,y,sigma=yerr)
    yfit = func(xfit,coeffs[0],coeffs[1])
    ax.plot(xfit,yfit,color='black',lw=3,ls='dashed',
            label=r'Weighted fit: $%.6f \pm %.6f$ '%(coeffs[1],np.sqrt(matcov[1][1])))
    
    leg = plt.legend(fancybox=True,loc=2,numpoints=1,handlelength=3,prop={'size':12})
    leg.get_frame().set_linewidth(0.1)
                
    ax1  = fig.add_axes([0.87,0.1,0.04,0.85])
    cmap = mpl.cm.cool
    norm = mpl.colors.Normalize(vmin=min(zabs),vmax=max(zabs))
    cb1  = mpl.colorbar.ColorbarBase(ax1,cmap=cmap,norm=norm)
    cb1.set_label('Absorption redshift',fontsize=12)
    
    savefig('equiwidth_vs_dispersion.pdf')
    clf()

    
    ''' ----------------------------------------------------------- '''
    ''' Plot Average Equivalent Width vs. Number of Tied Components '''
    ''' ----------------------------------------------------------- '''


    x    = bindata[:,0]
    y    = bindata[:,1]
    yerr = bindata[:,2]
    zabs = bindata[:,3]
    
    xmax = 1.1*max(x)
    ymax = 1.1*max(y)
    
    fig = figure(figsize=(7,6))
    plt.subplots_adjust(left=0.1, right=0.87, bottom=0.1, top=0.95, hspace=0, wspace=0)

    ax = subplot(111,xlim=[0,xmax],ylim=[0,ymax])
    ax.scatter(x,y,marker='o',s=50,edgecolors='none',zorder=3,\
            c=zabs,cmap=mpl.cm.cool,vmin=min(zabs),vmax=max(zabs))
    errorbar(x,y,yerr=yerr,fmt='o',ms=0,c='0.7',zorder=1)
    xlabel('Number of tied components',fontsize=12)
    ylabel('Average equivalent width',fontsize=12)
    axhline(y=0,ls='dotted',color='black')
    axvline(x=0,ls='dotted',color='black')
    
    xfit = np.arange(0,xmax,0.01)
    coeffs,matcov = curve_fit(func,x,y)
    yfit = func(xfit,coeffs[0],coeffs[1])
    ax.plot(xfit,yfit,color='black',lw=3,ls='dotted',
            label=r'Unweighted fit: $%.6f \pm %.6f$ '%(coeffs[1],np.sqrt(matcov[1][1])))
    
    xfit = np.arange(0,xmax,0.01)
    coeffs,matcov = curve_fit(func,x,y,sigma=yerr)
    yfit = func(xfit,coeffs[0],coeffs[1])
    ax.plot(xfit,yfit,color='black',lw=3,ls='dashed',
            label=r'Weighted fit: $%.6f \pm %.6f$ '%(coeffs[1],np.sqrt(matcov[1][1])))
    
    leg = plt.legend(fancybox=True,loc=2,numpoints=1,handlelength=3,prop={'size':12})
    leg.get_frame().set_linewidth(0.1)
                
    ax1  = fig.add_axes([0.87,0.1,0.04,0.85])
    cmap = mpl.cm.cool
    norm = mpl.colors.Normalize(vmin=min(zabs),vmax=max(zabs))
    cb1  = mpl.colorbar.ColorbarBase(ax1,cmap=cmap,norm=norm)
    cb1.set_label('Absorption redshift',fontsize=12)
    
    savefig('equiwidth_vs_tied.pdf')
    clf()

    
    ''' ------------------------------------------- '''
    ''' Plot Number of tied components vs. Redshift '''
    ''' ------------------------------------------- '''


    x    = bindata[:,3]
    y    = bindata[:,0]
    c    = bindata[:,4]
        
    xmax = 1.1*max(x)
    ymax = 1.1*max(y)
    
    fig = figure(figsize=(7,6))
    plt.subplots_adjust(left=0.1, right=0.87, bottom=0.1, top=0.95, hspace=0, wspace=0)
    
    ax = subplot(111,xlim=[0,xmax],ylim=[0,ymax])
    ax.scatter(x,y,marker='o',s=50,edgecolors='none',zorder=3,\
               c=c,cmap=mpl.cm.rainbow,vmin=min(c),vmax=max(c))
    xlabel('Absorption redshift',fontsize=12)
    ylabel('Number of tied components',fontsize=12)
    axhline(y=0,ls='dotted',color='black')
    axvline(x=0,ls='dotted',color='black')

    xfit = np.arange(0,xmax,0.01)
    coeffs,matcov = curve_fit(func,x,y)
    yfit = func(xfit,coeffs[0],coeffs[1])
    ax.plot(xfit,yfit,color='black',lw=3,ls='dashed',
            label=r'Unweighted fit: $%.6f \pm %.6f$ '%(coeffs[1],np.sqrt(matcov[1][1])))
    
    leg = plt.legend(fancybox=True,loc=2,numpoints=1,handlelength=3,prop={'size':12})
    leg.get_frame().set_linewidth(0.1)
                
    ax1  = fig.add_axes([0.87,0.1,0.04,0.85])
    cmap = mpl.cm.rainbow
    norm = mpl.colors.Normalize(vmin=min(c),vmax=max(c))
    cb1  = mpl.colorbar.ColorbarBase(ax1,cmap=cmap,norm=norm)
    cb1.set_label('Signal-to-Noise ratio',fontsize=12)
    
    savefig('tiedcomp_vs_redshift.pdf')
    clf()

    
    ''' ------------------------------------------ '''
    ''' Plot Average Equivalent Width vs. Redshift '''
    ''' ------------------------------------------ '''

    
    x    = bindata[:,3]
    y    = bindata[:,1]
    yerr = bindata[:,2]
    c    = bindata[:,4]
        
    xmax = 1.1*max(x)
    ymax = 1.1*max(y)
    
    fig = figure(figsize=(7,6))
    plt.subplots_adjust(left=0.1, right=0.87, bottom=0.1, top=0.95, hspace=0, wspace=0)
    
    ax = subplot(111,xlim=[0,xmax],ylim=[0,ymax])
    ax.scatter(x,y,marker='o',s=50,edgecolors='none',zorder=3,\
               c=c,cmap=mpl.cm.rainbow,vmin=min(c),vmax=max(c))
    errorbar(x,y,yerr=yerr,fmt='o',ms=0,c='0.7',zorder=1)
    xlabel('Absorption redshift',fontsize=12)
    ylabel('Average Equivalent Width',fontsize=12)
    axhline(y=0,ls='dotted',color='black')
    axvline(x=0,ls='dotted',color='black')

    xfit = np.arange(0,xmax,0.01)
    coeffs,matcov = curve_fit(func,x,y)
    yfit = func(xfit,coeffs[0],coeffs[1])
    ax.plot(xfit,yfit,color='black',lw=3,ls='dotted',
            label=r'Unweighted fit: $%.6f \pm %.6f$ '%(coeffs[1],np.sqrt(matcov[1][1])))
    
    xfit = np.arange(0,xmax,0.01)
    coeffs,matcov = curve_fit(func,x,y,sigma=yerr)
    yfit = func(xfit,coeffs[0],coeffs[1])
    ax.plot(xfit,yfit,color='black',lw=3,ls='dashed',
            label=r'Weighted fit: $%.6f \pm %.6f$ '%(coeffs[1],np.sqrt(matcov[1][1])))
    
    leg = plt.legend(fancybox=True,loc=2,numpoints=1,handlelength=3,prop={'size':12})
    leg.get_frame().set_linewidth(0.1)
                
    ax1  = fig.add_axes([0.87,0.1,0.04,0.85])
    cmap = mpl.cm.rainbow
    norm = mpl.colors.Normalize(vmin=min(c),vmax=max(c))
    cb1  = mpl.colorbar.ColorbarBase(ax1,cmap=cmap,norm=norm)
    cb1.set_label('Signal-to-Noise ratio',fontsize=12)
    
    savefig('equiwidth_vs_redshift.pdf')
    clf()


#==================================================================================================================

def plotwidthperion():

    def func(x,a,b):
        return a + b*x
        
    bindata,metals = getmetals()

    ''' ------------------------------------------- '''
    ''' Plot number of tied components vs. redshift '''
    ''' ------------------------------------------- '''

    
    fig = figure(figsize=(8,12))
    plt.subplots_adjust(left=0.07, right=0.93, bottom=0.05, top=0.93, hspace=0.3, wspace=0.1)
    fig.suptitle('Number of tied components vs. Absorption redshift',fontsize=15)

    for i in range(len(metals)):

        ion   = metals[i,0]
        data  = np.array(sorted(metals[i,2],key=lambda col: col[2]))
        bdata = np.empty((0,2))
        for j in range(0,len(data),self.binning):
            jlim  = j+self.binning if j+self.binning<=len(data) else len(data)
            zabs  = np.average([float(data[k,2]) for k in range(j,jlim)])
            tied  = np.average([float(data[k,0]) for k in range(j,jlim)])
            bdata = np.vstack((bdata,[zabs,tied]))
            
        ax = subplot(4,2,i+1,xlim=[0,max(bdata[:,0])],ylim=[0,max(bdata[:,1])])
        ax.scatter(bdata[:,0],bdata[:,1],marker='o',s=40,edgecolors='none',zorder=3,c='black',alpha=0.6)
        axhline(y=0,ls='dotted',color='black')
        axvline(x=0,ls='dotted',color='black')

        if len(bdata)>1:
            xfit = np.arange(0,max(bdata[:,0]),0.01)
            coeffs,matcov = curve_fit(func,bdata[:,0],bdata[:,1])
            yfit = func(xfit,coeffs[0],coeffs[1])
            ax.plot(xfit,yfit,color='red',lw=2,ls='dashed')
            self.linslopeval = coeffs[1]
            self.linslopeerr = np.sqrt(matcov[1][1])
            #print metals[i,0]+r': %.4f +/- %.4f'%(self.linslopeval,self.linslopeerr)

        plt.title(ion,fontsize=12,color='red')

        if (i+1)%2==0:
            ax.yaxis.tick_right()
            ax.yaxis.set_ticks_position('both')
                    
    savefig('tied_vs_redshift_per_ion.pdf')
    clf()

    
    ''' ----------------------------------------------------------- '''
    ''' Plot average equivalent width vs. number of tied components '''
    ''' ----------------------------------------------------------- '''

    
    fig = figure(figsize=(8,12))
    plt.subplots_adjust(left=0.07, right=0.93, bottom=0.05, top=0.93, hspace=0.3, wspace=0.1)
    fig.suptitle('Average Equivalent Width vs. Number of tied components',fontsize=15)

    for i in range(len(metals)):

        ion   = metals[i,0]
        data  = np.array(sorted(metals[i,2],key=lambda col: col[0]))
        bdata = np.empty((0,2))
        for j in range(0,len(data),self.binning):
            jlim  = j+self.binning if j+self.binning<=len(data) else len(data)
            tied  = np.average([float(data[k,0]) for k in range(j,jlim)])
            width = np.average([float(data[k,1]) for k in range(j,jlim)])
            bdata = np.vstack((bdata,[tied,width]))
            
        ax = subplot(4,2,i+1,xlim=[0,max(bdata[:,0])],ylim=[0,max(bdata[:,1])])
        ax.scatter(bdata[:,0],bdata[:,1],marker='o',s=40,edgecolors='none',zorder=3,c='black',alpha=0.6)
        axhline(y=0,ls='dotted',color='black')
        axvline(x=0,ls='dotted',color='black')

        if len(bdata)>1:
            xfit = np.arange(0,max(bdata[:,0]),0.01)
            coeffs,matcov = curve_fit(func,bdata[:,0],bdata[:,1])
            yfit = func(xfit,coeffs[0],coeffs[1])
            ax.plot(xfit,yfit,color='red',lw=2,ls='dashed')

        plt.title(ion,fontsize=12,color='red')

        if (i+1)%2==0:
            ax.yaxis.tick_right()
            ax.yaxis.set_ticks_position('both')
                    
    savefig('equiwidth_vs_tied_per_ion.pdf')
    clf()

    
    ''' ------------------------------------------ '''
    ''' Plot average equivalent width vs. redshift '''
    ''' ------------------------------------------ '''

    
    fig = figure(figsize=(8,12))
    plt.subplots_adjust(left=0.07, right=0.93, bottom=0.05, top=0.93, hspace=0.3, wspace=0.1)
    fig.suptitle('Average Equivalent Width vs. Absorption redshift',fontsize=15)

    for i in range(len(metals)):

        ion   = metals[i,0]
        data  = np.array(sorted(metals[i,2],key=lambda col: col[2]))
        bdata = np.empty((0,2))
        for j in range(0,len(data),self.binning):
            jlim  = j+self.binning if j+self.binning<=len(data) else len(data)
            zabs  = np.average([float(data[k,2]) for k in range(j,jlim)])
            width = np.average([float(data[k,1]) for k in range(j,jlim)])
            bdata = np.vstack((bdata,[zabs,width]))
            
        ax = subplot(4,2,i+1,xlim=[0,max(bdata[:,0])],ylim=[0,max(bdata[:,1])])
        ax.scatter(bdata[:,0],bdata[:,1],marker='o',s=40,edgecolors='none',zorder=3,c='black',alpha=0.6)
        axhline(y=0,ls='dotted',color='black')
        axvline(x=0,ls='dotted',color='black')
        
        if len(bdata)>1:
            xfit = np.arange(0,max(bdata[:,0]),0.01)
            coeffs,matcov = curve_fit(func,bdata[:,0],bdata[:,1])
            yfit = func(xfit,coeffs[0],coeffs[1])
            ax.plot(xfit,yfit,color='red',lw=2,ls='dashed')

        plt.title(ion,fontsize=12,color='red')

        if (i+1)%2==0:
            ax.yaxis.tick_right()
            ax.yaxis.set_ticks_position('both')
                    
    savefig('equiwidth_vs_redshift_per_ion.pdf')
    clf()

if __name__ == "__main__":

    rc('font', size=2, family='sans-serif')
    rc('axes', labelsize=8, linewidth=0.2)
    rc('legend', fontsize=2, handlelength=10)
    rc('xtick', labelsize=10)
    rc('ytick', labelsize=10)
    rc('lines', lw=0.2, mew=0.2)
    rc('grid', linewidth=0.2)
    home     = os.getenv('HOME')+'/ASTRO/analysis/alpha'
    here     = os.getenv('PWD')
    pathdata = os.path.abspath(__file__).rsplit('/',1)[0] + '/data/'
    done     = False
    c        = 299792.458
    atom     = makeatomlist(pathdata+'atom.dat')
    argument = np.array(sys.argv, dtype='str')
    binning  = 12 if '--bin' not in sys.argv else int(argument[np.where(argument=='--bin')[0][0]+1])
    plotwidth()
    plotwidthperion()
    
