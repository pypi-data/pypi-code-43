import sys,os,numpy,matplotlib,seaborn
import matplotlib.pyplot as plt
from .utils import getcoddam,getresults,getfitname

def curveplot(args):
    """
    Plot chi-square curves for real absorption systems.

    This operation will produce chi-square and da/a curves for every system
    that are selected. The slope range and other distortion details are
    retrieved from the distres table in CoDDAM so there is no need to define
    manually the parameters. The way the program works is to first loop over
    all the systems listed in CoDDAM and store the indexes of the targeted
    systems, then loop over each of those systems, retrieve the results and
    finally plot the results.

    Examples
    --------

    >>> alpha curve_real --instrument uves --chisq 1e-6 --mode single
    >>>                  --system J001602-001225/0.63630/UVES_squader
    """
    # Set up suitable lookup table
    database = getcoddam('distres',args.coddam)
    if args.instrument==None or args.mode==None:
        print('ERROR: Either --instrument or --mode is missing...')
        quit()
    # If curve not for specific system, save all results in file
    target = args.system
    if target==None:
        out = open('temp.dat','w')
    name = getfitname(args.instrument,args.mode,args.sample)
    # Identify indexes of systems from distortion table
    idxs = []
    for i in range(len(database)):
        cond0 = args.system in [None,database['system'][i]]
        cond1 = database['instrument'][i].lower()==args.instrument
        cond2 = database['whitmore'][i]=='yes' and '--whitmore' in sys.argv
        cond3 = database['whitmore'][i]=='no'  and '--whitmore' not in sys.argv
        cond4 = args.sample==None or args.sample in database['system'][i]
        if cond0 and cond1 and (cond2 or cond3) and cond4:
            idxs.append(i)
    # Initialize loop over all systems
    print('\nGet',args.mode,'distortion results for',len(idxs),'systems\n')
    systot = 0
    data  = numpy.empty((0,4))
    chisq = numpy.empty((0,7))
    model = numpy.empty((0,4))
    # Do loop over all targeted systems
    for i in idxs:
        # Define all specifications
        curvemode  = 'weight' if args.mode=='global' else 'individual'
        system     = database['system'][i]
        instrument = database['instrument'][i].lower()
        wminther   = float(database['thermal min_fit'][i])
        wmaxther   = float(database['thermal max_fit'][i])
        wminturb   = float(database['turbulent min_fit'][i])
        wmaxturb   = float(database['turbulent max_fit'][i])
        wminmom    = float(database['MoM min_fit'][i])
        wmaxmom    = float(database['MoM max_fit'][i])
        distmin    = float(database['min '+curvemode][i])
        distmax    = float(database['max '+curvemode][i])
        distsep    = float(database['step '+curvemode][i])
        model      = 'model-%.1f'%float(database['model '+curvemode][i])
        test       = 'v10_chisq%.E'%float(database['threshold '+curvemode][i])
        test       = test + '_all' if instrument=='uves' else test + '_slope'
        test       = test + '_step%.E'%distsep
        test       = test + '_prev' if '--previous' in sys.argv else test
        test       = test + '_jw' if '--whitmore' in sys.argv else test
        if distmin < distmax <= 0:
            distlist = numpy.arange(distmax,distmin-0.001,-distsep)
            distplot = sorted(distlist)
        elif distmax > distmin >= 0:
            distlist = numpy.arange(distmin,distmax+0.001,distsep)
            distplot = sorted(distlist)
        elif distmin < 0 < distmax:
            distlist = numpy.hstack((numpy.arange(0,distmax+0.001,distsep),numpy.arange(0,distmin-0.001,-distsep)))
            distplot = sorted(numpy.delete(distlist,0))
        fitres = getchisquare(args.path,system,model,test,distplot)
        # If curves to be produced for individual systems, plot curve and save results
        if args.mode=='single':
            print('\n{0:<10}\n{1:<7} | {2:<8}\n'.format(system,model,test))
            if target==None:
                out.write('{:<40}\t'.format(system))
                if len(fitres)!=len(distplot):
                    out.write('{:>10}\t'.format('-')*15+'\n')
            #if len(fitres)==len(distplot):
            loop = True if target==None else False
            curves(system,fitres,distmin,distmax,fit=args.fit,loop=loop)
        # If curve to be produced as a global weighted mean
        if args.mode=='global':
            cond1  = len(fitres)==len(distplot)
            cond2  = database['parabola weight'][i]=='good'
            if cond1 and cond2:
                systot += 1
                if len(chisq)==0:
                    chisq = fitres[:,[0,1,2,5,6,9,10]]
                else:
                    chisq[:,1:] += fitres[:,[1,2,5,6,9,10]]
            therslope = '-' if len(fitres[:,2])==0  else '%.2f'%numpy.mean(fitres[:,2])
            turbslope = '-' if len(fitres[:,6])==0  else '%.2f'%numpy.mean(fitres[:,6])
            momslope  = '-' if len(fitres[:,10])==0 else '%.2f'%numpy.mean(fitres[:,10])
            print('{0:>10}\t{1:>10}\t{2:>10}'.format(therslope,turbslope,momslope))
            curves(system,fitres,distmin,distmax,args.fit,loop)
        if args.mode=='model' and len(fitres)==len(distplot):
            for j in range(3):
                x    = fitres[:,0]
                y    = fitres[:,2+4*j]
                xfit = numpy.arange(-5,5,0.0001)
                yfit = fitparabola2(x,y,fitrange=xfit)
                if len(model)==0:
                    model = numpy.zeros((len(xfit),4),dtype=float)
                    model[:,0] = xfit
                model[:,j+1] += yfit
        if args.mode=='alpha' and len(fitres)>0:
            data = numpy.vstack((data,[database['redshift'][i],
                                       database['MoM alpha'][i],
                                       database['MoM error'][i],
                                       database['name'][i]]))
            if '--show' in sys.argv:
                print('{:>15}'.format(database['redshift'][i]),)
                print('{:>15}'.format(database['MoM alpha'][i]),)
                print('{:>15}'.format(database['MoM alpha'][i]),)
                print('{:>15}'.format(database['name'][i]))
    if target==None:
        out.close()
        os.system('mv temp.dat %s/results/curves/%s/%s.dat'%(home,instrument,name))
    if args.mode in ['global','model']:
        print('Total number of systems used:',systot)
        results = chisq if mode=='global' else model
        weight(args.mode)
    if args.mode=='alpha':
        print(data)

def getchisquare(fitdir,system,fitmodel,test,distplot,model=None,predicted=None):
    """
    Extract chi-square from results
    """
    if '--show' in sys.argv:
        print('\n{0:>7}{1:>12}{2:>12}{3:>12}{4:>12}{5:>12}{6:>12}{7:>12}{8:>12}{9:>12}{10:>12}{11:>12}{12:>12}\n'.format('dist','ther_ndf','therchisq','theralpha','thererror','turb_ndf','turbchisq','turbalpha','turberror','mom_ndf','momchisq','momalpha','momerror'))
    fitres   = numpy.empty((0,13))
    for i in distplot:
        strslope = '0.000' if round(i,3)==0 else str('%.3f'%i).replace('-','m') if '-' in str(i) else 'p'+str('%.3f'%i)
        distpath = fitdir+'/'+system+'/'+fitmodel+'/runs/'+test+'/'+strslope+'/'
        therfort = distpath+'/thermal/thermal.18'
        turbfort = distpath+'/turbulent/turbulent.18'
        quasar   = system.split('/')[0]
        zabs     = system.split('/')[1]
        sample   = system.split('/')[2]
        if os.path.exists(distpath):
            ther,turb,mom = getresults(therfort,turbfort)
            dist          = round(i,3)
            fitres        = numpy.vstack((fitres,[None]*13))
            fitres[-1,0]  = dist
            fitres[-1,1]  = ther.df
            fitres[-1,2]  = ther.chisq
            fitres[-1,3]  = ther.alpha
            fitres[-1,4]  = ther.error
            fitres[-1,5]  = turb.df
            fitres[-1,6]  = turb.chisq
            fitres[-1,7]  = turb.alpha
            fitres[-1,8]  = turb.error
            fitres[-1,9]  = mom.df
            fitres[-1,10] = mom.chisq
            fitres[-1,11] = mom.alpha
            fitres[-1,12] = mom.error
            if '-' not in fitres[-1]:
                if '--show' in sys.argv:
                    print('{:>7} '.format('%.3f'%dist),)
                    print('{:>10}'.format('%i'%ther.df),)
                    print('{:>11}'.format('%.4f'%ther.chisq),)
                    print('{:>11}'.format('%.4f'%ther.alpha),)
                    print('{:>11}'.format('%.4f'%ther.error),)
                    print('{:>11}'.format('%i'%turb.df),)
                    print('{:>11}'.format('%.4f'%turb.chisq),)
                    print('{:>11}'.format('%.4f'%turb.alpha),)
                    print('{:>11}'.format('%.4f'%turb.error),)
                    print('{:>11}'.format('%i'%mom.df),)
                    print('{:>11}'.format('%.4f'%mom.chisq),)
                    print('{:>11}'.format('%.4f'%mom.alpha),)
                    print('{:>11}'.format('%.4f'%mom.error))
                chisq = turb.chisq if model=='turb' else ther.chisq if model=='ther' else mom.chisq
                ndf   = turb.df    if model=='turb' else ther.df    if model=='ther' else mom.df
                alpha = turb.alpha if model=='turb' else ther.alpha if model=='ther' else mom.alpha
                error = turb.error if model=='turb' else ther.error if model=='ther' else mom.error
            else:
                fitres = numpy.delete(fitres,-1,0)
    if '--show' in sys.argv:
        print('\n')
    dist,x,yabs,y = [],[],[],[]
    if len(fitres)>0:
        dist = [round(i,3) for i in fitres[:,0]]
        yndf = fitres[:,1]
        yabs = fitres[:,2]
        yred = yabs/yndf
        #if predicted=='null':
        #    A = numpy.vander(dist,3)
        #    (coeffs, residuals, rank, sing_vals) = numpy.linalg.lstsq(A,yalp)
        #    f = numpy.poly1d(coeffs)
        #    x = numpy.arange(-0.5,0.5,0.0001)
        #    imid = abs(f(x)-min(f(x))).argmin()
        #    imid = abs(dist-x[imid]).argmin()
        #    minchisq = yalp[imid]
        #    y = [numpy.exp(-minchisq/2)*numpy.exp(-chisq/2.) for chisq in yalp]
        #    y = yalp
        #else:
        #    A = numpy.vander(dist,3)
        #    (coeffs, residuals, rank, sing_vals) = numpy.linalg.lstsq(A,yabs)
        #    f = numpy.poly1d(coeffs)
        #    x = numpy.arange(-0.5,0.5,0.0001)
        #    imid = abs(f(x)-min(f(x))).argmin()
        #    imid = abs(dist-x[imid]).argmin()     
        #    minchisq = yred[imid]
        #    #norm = 10**int(math.log10(numpy.exp(-minchisq/2)*numpy.exp(-minchisq/2.)))
        #    y = [numpy.exp(-minchisq/2)*numpy.exp(-chisq/2.) for chisq in yred]
        #    #y = yred
    dist     = dist
    yabs     = yabs
    fitres   = fitres
    return fitres
    
def curves(system,fitres,distmin,distmax,fit,loop=False):
    """
    Do scatter plot of both chi-square and da/a results versus distortion slope
    """
    degensys = ['J111113-080402/3.60770/UVES_squader',
                'J034943-381031/3.02470/HIRES_prochaska']
    # Initializing the figure        
    matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    plt.rc('font', size=2, family='sans-serif')
    plt.rc('axes', labelsize=10, linewidth=0.2)
    plt.rc('legend', fontsize=10, handlelength=10)
    plt.rc('xtick', labelsize=7)
    plt.rc('ytick', labelsize=7)
    plt.rc('lines', lw=0.2, mew=0.2)
    plt.rc('grid', linewidth=0.5)
    plt.style.use('seaborn')
    fig = plt.figure(figsize=(8,5))
    plt.subplots_adjust(left=0.05, right=0.97, bottom=0.05, top=0.95, hspace=0.2, wspace=0.2)
    model = ['Thermal','Turbulent','MoM']
    for j in range(len(model)):
        if loop:
            out.write('{0:>10}\t'.format('%.2f'%numpy.mean(fitres[:,2+4*j])))
        x     = fitres[:,0]
        y     = fitres[:,2+4*j]
        label = model[j]+' $\chi^2$'
        ax    = plt.subplot(2,3,1+j,xlim=[distmin,distmax])
        ax.errorbar(x,y,fmt='o',ms=4,markeredgecolor='none',ecolor='grey',alpha=0.7,color='black')
        ymin  = 0 if len(y)==0 else min(y)-1 if min(y)==max(y) else min(y)
        ymax  = 1 if len(y)==0 else max(y)+1 if min(y)==max(y) else max(y)
        if system not in degensys and fit in ['chisq','both']:
            fitparabola2(x,y,model=model[j])
        ax.set_ylim(ymin,ymax)
        y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
        ax.yaxis.set_major_formatter(y_formatter)
        t1 = ax.text((distmin+distmax)/2,ymax-0.1*(ymax-ymin),system,color='grey',ha='center',fontsize=6)
        t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
        ax.set_title(label,fontsize=10)
        if loop:
            slope = 'badwhit' if system in badwhit and '--whitmore' in sys.argv else \
                    'degenerate' if system in degensys else '%.4f'%slope
            error = 'badwhit' if system in badwhit and '--whitmore' in sys.argv else \
                    'degenerate' if system in degensys else '%.4f'%slope_error
            out.write('{0:>10}\t{1:>10}\t'.format(slope,error))
        x     = fitres[:,0]
        y     = fitres[:,3+4*j]
        yerr  = fitres[:,4+4*j]
        ymin  = 0 if len(y)==0 else min(y)-1 if min(y)==max(y) else min(y-yerr)
        ymax  = 1 if len(y)==0 else max(y)+1 if min(y)==max(y) else max(y+yerr)
        label = model[j]+r' $\Delta\alpha/\alpha$ $(10^{-5})$'
        ax    = plt.subplot(2,3,4+j,xlim=[distmin,distmax],ylim=[ymin,ymax])
        ax.errorbar(x,y,yerr=yerr,fmt='o',ms=4,markeredgecolor='none',ecolor='grey',alpha=0.7,color='black',lw=0.5)
        if system not in degensys and fit in ['alpha','both']:
            fitlinear(x,y,yerr,model=model[j])
        y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
        ax.yaxis.set_major_formatter(y_formatter)
        t1 = ax.text((distmin+distmax)/2,ymax-0.1*(ymax-ymin),system,color='grey',ha='center',fontsize=6)
        t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
        ax.set_title(label,fontsize=10)
        if loop:
            if system in badwhit and '--whitmore' in sys.argv:
                alpha = error = syst = 'badwhit'
            elif system in degensys:
                alpha = error = syst = 'degenerate'
            else:
                alpha = '%.4f'%alpha
                error = '%.4f'%alpha_stat
                syst  = '%.4f'%alpha_syst
            out.write('{0:>10}\t{1:>10}\t{2:>10}\t'.format(alpha,error,syst))
    if loop==True:
        out.write('\n')
    plt.savefig('chisq.pdf')
    plt.close(fig)

def weight(self):

    plt.rc('font', size=5, family='sans-serif')
    plt.rc('axes', labelsize=10, linewidth=0.2)
    plt.rc('legend', fontsize=10, handlelength=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)
    plt.rc('lines', lw=0.2, mew=0.2)
    plt.rc('grid', linewidth=0.2)
    fig = plt.figure(figsize=(5,8))
    plt.subplots_adjust(left=0.15, right=0.95, bottom=0.07, top=0.95, hspace=0.3, wspace=0)
    model = ['Thermal','Turbulent','MoM']
    for i in range(len(model)):
        if mode=='model':
            x      = results[:,0]
            y      = results[:,1+i]
            xmin   = -0.1
            xmax   = 0
            imin   = abs(x-xmin).argmin()
            imax   = abs(x-xmax).argmin()
            ymin   = min(y[imin:imax])
            ymax   = max(y[imin:imax])
            imid   = abs(y-min(y)).argmin()
            isig   = abs(y-(min(y)+1)).argmin()
            xmid   = x[imid]
            xsig   = abs(x[isig]-x[imid])
            xm1sig = xmid-xsig
            xp1sig = xmid+xsig
            print('Slope: {0:>8}+/-{1:<8}'.format('%.4f'%xmid,'%.4f'%xsig),)
            ax = plt.subplot(3,1,i+1)
            ax.plot(x,y,color='black',alpha=0.7,lw=2)
            axvline(x=xm1sig,ls='dotted',color='red',lw=1)
            axvline(x=xmid,ls='dashed',color='red',lw=1)
            axvline(x=xp1sig,ls='dotted',color='red',lw=1)
            t1 = text(0,ymax-0.17*(ymax-ymin),'$1\sigma$ : %.4f+/-%.4f'%(xmid,xsig),color='red',fontsize=6,ha='center')
            t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
        if mode=='global':
            x    = results[:,0]
            y    = results[:,2*(i+1)]
            xmin = distmin
            xmax = distmax
            ymin = min(y)
            ymax = max(y)
            #imin = abs(x+0.03).argmin()
            #imax = abs(x+0.14).argmin()
            A = numpy.vander(x[8:-1],3)
            (coeffs, residuals, rank, sing_vals) = numpy.linalg.lstsq(A,y[8:-1])
            f      = numpy.poly1d(coeffs)
            xfit   = numpy.arange(-50,50,0.0001)
            imid   = abs(f(xfit)-min(f(xfit))).argmin()
            isig   = abs(f(xfit)-(min(f(xfit))+1)).argmin()
            xmid   = xfit[imid]
            xsig   = abs(xfit[isig]-xfit[imid])
            xm1sig = xmid-xsig
            xp1sig = xmid+xsig
            print('Slope: {0:>8}+/-{1:<8}'.format('%.4f'%xmid,'%.4f'%xsig),)
            ax = plt.subplot(3,1,i+1)
            ax.scatter(x,y,color='black',alpha=0.7,lw=2)
            ax.plot(xfit,f(xfit),c='red',lw=1)
            axvline(x=xm1sig,ls='dotted',color='red',lw=1)
            axvline(x=xmid,ls='dashed',color='red',lw=1)
            axvline(x=xp1sig,ls='dotted',color='red',lw=1)
            t1 = text((xmin+xmax)/2,ymax-0.17*(ymax-ymin),'$1\sigma$ : %.4f+/-%.4f'%(xmid,xsig),color='red',fontsize=10,ha='center')
            t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
        if i==0 and '--whitmore' in sys.argv:
            plt.title('Simplistic model',fontsize=10)
        elif i==0:
            plt.title('Our model',fontsize=10)
        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymin,ymax)
        ax.axvline(x=0,color='black')
        #ax.set_title(model[i],color='red',fontsize=10)
        ax.set_xlabel('Applied distortion slope (in m/s/$\AA$)',fontsize=10)
        ax.set_ylabel(model[i]+' global absolute $\chi^2$',fontsize=10)
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter(useOffset=False))
    plt.savefig(name+'.pdf')
    plt.clf()
