import os,sys,numpy,re,math,requests,io,csv
from pandas import read_csv
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def getcoddam(sheetname):

    sheet_id = {'qsolist':26063364,'dipole':1491749328,'curlist':175866280,'publist':353421904,'distres':684542576}
    key = '1Udpiat0e97ZwKuKQuN9peG9jtfLFrCVN4uVsbxHpDOg'
    url = "https://docs.google.com/spreadsheets/d/{0}/export?format=csv&gid={1}".format(key,sheet_id[sheetname])
    r = requests.get(url)
    sio = io.StringIO( r.text, newline=None)
    output = read_csv(sio,skiprows=1)
    return output

def getfitname(instrument,mode,sample):
    """
    Get fitting repository name
    """
    name = instrument + '-'
    name = name + 'v10_slope'  if instrument=='hires'        else name
    name = name + 'v10_all'    if instrument=='uves'         else name
    name = name + '_jw'        if '--whitmore' in sys.argv   else name
    name = name + '_prev'      if '--previous' in sys.argv   else name
    name = name + '-' + mode   if mode in ['global','model'] else name
    name = name + '-' + sample if sample!=None               else name
    return name

def vpfitset(vpversion,instrument,chisq):
    """
    VPFIT settings
    """
    pathdata   = os.path.dirname(os.path.realpath(__file__)) + '/data/'
    vpfitpath  = '/home/561/vxd561/ASTRO/code/vpfit10/' if '--raijin' in sys.argv else ''
    vpcommand  = vpfitpath + 'vpfit' + vpversion
    atomdir    = pathdata  + 'atom.dat'
    atomdir    = pathdata  + 'atom_new.dat'       if '--newatom'   in sys.argv else atomdir
    atomdir    = pathdata  + 'atom_murphy.dat'    if '--murphy'    in sys.argv else atomdir
    atomdir    = pathdata  + 'atom_mgisotope.dat' if '--mgisotope' in sys.argv else atomdir
    vpfsetup   = 'vp_setup_king.dat' if vpversion=='9.5-king' else 'vp_setup_hires.dat' if instrument=='hires' else 'vp_setup_uves.dat'
    vpfsetup   = numpy.loadtxt(pathdata+vpfsetup,dtype=str,delimiter='\n',comments='!')
    vpfsetup   = numpy.hstack((vpfsetup,['chisqthres %.E 2 %.E'%(chisq,chisq)])) if vpversion!='9.5-king' else vpfsetup
    return vpcommand,atomdir,vpfsetup

def isfloat(value):
    """
    Check if string is float.
    """
    try:
      float(value)
      return True
    except ValueError:
      return False

def storedata(fortpath,headpath):
    '''
    Read data from fort.13 and header files and store them in arrays.

    Parameters
    ----------
    fortpath : str
      Path to input fort.13 file
    headpath : str
      Path to input header.dat file
    '''
    read_head = numpy.loadtxt(headpath,dtype='str',delimiter='\n',ndmin=1)
    read_fort = open(fortpath,'r')
    read_fort = [line.strip() for line in read_fort]
    fort_header_old  = numpy.empty((0,8))
    fort_content_old = numpy.empty((0,8))
    i = flag = comp = twoq = 0
    while i < len(read_fort):
        if flag==2 and (read_fort[i]=='' or (read_fort[i].split()[0]=='>>' and read_fort[i].split()[-3]=='1')):
            break
        if read_fort[i]=='*':
            flag = flag+1
            i = offset = i + 1
        if flag==1 and read_fort[i][0]!='!':
            vals = read_fort[i].replace('!',' ').split()
            val0 = 'data/'+vals[0].replace('data/','').replace('../','')
            val1 = int(vals[1])
            val2 = '%.2f'%float(vals[2])
            val3 = '%.2f'%float(vals[3])
            val4 = vals[4].split('=')[0]+'='+str('%5.8f'%float(vals[4].split('=')[1]))
            val5 = read_head[i-offset].split()[0]
            val6 = '' if len(read_head[i-offset].split())==1 else read_head[i-offset].split()[1]
            val7 = '' if len(read_head[i-offset].split())==1 else read_head[i-offset].split()[2]
            fort_header_old = numpy.vstack((fort_header_old,[val0,val1,val2,val3,val4,val5,val6,val7]))
        if flag==2 and read_fort[i][0]!='!':
            vals = read_fort[i].split()
            val0 = vals[0]+' '+vals[1] if len(vals[0])==1 else vals[0]
            k = 1 if len(vals[0])==1 else 0
            val1 = '%.5f'%float(vals[k+1][:-2]+re.compile(r'[^\d.-]+').sub('',vals[k+1][-2:]))
            if '--colfix' in sys.argv:
                val1 = val1+'FF'
            else:
                val1 = val1+" ".join(re.findall("[a-zA-Z]+",vals[k+1][-2:]))
            zabs = float(vals[k+2][:-2]+re.compile(r'[^\d.-]+').sub('',vals[k+2][-2:]))
            val2 = '%.7f'%zabs
            val2 = val2+" ".join(re.findall("[a-zA-Z]+",vals[k+2][-2:]))
            val3 = '%.4f'%float(vals[k+3][:-2]+re.compile(r'[^\d.-]+').sub('',vals[k+3][-2:]))
            val3 = val3+" ".join(re.findall("[a-zA-Z]+",vals[k+3][-2:]))
            div  = 10**(-6) if 'E-0' in vals[k+4] else 1
            val4 = '0.000' if '*' in vals[k+4] else '%.3f'%(float(vals[k+4][:-2]+re.compile(r'[^\d.-]+').sub('',vals[k+4][-2:]))/div)
            val4 = val4+" ".join(re.findall("[a-zA-Z]+",vals[k+4][-2:]))
            twoq = 1 if vals[k+4][-2]=='q' and twoq==0 else twoq
            val5 = '%.2f'%float(vals[k+5][:-2]+re.compile(r'[^\d.-]+').sub('',vals[k+5][-2:]))
            val5 = val5+" ".join(re.findall("[a-zA-Z]+",vals[k+5][-2:]))
            val6 = '%.2E'%float(vals[k+6][:-2]+re.compile(r'[^\d.-]+').sub('',vals[k+6][-2:]))
            val6 = val6+" ".join(re.findall("[a-zA-Z]+",vals[k+6][-2:]))
            val7 = str(int(float(vals[k+7][:-2]+re.compile(r'[^\d.-]+').sub('',vals[k+7][-2:]))))
            val7 = val7+" ".join(re.findall("[a-zA-Z]+",vals[k+7][-2:]))
            fort_content_old = numpy.vstack((fort_content_old,[val0,val1,val2,val3,val4,val5,val6,val7]))
            comp = comp+1 if vals[0] not in ['H','>>','<<','<>','__','??'] else comp
        i = i + 1
    return fort_header_old,fort_content_old,comp,twoq

def prepare_model(model2fit,header,fort13,simulation):
    if '--finalmodel' in sys.argv:
        fort2fit = model+'_ini.26'
        # Create new fort.13 and header files
        write_header = open('header.dat','w')
        write_fort   = open(fort2fit,'w')
        os.system('rm '+model2fit+'_ini.13')
        for i in range (len(header)):
            datalength = [len(header[k,0]) for k in range (len(header))]
            datalength = "{0:<"+str(max(datalength))+"}"
            write_fort.write('%% ')
            write_fort.write(datalength.format(header[i,0])+' ')
            write_fort.write('{0:>5}'.format(header[i,1])+' ')
            write_fort.write('{0:>10}'.format('%.2f'%float(header[i,2]))+' ')
            write_fort.write('{0:>10}'.format('%.2f'%float(header[i,3]))+' ')
            write_fort.write('{0:<17}'.format(header[i,4])+' ! ')
            write_fort.write('{0:<15}'.format(header[i,5])+' ')
            write_header.write('{0:<15}'.format(header[i,5])+' ')
            if header[i,6]!='':
                write_fort.write('{0:<15}'.format(header[i,6])+' ')
                write_header.write('{0:<15}'.format(header[i,6])+' ')
                write_fort.write('{0:<15}'.format(header[i,7]))
                write_header.write('{0:<15}'.format(header[i,7]))
            write_header.write('\n')
            write_fort.write('\n')
        line26 = numpy.loadtxt(fitdir+system+'/original/'+model2fit+'.26',dtype='str',delimiter='\n')
        for i in range (len(line26)):
            if line26[i][0:2]!='%%':
                write_fort.write(line26[i]+'\n')
        write_header.close()
        write_fort.close()
    else:
        fort2fit = model2fit+'_ini.13'
        # Create new fort.13 and header files
        write_header = open('header.dat','w')
        write_fort   = open(fort2fit,'w')
        write_fort.write('   *\n')
        for i in range (len(header)):
            datalength = [len(header[k,0]) for k in range (len(header))]
            datalength = "{0:<"+str(max(datalength))+"}"
            write_fort.write(datalength.format(header[i,0])+' ')
            write_fort.write('{0:>5}'.format(header[i,1])+' ')
            write_fort.write('{0:>10}'.format('%.2f'%float(header[i,2]))+' ')
            write_fort.write('{0:>10}'.format('%.2f'%float(header[i,3]))+' ')
            write_fort.write('{0:<17}'.format(header[i,4])+' ! ')
            write_fort.write('{0:<15}'.format(header[i,5])+' ')
            write_header.write('{0:<15}'.format(header[i,5])+' ')
            if header[i,6]!='':
                write_fort.write('{0:<15}'.format(header[i,6])+' ')
                write_header.write('{0:<15}'.format(header[i,6])+' ')
                write_fort.write('{0:<15}'.format(header[i,7]))
                write_header.write('{0:<15}'.format(header[i,7]))
            write_header.write('\n')
            write_fort.write('\n')
        write_fort.write('  *\n')
        for i in range (len(fort13)):
            val = fort13[i]
            write_fort.write('   '+'{0:<5}'.format(val[0])+' ')
            write_fort.write('{0:>5}'.format(val[1].split('.')[0])+'.'+'{0:<7}'.format(val[1].split('.')[1])+' ')
            write_fort.write('{0:>3}'.format(val[2].split('.')[0])+'.'+'{0:<9}'.format(val[2].split('.')[1])+' ')
            write_fort.write('{0:>4}'.format(val[3].split('.')[0])+'.'+'{0:<6}'.format(val[3].split('.')[1])+' ')
            if simulation==None and '--noalpha' in sys.argv:
                write_fort.write('    0.000FF  ')
            else:
                write_fort.write('{0:>5}'.format(val[4].split('.')[0])+'.'+'{0:<6}'.format(val[4].split('.')[1])+' ')
            write_fort.write('{0:>5}'.format(val[5].split('.')[0])+'.'+'{0:<2}'.format(val[5].split('.')[1])+' ')
            if model2fit=='turbulent' and val[2][-1].islower():
                write_fort.write('  1.00E+00 ')
            else:
                write_fort.write('  0.00E+00 ')
            write_fort.write('{0:>2}'.format(val[7])+' ! ')
            write_fort.write('{0:>4}'.format(i+1))
            write_fort.write('\n')
        write_header.close()
        write_fort.close()

def gettestname(instrument=None,distsep=None,slope=0,chisq=1.E-5,vpversion='10',arm=None,shape='slope',
                previous=False,mgisotope=False,murphy=False,whitmore=False,simulation=False,newatom=False):
    '''
    Create distortion calculation test repository name.

    Parameters
    ----------
    instrument : str
      Spectrograph to be used
    distsep : float
      Step size value
    slope : float
      Middle or single slope value
    chisq : float
      Chi-square fitting value
    vpversion : str
      VPFIT version
    arm : str
      Spectrograph arm to select
    shape : str
      Shape of distortion model
    previous : bool
      Used previous slope results as first guesses
    mgisotope : bool
      Do non-terrestrial MgII isotope calculations
    murphy : bool
      Use original vp_setup.dat from Murphy from early 2000's
    whitmore : bool
      Use simplistic distortion model from Whitmore
    simulation : bool
      Do simulated distortion calculations
    newatom : bool
      Use new atomic data
    
    Return
    ------
    test : str
      Distortion calculation folder name
    '''
    test = 'v' + vpversion + '_chisq%.E'%chisq
    test = test+'_'+arm   if instrument=='uves'  and simulation==False        else test
    test = test+'_'+shape if instrument=='hires' and (slope!=0 or distsep!=0) else test
    test = test+'_step%.E'%distsep if distsep!=0                              else test
    test = test+'_prev'   if previous and (slope!=0 or distsep!=0)            else test
    test = test+'_jw'     if whitmore and (slope!=0 or distsep!=0)            else test
    test = test+'_null'   if simulation==False and noalpha                    else test
    test = test+'_new'    if newatom                                          else test
    test = test+'_murphy' if murphy                                           else test
    test = test+'_mg'     if mgisotope                                        else test
    return test
  
def vpfit_commands(nregs,fort='fort.13',action='d'):
    '''
    Generate list of commands to be run with VPFIT.

    Parameters
    ----------
    nregs : float
      Total number of regions.
    fort : str
      Input fort.13 file name
    action : str
      Action to be performed. Default is 'd' for display.
    '''
    opfile = open('fitcommands','w')
    opfile.write('%s\n'%action)         # Run display command + enter
    opfile.write('\n')              # ...used default setup -> enter only
    opfile.write('\n')                  # Used default selfeter (logN) -> enter only
    opfile.write('%s\n'%fort)           # Insert fort file name + enter
    opfile.write('\n')                  # Plot the fitting region (default is yes) -> enter only
    if nregs>1:                         # If more than one transitions...
        opfile.write('\n')              # ...select first transition to start with (default)
    opfile.write('as\n\n\n')
    for line in range(nregs):
        opfile.write('\n\n\n\n')
    if nregs>1:                         # If more than one transitions...
        opfile.write('\n')              # ...select first transition to start with (default)
    opfile.write('\n\nn\n\n')
    opfile.close()
  
def slopelist(slope,distmin,distmax,distsep):
    """
    Create array of slope values.
    
    slope : float
      Middle or single slope value
    distmin : float
      Minimum slope value
    distmax : float
      Maximum slope value
    distsep : float
      Step size value
    """
    distlist = distplot = [slope]
    if distmin < distmax <= slope:
        distlist = numpy.arange(distmax,distmin-0.001,-distsep)
        distplot = sorted(distlist)
    elif distmax > distmin >= slope:
        distlist = numpy.arange(distmin,distmax+0.001,distsep)
        distplot = sorted(distlist)
    elif distmin < slope < distmax:
        distlist = numpy.hstack((numpy.arange(slope,distmax+0.001,distsep),
                                   numpy.arange(slope,distmin-0.001,-distsep)))
        distplot = sorted(numpy.delete(distlist,0))
    return distlist,distplot

def make_atom_list(atompath):
    """
    Store data from atom.dat
    """
    atom   = numpy.empty((0,6))
    atomdat     = numpy.loadtxt(atompath,dtype='str',delimiter='\n')
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
            atom = numpy.vstack((atom,[species,wave,f,gamma,mass,alpha]))
    return atom

def atominfo(atomid):
    """
    Find transition in atom list and extract information.

    Parameters
    ----------
    atomid : string
      Name of the transition, written as ion_wavelength.
    """
    pathdata = os.path.dirname(os.path.realpath(__file__)) + '/data/'
    atom = make_atom_list(pathdata+'atom.dat')
    target = [0,0,0,0,0]
    atomid = atomid.split('_')
    for i in range(len(atom)):
        element     = atom[i,0]
        wavelength  = atom[i,1]
        oscillator  = atom[i,2]
        gammavalue  = atom[i,3]
        qcoeff      = atom[i,5]
        if (len(atomid)>1 and element==atomid[0] and abs(float(wavelength)-float(atomid[1]))<abs(float(target[1])-float(atomid[1]))) \
           or (len(atomid)==1 and element==atomid[0]):
           target = [element,wavelength,oscillator,gammavalue,qcoeff] 
    if target==[0,0,0,0,0]:
        print(atomid,'not identifiable...')
        quit()
    return target

def createfit13(model,simulation=False):
    """
    Create model_fit.13 after fitting model_ini.13 completed.

    Parameters
    ----------
    model : string
      Fitting model, either thermal or turbulent
    simulation : bool (False)
      Set if the model is based on a simulation
    """
    flag26 = flag18 = 0
    final = open(model+'_fit.13','w')
    final.write('   *\n')
    line26 = numpy.loadtxt('fort.26',dtype='str',delimiter='\n')
    for i in range(len(line26)):
        if 'Stats:' in line26[i]:
            flag26 = 1
        if line26[i][0:2]!='%%':
            break
        else:
            final.write(line26[i].replace('%% ','')+'\n')
    final.write('  *\n')
    line18 = numpy.loadtxt('fort.18',dtype='str',delimiter='\n')
    for i in range(len(line18)-1,0,-1):
        if 'statistics for whole fit:' in line18[i]:
            flag18 = 1
        if 'chi-squared' in line18[i]:
            chisq   = '%.4f'%float(line18[i].split('(')[1].split(',')[0])
            chisqnu = '%.3f'%float(line18[i].split('(')[0].split(':')[1])
            ndf     = '%.0f'%float(line18[i].split(')')[0].split(',')[1])
            if simulation==False:
                print('|  |  |  |  |- chisq='+chisq+', ndf='+ndf+', chisq_nu='+chisqnu)
            a = i + 2
            break
    for i in range(a,len(line18)):
        if len(line18[i])==1:
            break
        final.write(line18[i]+'\n')
    final.close()
    if '--raijin' in sys.argv and simulation==False:
        os.system('cp '+model+'_fit.13 ../')
    if flag26==1 and flag18==1 and simulation==False:
        os.system('mv fort.26 '+model+'.26')
        os.system('mv fort.18 '+model+'.18')
        
def dist2dip(qsoname):
    """
    Determine distance to dipole from specific quasar.

    Parameters
    ----------
    qsoname : string
      J2000 name of the quasar object
    
    Returns
    -------
    zem : float
      Emission redshift of the quasar
    ra : float
      Right Ascension
    dec : float
      Declinaison
    distance : float
      Distance to dipole from quasar object
    """
    idx = numpy.where(qsolist['name']==qsoname)[0][0]
    val = qsolist['RA\n(hh:mm:ss)'][idx].split(':')
    ra  = float(val[0])+float(val[1])/60+float(val[2])/3600         # in hours
    val = qsolist['DEC\n(dd:mm:ss)'][idx].split(':')
    if (val[0][0]=='-'):
        dec = float(val[0])-float(val[1])/60-float(val[2])/3600     # in degrees
    else:
        dec = float(val[0])+float(val[1])/60+float(val[2])/3600     # in degrees
    zem  = float(qsolist['z_em'][idx])
    # Dot product using spherical coordinates phi and theta in radians
    xdipole  = alphara*360/24.    # in degrees
    ydipole  = alphadec           # in degrees
    distance = spheredist(ra*360/24.,dec,xdipole,ydipole)
    return zem,ra,dec,distance

def fitparabola(x,y):
    """
    Fit parabola.
    """
    A      = numpy.vander(x,3)
    (coeffs, residuals, rank, sing_vals) = numpy.linalg.lstsq(A,y)
    f      = numpy.poly1d(coeffs)
    xfit   = numpy.arange(min(x),max(x),0.001)
    yfit   = f(xfit)
    imid   = abs(yfit-min(yfit)).argmin()
    xmid   = round(xfit[imid],7)
    fmin   = f(xfit[0:imid])
    fmax   = f(xfit[imid:-1])
    xm1sig = round(xfit[abs(fmin-(min(yfit)+1)).argmin()],3) if len(fmin)>0 and max(fmin)>min(yfit)+1 else 0
    xp1sig = round(xfit[imid+abs(fmax-(min(yfit)+1)).argmin()],3) if len(fmax)>0 and max(fmax)>min(yfit)+1 else 0
    print('Best Distortion Slope: %.4f+/-%.4f'%(xmid,abs(max(xm1sig,xp1sig)-xmid)))
    return xfit,yfit,xmid,xm1sig,xp1sig

def fitparabola2(x,y,fitrange=[],model=None,show=True,xmin=None,xmax=None):
    """
    Fit parabola to the chi-square curves.

    Parameters
    ----------
    x : numpy.array
      List of slope value
    y : numpy.array
      List of absolute chi-square values
    fitrange : list

    Returns
    -------
    slope : float
      Fitted best slope value
    sigma : float
      One sigma error value
    """
    ymin = 0 if len(y)==0 else min(y)-1 if min(y)==max(y) else min(y)
    ymax = 1 if len(y)==0 else max(y)+1 if min(y)==max(y) else max(y)
    imin,imax = 0,len(x)
    xmin = min(x) if xmin==None else xmin
    xmax = max(x) if xmax==None else xmax
    imin = numpy.where(x>xmin)[0][0]
    imax = numpy.where(x<xmax)[0][-1]
    A = numpy.vander(x[imin:imax],3)
    (coeffs, residuals, rank, sing_vals) = numpy.linalg.lstsq(A,y[imin:imax])
    f = numpy.poly1d(coeffs)
    x,y = x[imin:imax],y[imin:imax]
    #residuals = '%.7f'%residuals[0]
    #residuals = sum([(y[i]-f(x)[i])**2/f(x)[i] for i in range(len(x))])
    if len(fitrange)!=0:
        return f(fitrange)
    else:
        # Create high resolution slope array
        xfit = numpy.arange(-100,100,0.0001)
        # Slope index and value of minimum absolute chi-square
        imid = abs(f(xfit)-min(f(xfit))).argmin()
        xmid = xfit[imid]
        # Slope index and value of minimum absolute chi-square + 1
        isig = abs(f(xfit)-(min(f(xfit))+1)).argmin()
        xsig = xfit[isig]
        # Calculate +1 sigma slope value
        slope = xmid
        sigma = abs(xsig-xmid)
        # Plot high resolution slope array with fitted parabola
        plt.plot(xfit,f(xfit),c='red',lw=1)
        print('Slope: {0:>8}+/-{1:<8}'.format('%.4f'%slope,'%.4f'%sigma))
        #print('Chisq: {0:>12}'.format(residuals))
        plt.axvline(x=slope-sigma,ls='dotted',color='blue',lw=1)
        plt.axvline(x=slope,ls='dashed',color='red',lw=1)
        plt.axvline(x=slope+sigma,ls='dotted',color='blue',lw=1)
        if show==True:
            t1 = plt.text((distmin+distmax)/2,ymax-0.17*(ymax-ymin),r'$1\sigma$ : %.4f $\pm$ %.4f'%(slope,sigma),color='red',fontsize=6,ha='center')
            t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
        ymin = min(f(xfit))
        ymax = max(f(xfit))
    return slope,sigma

def fitlinear(x,y,yerr=[],slope=None,sigma=None,fitrange=[],model=None,show=True,xmin=None,xmax=None):
    """
    Do linear fit to da/a vs. distortion slope curves.
    """
    ymin = 0 if len(y)==0 else min(y)-1 if min(y)==max(y) else min(y-yerr)
    ymax = 1 if len(y)==0 else max(y)+1 if min(y)==max(y) else max(y+yerr)
    xfit = numpy.arange(-100,100,0.001)
    imin,imax = 0,len(x)
    xmin = min(x) if xmin==None else xmin
    xmax = max(x) if xmax==None else xmax
    imin = numpy.where(x>xmin)[0][0]
    imax = numpy.where(x<xmax)[0][-1]
    x,y,yerr = numpy.array(x[imin:imax],dtype=float),numpy.array(y[imin:imax],dtype=float),numpy.array(yerr[imin:imax],dtype=float)
    if yerr!=[]:
        def func(func,a,b):
            return a + b*x
        pars,cov = curve_fit(func,x,y,sigma=yerr)
        linslopeval = pars[1]
        linslopeerr = numpy.sqrt(cov[1][1])
        yfit = pars[0] + pars[1]*xfit
        if len(fitrange)!=0:
            return pars[0] + pars[1] * fitrange
        else:
            xfit,yfit = xfit,yfit
            plt.plot(xfit,yfit,color='red',lw=1)
            imid = abs(xfit-slope).argmin()
            imin = abs(xfit-(slope-sigma)).argmin()
            imax = abs(xfit-(slope+sigma)).argmin()
            plt.axvline(x=slope-sigma,ls='dotted',color='blue',lw=0.5)
            plt.axvline(x=xfit[imid],ls='dashed',color='red',lw=1)
            plt.axvline(x=slope+sigma,ls='dotted',color='blue',lw=0.5)
            plt.axhline(y=yfit[imid],ls='dashed',color='red',lw=1)
            plt.axhline(y=yfit[imax],ls='dotted',color='blue',lw=0.5)
            plt.axhline(y=yfit[imin],ls='dotted',color='blue',lw=0.5)
            alpha      = yfit[imid]
            alpha_stat = numpy.average(yerr)
            alpha_syst = abs(yfit[imax]-yfit[imid])
            if show==True:
                t1 = plt.text((distmin+distmax)/2,
                              ymax-0.17*(ymax-ymin),
                              r'$\Delta\alpha/\alpha$ = %.4f $\pm$ %.4f $\pm$ %.4f'%(yfit[imid],alpha_stat,alpha_syst),
                              color='red',fontsize=6,ha='center')
                t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
            print('Alpha: {0:>8}+/-{1:<6}+/-{2:<6}'.format('%.4f'%alpha,
                                                           '%.4f'%alpha_stat,
                                                           '%.4f'%alpha_syst))
    else:
        a,b = polyfit(x,y,1)

def getresults(therfort=None,turbfort=None,original=False):
    """
    Extract thermal and turbulent results and calculate
    weighted results using method-of-moments estimator.
    """
    chisq=alpha=error=df='-'
    ther = readfort18(therfort)
    turb = readfort18(turbfort)
    if turb.chisq!='-' and ther.chisq!='-':
        k         = ther.n - ther.df
        ther_AICc = ther.chisq + 2*k + 2*k*(k+1)/(ther.n-k-1)
        k         = turb.n - turb.df
        turb_AICc = turb.chisq + 2*k + 2*k*(k+1)/(turb.n-k-1)
        csmin     = min([ther_AICc,turb_AICc])
        k1        = math.exp(-(ther_AICc-csmin)/2)
        k2        = math.exp(-(turb_AICc-csmin)/2)
        k         = k1 + k2
        k1        = k1/k
        k2        = k2/k
        df        = k1 * ther.df    + k2 * turb.df
        chisq     = k1 * ther.chisq + k2 * turb.chisq
        alpha     = k1 * ther.alpha + k2 * turb.alpha
        error     = numpy.sqrt(k1*ther.error**2 + \
                               k2*turb.error**2 + \
                               k1*ther.alpha**2 + \
                               k2*turb.alpha**2 - \
                               alpha**2)
    # Create object and include results
    mom = type('mom', (object,), {})()
    mom.chisq=chisq
    mom.alpha=alpha
    mom.error=error
    mom.df=df
    return ther,turb,mom

def getshift(qso,sample,left,right,slope,shape,whitmore=False,stdev=0):
    """
    Calculate velocity shift do to distortion depending on model used.

    Parameters
    ----------
    qso : str
      Quasar name.
    sample : str
      Data sample.
    left : float
      Minimum wavelength of the fitting region
    right : float
      Maximum wavelength of the fitting region
    slope : float
      Slope of the long-range distortion model
    whitmore : bool
      Flag to do simplistic Whitmore distortion model
    stdev : float
      Standard deviation if random slope used

    Returns
    -------
    shift : float
      Velocity shift due to long-range distortion effect.
    """
    keck = ['HIRES_churchill','HIRES_sargent','HIRES_prochaska','HIRES_outram']
    vlt  = ['UVES_squader']
    def uves_slope(cent,x,slope):
        return slope*(x-cent)
    def uves_whitmore(x,slope):
        if x < 3259.1:
            return slope*(3259.1-3900)
        if 3259.1 < x < 4518.8:
            return slope*(x-3900)
        if 4518.8 < x < 4726.9:
            y1 = -slope*3900 + slope*4518.8
            y2 = -slope*5800 + slope*4726.9
            a  = (y2-y1)/(4726.9-4518.8)
            b  = 4518.8 - y1/a
            return a*(x-b)
        if 4726.9 < x < 6834.9:
            return slope*(x-5800)
        if x > 6834.9:
            return slope*(6834.9-5800)
    def hires_amplitude(left,right,amplitude):
        middle = (left+right)/2
        x0,x1  = 3800.,5300.
        if middle<x0:
            return amplitude
        if x0<middle<x1:
            return amplitude * (numpy.cos((middle-x0)*numpy.pi/(x1-x0)))**2
        if x1<middle:
            return amplitude
    def hires_slope(x,slope):
        return slope*(x-5500.)
    
    middle = (left+right)/2
    shift = blflag = rdflag = 0
    # If data sample of the selected system is a UVES system
    if sample in vlt:
        # If Whitmore distortion model and non-zero slope
        if whitmore and slope!=0:
            # Calculate the shift based on the Whitmore model
            shift = uves_whitmore(middle,slope)
        # If selected system is using UVES SQUADER data
        elif sample=='UVES_squader':
            # Search position of the quasar in the list of UVES exposures (uvesexp)
            pos = numpy.where(uvesexp['name']==qso)[0][0]
            # Initialize total shift and exposure time parameter
            sumshift = sumcount = 0
            # Loop in the list of UVES exposures until break is called
            for l in range (pos,len(uvesexp)):
                # If quasar name in list different from the selected system
                if uvesexp['name'][l]!=qso:
                    # Break the loop
                    break
                # For each exposure, loop over all the existing settings
                for k in range(len(uvesset)):
                    # Condition 1: Central wavelength of setting same than the exposure
                    cond1 = uvesset['cent'][k]==uvesexp['cent'][l]
                    # Condition 2: Optical arm of setting same than the exposure
                    cond2 = uvesset['arm'][k]==uvesexp['arm'][l]
                    # Condition 3: Optical mode of setting same than the exposure
                    cond3 = uvesset['mode'][k]==uvesexp['mode'][l]
                    # If the 3 conditions are satisfied
                    if cond1==cond2==cond3==True:
                        # Define starting wavelength (in Angstrom) from value in the list of settings (in nm)
                        wbeg  = 10*float(uvesset['TS_min'][k])
                        # Define central wavelength (in Angstrom) from value in the list of settings (in nm)
                        cent  = 10*float(uvesset['cent'][k])
                        # Define ending wavelength (in Angstrom) from value in the list of settings (in nm)
                        wend  = 10*float(uvesset['TS_max'][k])
                        # Break the loop in the list of settings as the correct setting has been matched
                        break
                # If creating simulated spectrum and expind option used, define a random slope based on exposure settings
                if stdev!=0:
                    # If no slope already attributed or exposure not yet tabulated in shifts
                    if len(shifts)==0 or str(uvesexp['dataset'][l]) not in shifts[:,0]:
                        # Determine slope for this exposure using gaussian distribution
                        slope = numpy.random.normal(slope,stdev)
                        # Store the exposure name and associated slope value calculated in shifts
                        shifts = numpy.vstack((shifts,[str(uvesexp['dataset'][l]),str(slope)]))
                    # If exposure already tabulated in shifts
                    if len(shifts)>0 and str(uvesexp['dataset'][l]) in shifts[:,0]:
                        # Find index position of this exposure in shifts
                        idx   = numpy.where(shifts[:,0]==uvesexp['dataset'][l])[0][0]
                        # Extract previously calculated and stored slope value for this exposure
                        slope = float(shifts[idx,1])
                if uvesexp['arm'][l]=='BLUE' and wbeg < left and right < wend:
                    sumshift = sumshift + numpy.sqrt(float(uvesexp['exptime'][l])) * uves_slope(cent,middle,slope)
                    sumcount = sumcount + numpy.sqrt(float(uvesexp['exptime'][l]))
                    blflag = 1
                if uvesexp['arm'][l]=='RED' and wbeg < left and right < wend:
                    sumshift = sumshift + numpy.sqrt(float(uvesexp['exptime'][l])) * uves_slope(cent,middle,slope)
                    sumcount = sumcount + numpy.sqrt(float(uvesexp['exptime'][l]))
                    rdflag = 1
            shift = sumshift / sumcount
            #regtotal = regtotal + 1
            #if blflag==1 and rdflag==0:
            #    armflag = 'blue'
            #    regblue = regblue + 1
            #if blflag==0 and rdflag==1:
            #    armflag = 'red'
            #    regred = regred + 1
            #if blflag==rdflag==1:
            #    armflag = 'overlap'
            #    regboth = regboth + 1
    if sample in keck:
        if slope==0:
            shift = 0
        elif whitmore and shape=='amplitude':
            shift = shift + hires_amplitude(left,right,slope)
        elif whitmore and shape=='slope':
            shift = shift + hires_slope(middle,slope)
        elif sample=='HIRES_sargent':
            pos = numpy.where(numpy.logical_and(hiresexp['name']==qso,hiresexp['sample']==sample))[0][0]
            sumshift = sumcount = 0
            for l in range (pos,len(hiresexp)):
                if hiresexp['name'][l]!=qso:
                    break
                wbeg = float(hiresexp['blue'][l])
                cent = float(hiresexp['cent'][l])
                wend = float(hiresexp['red'][l])
                if wbeg < left and right < wend:
                    sumshift = sumshift + numpy.sqrt(float(hiresexp['exptime'][l])) * uves_slope(cent,middle,slope)
                    sumcount = sumcount + numpy.sqrt(float(hiresexp['exptime'][l]))
            shift = sumshift / sumcount
    return '{0:.4f}'.format(float(shift)/1000.)

def readfort26(fortpath,daoaun):
    fort26 = numpy.loadtxt(fortpath,dtype='str',comments='%',delimiter='\n')[1:]
    for i,line in enumerate(fort26):
        s = 1 if len(line.split()[0])==1 else 0
        zabs = float(re.compile(r'[^\d.-]+').sub('',line.split()[1+s]))
        if 'q' in str(line.split()[7+s]) and abs(2*(zabs-float(zabs))/(zabs+float(zabs))) < 0.02:
            alpha = float(line.split()[7+s].split('q')[0])*daoaun/1e-5
            error = float(line.split()[8+s].split('q')[0])*daoaun/1e-5
            break
    return i,alpha,error
        
def readfort18(fortpath):
    """
    Extract fitting results from fort.18 output. If the path to the fort.18 file is found,
    the routine will read the file from the end backward.
    """
    flag,n,df,chisq,chisq_nu,alpha,error,n,df = 1,'-','-','-','-','-','-','-','-'
    if fortpath!=None and os.path.exists(fortpath):
        daoaun = 1. if '--published' in sys.argv else 1e-6 
        if '--published' not in sys.argv:
            vpsetup = fortpath.replace(fortpath.split('/')[-1],'vp_setup.dat')
            if os.path.exists(vpsetup):
                for line in numpy.loadtxt(vpsetup,dtype=str,delimiter='\n',comments='!'):
                    if 'daoaun'in line:
                        daoaun = float(line.split()[1])
        reg,alpha,error = readfort26(fortpath.replace('.18','.26'),daoaun)
        fort18 = numpy.loadtxt(fortpath,dtype='str',delimiter='\n')
        for i in range(len(fort18)-1,0,-1):
            if 'statistics for whole fit:' in fort18[i] and flag==1:
                n     = float(fort18[i+2].split()[3])
                df    = float(fort18[i+2].split()[4])
                flag  = 2
            if 'arameter errors:' in fort18[i] and flag==2:
                line  = fort18[i+1+reg]
                s     = 1 if len(line.split()[0])==1 else 0
                if 'q' in str(line.split()[4+s]) and '*' not in str(line.split()[4+s]):
                    error = float(line.split()[4+s].split('q')[0])*daoaun/1e-5
                flag = 3
            if 'chi-squared :' in fort18[i] and flag==3:
                chisq_nu = float(fort18[i].split()[2])
                chisq = float(fort18[i].split()[-3].replace(',',''))
                line  = fort18[i+2+reg]
                s     = 1 if len(line.split()[0])==1 else 0
                if 'q' in str(line.split()[4+s]) and '*' not in str(line.split()[4+s]):
                    alpha = float(line.split()[4+s].split('q')[0])*daoaun/1e-5
                break
    # Create object and include results
    results = type('results', (object,), {})()
    results.chisq_nu=chisq_nu
    results.chisq=chisq
    results.alpha=alpha
    results.error=error
    results.df=df
    results.n=n
    return results
        
def spheredist(ra1,dec1,ra2,dec2):
    """
    Calculate spherical distance between 2 points.

    Parameters
    ----------
    ra1 : float
      Right ascension of the first object
    ded1 : float
      Declinaison of the first object
    ra2 : float
      Right ascension of the second object
    ded2 : float
      Declinaison of the seconds object

    Returns
    -------
    distance : float
      spherical distance between the 2 objects
    """
    theta1   = ra1*math.pi/180
    phi1     = math.pi/2-dec1*math.pi/180
    x1       = math.sin(phi1)*math.cos(theta1)
    y1       = math.sin(phi1)*math.sin(theta1)    
    z1       = math.cos(phi1)
    theta2   = ra2*math.pi/180
    phi2     = math.pi/2-dec2*math.pi/180
    x2       = math.sin(phi2)*math.cos(theta2)
    y2       = math.sin(phi2)*math.sin(theta2)    
    z2       = math.cos(phi2)
    distance = math.acos(x1*x2+y1*y2+z1*z2)
    distance = distance*180/math.pi
    return distance

def system_list():
    """
    Create list of systems based on user-defined selection criteria.
    """
    n = 0
    filename = 'fortlist_'+str(system).replace('/','--')+'.dat'
    os.system('find '+fitdir+' -mindepth 3 -maxdepth 3 | sort > list_'+filename)
    allsys = numpy.loadtxt('list_'+filename,dtype='str')
    outfile = open(filename,'w')
    for line in allsys:
        quasar  = line.split('/')[-3]
        redabs  = line.split('/')[-2]
        sample  = line.split('/')[-1]
        system  = quasar+'/'+redabs+'/'+sample
        # condition 0: check if system specified by the user and match the current system
        cond0   = system==None or system==system
        # condition 1: either sample is specified or in the list of Keck+VLT sample
        cond1   = sample==sample or (sample==None and sample in keck+vlt)
        # condition 2: either selection not specified or valid selection name and identified model
        cond2a  = selection==None
        cond2b  = str(selection) in curlist.head(0).columns.values and \
                  system in numpy.array(curlist['system']) and \
                  curlist[selection][numpy.where(numpy.array(curlist['system'])==system)[0][0]]!='-'
        # condition 3: check user-defined instrument and identify right sample
        cond3a  = instrument==None
        cond3b  = instrument=='uves'  and sample in vlt
        cond3c  = instrument=='hires' and sample in keck
        # condition 4: if clip option specified, check that the system is in the clipped list
        cond4   = ('--clip' not in sys.argv) or ('--clip' in sys.argv and system not in clippeduves)
        if cond0 and cond1 and (cond2a or cond2b) and (cond3a or cond3b or cond3c) and cond4:
            # Get the model ID
            if '--distortion' in sys.argv and selection=='jak12':
                whitmore = 'yes' if '--whitmore' in sys.argv else 'no'
                i = numpy.where(numpy.logical_and(distres['system']==system,distres['whitmore']==whitmore))[0][0]
                model = 'model-%.1f'%float(distres['model individual'][i])
            elif selection!=None:
                model = 'model-%.1f'%float(curlist[selection][numpy.where(curlist['system']==system)[0][0]])
            elif model!=None:
                model = 'model-%.1f'%float(model)
            else:
                print('ERROR: Please specify either --distortion, the model or the selection...')
                quit()
            # Add system into list
            if '--simulation' in sys.argv:
                outfile.write(line+'/'+model+'/sims/'+simtest+'/'+test+'/'+distortion+'\n')
            else:
                outfile.write(line+'/'+model+'/runs/'+test+'/'+distortion+'\n')
            n = n + 1
    outfile.close()
    os.system('rm list_'+filename)
    if n==0:
        print('|- ABORT: No absorption systems found, please make sure your arguments are correct.')
        quit()
    return filename

def env(var_name):
    """
    Store main variables in object
    """
    #home        = os.getenv('HOME')+'/ASTRO/analysis/alpha'
    #home        = os.getenv('HOME')+'/Volumes/ASTRO_HOME/ASTRO/analysis/alpha' if '--server'   in sys.argv else home
    #home        = '/media/removable/ASTRO/analysis/alpha'                      if '--external' in sys.argv else home
    #home        = '/short/gd5/ASTRO/analysis/alpha'                            if '--raijin'   in sys.argv else home
    #alphapath   = '/home/561/vxd561/ASTRO/code/'                               if '--raijin'   in sys.argv else ''
    #vpfitpath   = '/home/561/vxd561/ASTRO/code/vpfit10/'                       if '--raijin'   in sys.argv else ''
    #fitdir      = home+'/systems/'
    #wdrep       = home+'/systems/G191-B2B/'
    #Crep        = home+'/dipole/'
    #Rrep        = home+'/alpha_analysis/'
    #rundir      = home+'/runs/'
    #uveshead    = home+'/headers/'
    #compdir     = home+'/multiplots/compare/'
    #here        = os.getenv('PWD')
    #pathdata    = os.path.abspath(__file__).rsplit('/',1)[0] + '/data/'
    #pathdata    = os.path.dirname(os.path.realpath(__file__)) + '/data/'
    #skipabs     = []
    #discard     = []
    #keck        = ['HIRES_churchill','HIRES_sargent','HIRES_prochaska','HIRES_outram']
    #vlt         = ['UVES_squader']
    #murphy      = ['HIRES_murphy_A','HIRES_murphy_B1','HIRES_murphy_B2','HIRES_murphy_C']
    var_dictionary={
        'outliers':['J194454+770552/2.84330/HIRES_sargent',
                    'J220852-194400/1.01720/HIRES_sargent',
                    'J220852-194400/2.07620/HIRES_sargent',
                    'J000448-415728/1.54190/UVES_squader']
        }
    #degensys    = ['J111113-080402/3.60770/UVES_squader',
    #                 'J034943-381031/3.02470/HIRES_prochaska']
    #badwhit     = ['J200324-325145/2.03290/UVES_squader']
    #clippeduves = ['J104032-272749/1.38610/UVES_squader',
    #                 'J010311+131617/2.30920/UVES_squader',
    #                 'J234628+124900/2.17130/UVES_squader',
    #                 'J010311+131617/1.79750/UVES_squader',
    #                 'J044017-433308/2.04820/UVES_squader',
    #                 'J055246-363727/1.74750/UVES_squader',
    #                 'J040718-441014/2.59480/UVES_squader']
    #atom       = make_atom_list(pathdata+'atom.dat')
    #uvesexp    = numpy.genfromtxt(pathdata+'uvesexp.dat',names=True,dtype=object,comments='!')
    #hiresexp   = numpy.genfromtxt(pathdata+'hiresexp.dat',names=True,dtype=object,comments='!')
    #uvesset    = numpy.genfromtxt(pathdata+'settings.dat',names=True,dtype=object,comments='!',skip_header=4)
    #done       = False
    #c          = 299792.458
    #alphara    = 17.3
    #alphadec   = -61
    #uvesblue   = 3900.
    #uvesred    = 5800.
    #zsample    = 'all'
    #zcut       = 1.6
    #wd_slope   = numpy.arange(-15,15.1,0.1)
    #hires_amp  = numpy.arange(0,400,50)
    #args         = numpy.array(sys.argv, dtype='str')
    #slope      = 0    if '--slope'    not in sys.argv else float(args[numpy.where(args=='--slope'   )[0][0]+1])
    #minslope   = None if '--minslope' not in sys.argv else float(args[numpy.where(args=='--minslope')[0][0]+1])
    #maxslope   = None if '--maxslope' not in sys.argv else float(args[numpy.where(args=='--maxslope')[0][0]+1])
    #step       = None if '--step'     not in sys.argv else float(args[numpy.where(args=='--step'    )[0][0]+1])
    #operation  = None if len(sys.argv)==1 else sys.argv[1]
    #clean      = '--clean'     in sys.argv
    #compress   = '--compress'  in sys.argv
    #constrain  = '--constrain' in sys.argv
    #display    = '--display'   in sys.argv
    #display2   = '--display2'  in sys.argv
    #expind     = '--expind'    in sys.argv  
    #fit        = '--fit'       in sys.argv
    #fit2       = '--fit2'      in sys.argv
    #loop       = '--loop'      in sys.argv
    #mgisotope  = '--mgisotope' in sys.argv
    #murphy     = '--murphy'    in sys.argv
    #newatom    = '--newatom'   in sys.argv
    #noalpha    = '--noalpha'   in sys.argv
    #original   = '--original'  in sys.argv
    #previous   = '--previous'  in sys.argv
    #reset      = '--reset'     in sys.argv
    #show       = '--show'      in sys.argv
    #tbs        = '--tbs'       in sys.argv
    #whitmore   = '--whitmore'  in sys.argv
    #binning    = 12          if '--bin'        not in sys.argv else   int(args[numpy.where(args=='--bin'       )[0][0]+1])
    #order      = 3           if '--order'      not in sys.argv else   int(args[numpy.where(args=='--order'     )[0][0]+1])
    #repeat     = 1           if '--repeat'     not in sys.argv else   int(args[numpy.where(args=='--repeat'    )[0][0]+1])
    #ntrans     = 5           if '--ntrans'     not in sys.argv else   int(args[numpy.where(args=='--ntrans'    )[0][0]+1])
    #stdev      = 0           if '--stdev'      not in sys.argv else float(args[numpy.where(args=='--stdev'     )[0][0]+1])
    #chisq      = 1.E-5       if '--chisq'      not in sys.argv else float(args[numpy.where(args=='--chisq'     )[0][0]+1])
    #snr        = None        if '--snr'        not in sys.argv else float(args[numpy.where(args=='--snr'       )[0][0]+1])
    #threshold  = None        if '--threshold'  not in sys.argv else float(args[numpy.where(args=='--threshold' )[0][0]+1])
    #wmin       = None        if '--wmin'       not in sys.argv else float(args[numpy.where(args=='--wmin'      )[0][0]+1])
    #wmax       = None        if '--wmax'       not in sys.argv else float(args[numpy.where(args=='--wmax'      )[0][0]+1])
    #xmin       = None        if '--xmin'       not in sys.argv else float(args[numpy.where(args=='--xmin'      )[0][0]+1])
    #xmax       = None        if '--xmax'       not in sys.argv else float(args[numpy.where(args=='--xmax'      )[0][0]+1])
    #ymin       = None        if '--ymin'       not in sys.argv else float(args[numpy.where(args=='--ymin'      )[0][0]+1])
    #ymax       = None        if '--ymax'       not in sys.argv else float(args[numpy.where(args=='--ymax'      )[0][0]+1])
    #mode       = None        if '--mode'       not in sys.argv else   str(args[numpy.where(args=='--mode'      )[0][0]+1])
    #compare    = None        if '--compare'    not in sys.argv else   str(args[numpy.where(args=='--compare'   )[0][0]+1])
    #custom     = None        if '--custom'     not in sys.argv else   str(args[numpy.where(args=='--custom'    )[0][0]+1])
    #sample     = None        if '--sample'     not in sys.argv else   str(args[numpy.where(args=='--sample'    )[0][0]+1])
    #tarfile    = None        if '--include'    not in sys.argv else   str(args[numpy.where(args=='--include'   )[0][0]+1])
    #instrument = None        if '--instrument' not in sys.argv else   str(args[numpy.where(args=='--instrument')[0][0]+1])
    #simulation = None        if '--simulation' not in sys.argv else   str(args[numpy.where(args=='--simulation')[0][0]+1])
    #model      = None        if '--model'      not in sys.argv else   str(args[numpy.where(args=='--model'     )[0][0]+1])
    #system     = None        if '--system'     not in sys.argv else   str(args[numpy.where(args=='--system'    )[0][0]+1])
    #selection  = None        if '--selection'  not in sys.argv else   str(args[numpy.where(args=='--selection' )[0][0]+1])
    #path       = '.'         if '--path'       not in sys.argv else   str(args[numpy.where(args=='--path'      )[0][0]+1])
    #plot       = 'all'       if '--plot'       not in sys.argv else   str(args[numpy.where(args=='--plot'      )[0][0]+1])
    #vpversion  = '10'        if '--vpfit'      not in sys.argv else   str(args[numpy.where(args=='--vpfit'     )[0][0]+1])
    #arm        = None        if '--arm'        not in sys.argv else   str(args[numpy.where(args=='--arm'       )[0][0]+1])
    #shape      = 'slope'     if '--shape'      not in sys.argv else   str(args[numpy.where(args=='--shape'     )[0][0]+1])
    #vpcommand  = vpfitpath + 'vpfit' + vpversion
    #atomdir    = pathdata  + 'atom.dat'  
    #atomdir    = pathdata  + 'atom_new.dat'       if '--newatom'   in sys.argv else atomdir
    #atomdir    = pathdata  + 'atom_murphy.dat'    if '--murphy'    in sys.argv else atomdir
    #atomdir    = pathdata  + 'atom_mgisotope.dat' if '--mgisotope' in sys.argv else atomdir
    #vpfsetup   = 'vp_setup_king.dat' if vpversion=='9.5-king' else 'vp_setup_hires.dat' if instrument=='hires' else 'vp_setup_uves.dat'
    #vpfsetup   = numpy.loadtxt(pathdata+vpfsetup,dtype=str,delimiter='\n',comments='!')
    #vpfsetup   = numpy.hstack((vpfsetup,['chisqthres %.E 2 %.E'%(chisq,chisq)])) if vpversion!='9.5-king' else vpfsetup
    #distortion = '0.000' if round(slope,3)==0 else 'm%.3f'%abs(slope) if slope<0 else 'p%.3f'%abs(slope)
    #deviation  = '%.2f'%stdev if expind else '0.00'
    ##test       = 'v' + vpversion + '_chisq%.E'%chisq
    ##test       = test+'_'+arm            if instrument=='uves'  and '--simulation' not in sys.argv    else test
    ##test       = test+'_'+shape          if instrument=='hires' and (slope!=0 or distsep!=0)      else test
    ##test       = test+'_step%.E'%distsep if distsep!=0                                                else test
    ##test       = test+'_prev'              if '--previous'   in sys.argv and (slope!=0 or distsep!=0) else test
    ##test       = test+'_jw'                if '--whitmore'   in sys.argv and (slope!=0 or distsep!=0) else test
    ##test       = test+'_null'              if '--simulation' not in sys.argv and '--noalpha' in sys.argv  else test
    ##test       = test+'_new'               if '--newatom'    in sys.argv                                  else test
    ##test       = test+'_murphy'            if '--murphy'     in sys.argv                                  else test
    ##test       = test+'_mg'                if '--mgisotope'  in sys.argv                                  else test
    ##test = test+'_noalpha'         if '--noalpha'     in sys.argv    else test
    ##test = test+'_colfix'          if '--colfix'      in sys.argv    else test
    ##test = test+'_fddhires'        if '--fdd'         in sys.argv    else test
    ##test = test+'_fddhires2'       if '--fdd2'        in sys.argv    else test
    ##test = test+'_final'           if '--finalmodel'  in sys.argv    else test
    #modflag = ''
    ##modflag = modflag+'_'+str(totrep)+'-0'            if totrep!=0 and sys.argv[1]=='run' else modflag
    ##modflag = modflag+'_'+str(totrep)+'-'+str(totrep) if totrep!=0 and sys.argv[1]!='run' else modflag
    #if '--test' in sys.argv:
    #    k = numpy.where(args=='--test')[0][0]
    #    test = args[k+1]
    #if os.getenv('HOME')=='/home/561/vxd561':
    #    curlist = numpy.genfromtxt(pathdata+'allsys.dat',names=True,dtype=object,comments='!')
    #    distres = numpy.genfromtxt(pathdata+'sims.dat',names=True,dtype=object,comments='!')
    return var_dictionary[var_name]
