import os,sys,numpy,re
from .vpfit import make_atom_list,atomic_info
from .distortion import getshift

def create_fit13(model,simulation=False):
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

def read_fort26(fortpath,daoaun):
    fort26 = numpy.loadtxt(fortpath,dtype='str',comments='%',delimiter='\n')[1:]
    for i,line in enumerate(fort26):
        s = 1 if len(line.split()[0])==1 else 0
        zabs = float(re.compile(r'[^\d.-]+').sub('',line.split()[1+s]))
        if 'q' in str(line.split()[7+s]) and abs(2*(zabs-float(zabs))/(zabs+float(zabs))) < 0.02:
            alpha = float(line.split()[7+s].split('q')[0])*daoaun/1e-5
            error = float(line.split()[8+s].split('q')[0])*daoaun/1e-5
            break
    return i,alpha,error
        
def read_fort18(fortpath):
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

def store_data(fortpath,headpath):
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

def fort_update(fort_header_old,fort_content_old,atom,qso,sample,slope2fit,mgisotope=False,
                shape='slope',whitmore=False,arm=None,explist=None,settings=None,stdev=0):
    
    # Initialize parameters
    qvar = numpy.empty((0,2))
    qini,qend,qred,qblue,olap,ovlp = [],[],[],[],[],'-'
    # Initialize arm regions (deprecated, originally used in get_shift module)
    #regtotal = regboth = regblue = regred = 0
    # Store selected fort.13 header, and shifts
    store_shift = []
    fort_header_new = numpy.empty((0,8))
    for i in range (len(fort_header_old)):
        armflag = None
        trans = fort_header_old[i,-3]
        wrest = float(atomic_info(atom,trans)[1])
        wave1 = float(fort_header_old[i,2])
        wave2 = float(fort_header_old[i,3])
        shift = getshift(wave1,wave2,slope2fit,qso,sample,explist,settings,shape,whitmore,stdev)
        if sample.startswith('UV'):
            if arm==None or armflag==arm or armflag in arm:
                fort_header_new = numpy.vstack((fort_header_new,fort_header_old[i]))
                store_shift.append(shift)
                if fort_header_old[i,-2]!='external': qvar=numpy.vstack((qvar,[trans,wrest]))
                if fort_header_old[i,-2]=='overlap': ovlp='o'
            qini.append(wrest)
            if armflag=='blue':
                qblue.append(wrest)
                qend.append(wrest)
            if armflag=='red':
                qred.append(wrest)
                qend.append(wrest)
            if armflag=='overlap':
                olap.append(fort_header_old[i,-3])
        else:
            fort_header_new = numpy.vstack((fort_header_new,fort_header_old[i]))
            store_shift.append(shift)
            if fort_header_old[i,-2]!='external':
                qvar = numpy.vstack((qvar,[fort_header_old[i,-3],wrest]))
            if fort_header_old[i,-2]=='overlap':
                ovlp = 'o'
    if len(qvar)==0:
        qmin = qmax = qvar
    else:
        qlist     = numpy.array(qvar[:,1],dtype='float')
        qlist_min = numpy.where(qlist==min(qlist))[0][0]
        qlist_max = numpy.where(qlist==max(qlist))[0][0]
        qmin = qvar[qlist_min,0].replace('_','')
        qmax = qvar[qlist_max,0].replace('_','')
        qvar = str(int(abs(max(qlist)-min(qlist))))
    # Store selected fort.13 content, and shift components
    fort_content_new = numpy.empty((0,8))
    mgcomps = numpy.empty((0,8))
    for i in range (len(fort_content_old)):
        if mgisotope and 'Mg' in fort_content_old[i,0]:
            mgcomps = numpy.vstack((mgcomps,fort_content_old[i]))
        else:
            fort_content_new = numpy.vstack((fort_content_new,fort_content_old[i]))        
    # Implement Mg and Aw components
    for p in range (len(mgcomps)):
        fort_content_new = numpy.vstack((fort_content_new,mgcomps[p]))        
        fort_content_new[-1,1] = re.compile(r'[^\d.-]+').sub('',fort_content_new[-1,1])+'x'
    for p in range (len(mgcomps)):
        fort_content_new = numpy.vstack((fort_content_new,mgcomps[p]))
        fort_content_new[-1,0] = fort_content_new[-1,0].replace('Mg','Aw')
        if p==0 and len(mgcomps)>1:
            fort_content_new[-1,1] = re.compile(r'[^\d.-]+').sub('',fort_content_new[-1,1])+'%'
        else:
            fort_content_new[-1,1] = re.compile(r'[^\d.-]+').sub('',fort_content_new[-1,1])+'X'
        fort_content_new[-1,2] = fort_content_new[-1,2].upper()
        fort_content_new[-1,3] = fort_content_new[-1,3].upper()
        fort_content_new[-1,4] = fort_content_new[-1,4].upper()
        fort_content_new[-1,5] = fort_content_new[-1,5].upper()
    # Implement fix shift values in fort arrays
    if round(slope2fit,3)!=0:
        for p in range (len(store_shift)):
            shift = ['>>','1.00000FF','0.0000000FF',store_shift[p]+'FF','0.000FF','0.00','0.00E+00',p+1]
            fort_content_new = numpy.vstack((fort_content_new,shift))
    fort_header_new = fort_header_new
    fort_content_new = fort_content_new
    return fort_header_new,fort_content_new,qred,qblue

def get_results(therfort=None,turbfort=None,original=False):
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
            if simulation==False and '--noalpha' in sys.argv:
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
