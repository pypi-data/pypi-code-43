import sys,os,numpy
from matplotlib import re
from .utils import *

def run(args):
    """
    This operation will create realistic simulated absorption systems based
    on the real turbulent fort.13 model from each selected system.
    
    Examples
    --------
    
    >>> alpha run --system J000344-232354/0.45210/UVES_squader \ 
    >>>           --simulation complex --stdev 0.05 \ 
    >>>           --slope -0.123 --sloperange -1.123 0.877 \ 
    >>>           --step 0.1 --model 1 --previous
    
    The following is the command to be run to reproduce the results from
    `Dumont et al. (2017) <https://doi.org/10.1093/mnras/stx381>`_:

    >>> alpha run --system J043037m485523/1.35560/UVES_squader/ \ 
    >>>           --simulation complex --snr 1000 --slope 0.200 \ 
    >>>           --sloperange 0 0.3 --step 0.005 --model 7.2
    >>>           --chisq 1e-05 --previous --instrument uves
    """
    # Set up suitable lookup table
    database = [args.system] if args.system!=None \
        else getcoddam('distres',args.coddam) if args.simulation!=None \
             else getcoddam('curlist',args.coddam) if args.selection!=None \
                  else getcoddam('publist',args.coddam)
    # Get VPFIT setup
    vpcommand,atomdir,vpfsetup = vpfitset(args.vpfit,args.instrument,args.chisq)
    # Move to systems parent location
    os.chdir(args.path)
    path = os.getcwd()
    # Loop over look up table
    for i in range(len(database)):
        # Extract system name from database row
        system = args.system if args.system!=None else database['system'][i]
        qso    = system.split('/')[0]
        zabs   = system.split('/')[1]
        sample = system.split('/')[2]
        # Identify right target model
        modpath = getmodpath(args,system)
        if modpath==None: continue
        # Define model directory name
        syspath = '/'.join([path,system,modpath])
        # Check if system path exists
        if os.path.exists(syspath)==False:
            print('ERROR: Path not found (%s)'%syspath)
            quit()
        else:
            print('|- System/Model: %s/%s'%(system,modpath))
        # Define run directory name
        runpath = syspath+'/runs' if args.simulation==None else  '/'.join([syspath,'sims',simtest])
        if args.simulation!=None: print('|  |- Simulation: sims/%s'%simtest)
        if args.simulation!=None and os.path.exists('/'.join([runpath,'model','original']))==False: getsimdata()
        # Prepare distortion repository and create synthetis spectrum if not existent
        test_name = gettestname(args.instrument,args.step,args.slope,args.chisq,previous=args.previous,whitmore=args.whitmore,simulation=args.simulation)
        print('|  |  |- Test version:',test_name)
        # Loop through all slope values and perform calculations
        distlist,distplot = slopelist(args.slope,args.sloperange[0],args.sloperange[1],args.step)
        for slope2fit in distlist:
            # Create and move to distortion folder
            distortion = '0.000' if round(slope2fit,3)==0 else 'm%.3f'%abs(slope2fit) if i<0 else 'p%.3f'%abs(slope2fit)
            distpath = '%s/%s/%s'%(runpath,test_name,distortion)
            # Loop over models to prepare and fit them
            models = ['turbulent','thermal'] if args.simulation==None else ['turbulent']
            for model2fit in models:
                # Initialize parameters
                qvar = numpy.empty((0,2))
                qini,qend,qred,qblue,olap,ovlp = [],[],[],[],[],'-'
                regtotal = regboth = regblue = regred = 0
                # Read header and fort.13 informations
                main_path = syspath if args.simulation==None else runpath
                head_path = main_path+'/model/header.dat'
                if args.previous and args.slope!=slope2fit and args.step!=0:
                    i = slope2fit - args.step if slope2fit > args.slope else slope2fit+args.step
                    path_dist = '0.000' if round(i,3)==0 else 'm%.3f'%abs(i) if i<0 else 'p%.3f'%abs(i)
                    fort_path = runpath+'/'+test_name+'/'+path_dist+'/'+model2fit+'/'+model2fit+'_fit.13'
                else:
                    fort_path = main_path+'/model/'+model2fit+'.13'
                fort_header_old,fort_content_old,comp,twoq = storedata(fort_path,head_path)
                # Store selected fort.13 header, and shifts
                store_shift = []
                fort_header_new = numpy.empty((0,8))
                for i in range (len(fort_header_old)):
                    armflag = None
                    trans = fort_header_old[i,-3]
                    wrest = float(atominfo(trans)[1])
                    wave1 = float(fort_header_old[i,2])
                    wave2 = float(fort_header_old[i,3])
                    shift = getshift(qso,sample,wave1,wave2,slope2fit,args.shape,args.whitmore)
                    if args.instrument=='uves':
                        if args.arm==None or armflag==args.arm or armflag in args.arm:
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
                    if args.mgisotope and 'Mg' in fort_content_old[i,0]:
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
                if distortion not in ['','0.000']:
                    for p in range (len(store_shift)):
                        shift = ['>>','1.00000FF','0.0000000FF',store_shift[p]+'FF','0.000FF','0.00','0.00E+00',p+1]
                        fort_content_new = numpy.vstack((fort_content_new,shift))
                fort_header_new = fort_header_new
                fort_content_new = fort_content_new
                # Output action
                skip1 = ( args.arm=='red' and len(qred)==0 )
                skip2 = ( args.arm=='blue' and len(blue)==0 )
                skip3 = ( args.arm=='redblue' and len(qred)==0 and len(blue)==0 )
                skip4 = ( sys.argv[1]=='run' and '--catchup' in sys.argv and \
                          os.path.exists(runpath+'/'+distortion+'/thermal'+modflag+'/fort.26')==True )
                skip5 = ( sys.argv[1]=='results' and system in outliers )
                if skip1 or skip2 or skip3 or skip4 or skip5:
                    continue
                # Loop over number of VPFIT iterations
                for nrep in range(args.repeat):
                    # Create fitting mode flag if several VPFIT iterations are requested
                    modflag = '' if nrep==0 else '_%i'%(nrep+1)
                    print('|  |  |- Distortion slope:',distortion)
                    print('|  |  |  |- Processing %s fitting...'%model2fit)
                    print('|  |  |  |- VPFIT iteration:',nrep+1)
                    modpath = distpath+'/'+model2fit+modflag
                    os.system('mkdir -p '+modpath)
                    os.chdir(modpath)
                    # Prepare input fort.13 for distortion slope
                    prepare_model(model2fit,fort_header_new,fort_content_new,args.simulation)
                    # Remove and re-create link to data folder
                    if os.path.exists('data'):
                        os.system('rm data')
                    if args.simulation==None:
                        os.system('ln -s ../../../../../data')
                    else:
                        os.system('ln -s ../../../model/data')
                    # Prepare model folders and run VPFIT
                    if os.path.exists('atom.dat')==True:
                        os.system('rm atom.dat vp_setup.dat')
                    os.system('cp '+atomdir+' atom.dat')
                    opfile = open('vp_setup.dat','w')
                    for row in vpfsetup:
                        opfile.write(row+'\n')
                    opfile.close()
                    os.environ['ATOMDIR']='./atom.dat'
                    os.environ['VPFSETUP']='./vp_setup.dat'
                    if '--iterone' in sys.argv:            
                        open('fitcommands','w').write('e\n\n\n'+model2fit+'_ini.13\nn\nn\n')
                    elif '--illcond' in sys.argv:
                        open('fitcommands','w').write('f\nil\n\n\n'+model2fit+'_ini.13\nn\nn\n')
                    else:
                        open('fitcommands','w').write('f\n\n\n'+model2fit+'_ini.13\nn\nn\n')
                    os.system(vpcommand+' < fitcommands > termout')
                    if os.path.exists('fort.26')==True:
                        createfit13(model2fit)
            # Compress results for supercomputer calculations
            if args.compress:
                destination = path.replace('list','execute')+'/'
                os.chdir(path)
                target   = system+'/'+model+'/sims/'+simtest+'/'+test+'/'+distortion
                filename = target.replace('/','--')
                os.system('tar -zcvf '+filename+'.tar.gz '+target+'/')
                os.system('rm -rf '+target+'/')
                os.system('mkdir -p '+destination)
                os.system('mv '+filename+'.tar.gz '+destination)

def getmodpath(args,system):
    modpath = None
    # Identify system and check if it is targeted
    if args.simulation!=None and args.system==system and \
       args.system not in outliers and args.whitmore==(database['whitmore'][i]=='yes'):
        sim     = 'sim2' if args.stdev!=0 else 'sim1'
        slope   = float(database['%s mid%02i'%(sim,100*args.stdev)][i]) if args.slope==None else args.slope
        tilt    = '0.000' if round(slope,3)==0 else 'm%.3f'%abs(slope) if slope<0 else 'p%.3f'%abs(slope)
        simtest = '%s_%s_%.2f'%(args.simulation,tilt,args.stdev)
        simtest = simtest if args.snr==None else simtest+'_snr%.E'%args.snr
        model   = database['%s model'%sim][i] if args.model==None else args.model
        modpath = 'model-%.1f'%float(model)
    elif args.system!=None and args.system==system:
        model   = args.model if args.selection==None else database[args.selection][i]
        modpath = None if model==None else 'model-%.1f'%float(model)
    elif args.selection!=None and database[args.selection][i]!='-':
        model   = database[args.selection][i]
        modpath = 'model-%.1f'%float(model)
    elif args.instrument==database['instrument'][i].lower():
        modpath = 'model-7.1'
    return modpath
                
def getsimdata():
    os.system('mkdir -p %s/model/original'%runpath)
    os.system('mkdir -p %s/model/data'%runpath)
    os.chdir('%s/model/'%runpath)
    # Copy transition list, fort.18 and fort.26 files in model folder
    os.system('cp %s/model/header.dat .'%syspath)
    os.system('cp %s/model/turbulent.18 fort.18'%syspath)
    os.system('cp %s/model/turbulent.26 fort.26'%syspath)
    # Create fort_fit.13 from the fort.26 file and store contents in fort13 array
    createfit13('fort',simulation=True)
    fort13 = open('fort_fit.13','r')
    fort13 = [line.strip() for line in fort13]
    # Store transition list into array and delete temporary files
    hdin   = numpy.loadtxt('header.dat',dtype=str,delimiter='\n')
    os.system('rm header.dat fort*')
    # Initialise output files
    file1  = open('original/fort.13','w')
    file2  = open('turbulent.13','w')
    hdout  = open('header.dat','w')
    regs   = numpy.empty((0,2))
    # Loop over all the components and prepare ouput model
    i,flag,ihead,idx = 0,0,0,1
    while i<len(fort13):
        line = fort13[i]
        # End loop when empty line is reached
        if len(line.strip())==0:
            break
        elif '*' in line:
            file1.write(line+'\n')
            file2.write(line+'\n')
            flag += 1
        elif flag==1:
            spec = line.split()[0].split('/')[-1].replace('.fits','')
            regs = numpy.vstack((regs,[float(line.split()[2]),float(line.split()[3])]))
            head = line.replace(line.split()[0],'data/'+line.split()[0].split('/')[-1])
            file1.write(head+'\n')
            file2.write(line.replace(line.split()[0],'data/spec%02i.txt'%(idx))+'\n')
            hdout.write(hdin[ihead]+'\n')
            idx += 1
            ihead += 1
        elif flag==2:
            val = line.split()
            if len(val[0])==1:
                vals = [val[0]+' '+val[1],val[2],val[3],val[4],val[5],val[6],val[7],val[8]]
            else:
                vals = [val[0],val[1],val[2],val[3],val[4],val[5],val[6],val[7]]
            comp = numpy.delete(vals,4,0)
            file1.write('   {0:<6} {1:>10} {2:>15} {3:>11} {4:>10} {5:>10} {6:>3}\n'.format(*comp))
            vals[4] = '0.000'+" ".join(re.findall("[a-zA-Z]+",vals[4][-2:]))
            file2.write('   {0:<6} {1:>10} {2:>15} {3:>11} {4:>11} {5:>10} {6:>10} {7:>3}\n'.format(*vals))
        i += 1
    file1.close()
    file2.close()
    hdout.close()
    # Go to relevant folder and create symlink to data folder
    os.chdir(runpath+'/model/original/')
    if os.path.exists('data'): os.system('rm data')
    os.system('ln -s ../../../../../data')
    # Prepare input commands to generate chunks on VPFIT
    vpfit_commands(len(hdin))
    # Copy atom.dat and vp_dat and ex
    os.system('cp '+atomdir+' atom.dat')
    opfile = open('vp_setup.dat','w')
    for row in vpfsetup:
        row = 'NOVARS 3' if 'NOVARS' in row else row
        opfile.write(row+'\n')
    opfile.close()
    os.environ['ATOMDIR']='./atom.dat'
    os.environ['VPFSETUP']='./vp_setup.dat'
    # Run VPFIT and create chunks for original fort.13
    os.system(vpcommand+' < fitcommands > termout')
    # Remove temporary files and move chunks to specific folder
    #os.system('rm fitcommands termout')
    os.system('mkdir -p chunks/')
    os.system('mv vpfit_chunk* chunks/')
    # Extract data chunks, modify error array and add noise
    shifts = numpy.empty((0,2))
    os.chdir(runpath+'/model/')
    sp = numpy.loadtxt('original/data/'+spec+'.dat',comments='!')
    wa = sp[:,0]
    er = sp[:,2]
    for ireg in range(len(regs)):
        data  = numpy.loadtxt('./original/chunks/vpfit_chunk%03i.txt'%(ireg+1),comments='!')
        # Initialize non-used parameters called in getshift function
        shift = float(getshift(qso,sample,regs[ireg,0],regs[ireg,1],slope,args.shape,args.whitmore,args.stdev))
        wmin  = data[0,0]
        wmax  = data[-1,0]
        imin1 = abs(wa-(wmin-3)).argmin()
        imin2 = abs(wa-wmin).argmin()
        imax1 = abs(wa-wmax).argmin()
        imax2 = abs(wa-(wmax+3)).argmin()
        wave  = wa[imin1:imax2+1]
        error = er[imin1:imax2+1]
        flux  = numpy.hstack(([1]*(imin2-imin1),data[:,3],[1]*(imax2-imax1)))
        ofile = open('data/spec%02i.txt'%(ireg+1),'w')
        for j in range(len(wave)):
            iwave  = wave[j]*(2*c+shift)/(2*c-shift)
            ierror = error[j] if args.snr==None else 1./args.snr
            iflux  = flux[j] if ierror<0 else flux[j]+numpy.random.normal(0,ierror)
            ofile.write('{0:>21} {1:>25} {2:>30}\n'.format('%.13f'%iwave,'%.16f'%iflux,'%.16E'%ierror))
        ofile.close()
    if expind:
        outfile = open('shifts.dat','w')
        for i in range(len(shifts)):
            outfile.write(shifts[i,0]+'  '+shifts[i,1]+'\n')
        outfile.close()
