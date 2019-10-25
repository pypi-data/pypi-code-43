import sys,os,numpy
from matplotlib import re
from .simulation import create_simulated_model
from .utils import get_coddam,get_path_to_model,get_test_name,check_file_path
from .vpfit import vpfit_setup
from .forthandle import store_data,fort_update,prepare_model,create_fit13
from .constants import *
from .distortion import slopelist

def batch_run(target_system,selection,instrument,dbkey,simulation=False,model='turbulent',vpfit='vpfit',
              chisq=1.E-5,path='./',whitmore=False,stdev=0,mid_slope=0,sloperange=[None,None],step=0,
              snr=None,no_alpha=False,previous=False,arm=None,compress=False,repeat=1):
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
    if target_system!=None:
        database = {'system':[target_system],'whitmore':[whitmore]}
    elif simulation:
        database = get_coddam('distres',dbkey)
    elif selection!=None:
        database = get_coddam('curlist',dbkey)
    else:
        database = get_coddam('publist',dbkey)
    # Get VPFIT setup
    vpfit,atom,atomdir,vpsetup,vpfsetup = vpfit_setup(vpfit,instrument,chisq,no_alpha)
    os.chdir(path)
    path = os.getcwd()
    # Loop through database
    for i in range(len(database)):
        # Extract QSO name, absorption redshift and sample name from system name
        system = database['system'][i]
        qso    = system.split('/')[0]
        zabs   = system.split('/')[1]
        sample = system.split('/')[2]
        # Identify right target model
        simtest,modpath = get_path_to_model(system,target_system,simulation,whitmore,database,stdev,mid_slope,snr,model,selection)
        if modpath==None:
            continue
        # Define model directory name
        syspath = '/'.join([path,system,modpath])
        if os.path.exists(syspath)==False:
            print('ERROR: Path not found (%s)'%syspath)
            quit()
        print('|- System/Model: %s/%s'%(system,modpath))
        # Define run directory name
        runpath = '/'.join([syspath,'sims',simtest]) if simulation else syspath+'/runs'
        os.chdir(runpath)
        # If no simulation requested, create alias of model repository
        if simulation==False:
            if os.path.exists('model'):
                os.system('rm model')
            os.system('ln -s ../model model')
        # If simulation requested, create simulated data
        if simulation==True:
            print('|  |- Simulation: sims/%s'%simtest)
            if os.path.exists('/'.join([runpath,'model','original']))==False:
                # Move to target repository
                create_simulated_model(runpath,vpfit,atomdir,instrument,qso,sample,slope,snr,chisq,atomdir,vpsetup)
        # Prepare distortion repository and create synthetis spectrum if not existent
        test_name = get_test_name(instrument,step,mid_slope,chisq,previous=previous,whitmore=whitmore,simulation=simulation)
        # Fit absorption line system
        fit_system(runpath,test_name,vpfit,instrument,qso,sample,chisq,no_alpha,mid_slope,sloperange,
                   step,previous,arm,compress,simulation,whitmore,repeat,shape,stdev)
        
def fit_system(runpath,test_name,vpfit,instrument=None,qso=None,sample=None,chisq=1.E-5,no_alpha=False,mid_slope=0,sloperange=[None,None],step=0,previous=False,arm=None,compress=False,simulation=False,whitmore=False,repeat=1,shape='slope',explist=None,settings=None,stdev=0,mgisotope=False,atomdir=None,vpfsetup=None):

    print('|  |  |- Fitting version:',test_name.split('/')[-1])
    # Get absolute path for further calls
    explist,settings,atomdir,vpfsetup = check_file_path([explist,settings,atomdir,vpfsetup])
    # Move to run path directory
    runpath = os.path.abspath(runpath)
    # Get VPFIT setup
    vpfit,atom,atomdir,vpsetup,vpfsetup = vpfit_setup(vpfit,instrument,chisq,no_alpha,atomdir,vpfsetup)
    # Get full path of explist and settings files
    if explist!=None: os.path.abspath(explist)
    if settings!=None: os.path.abspath(settings)
    # Loop through all slope values and perform calculations
    distlist,distplot = slopelist(mid_slope,sloperange[0],sloperange[1],step)
    for slope2fit in distlist:
        # Create and move to distortion folder
        distortion = '0.000' if round(slope2fit,3)==0 else 'm%.3f'%abs(slope2fit) if slope2fit<0 else 'p%.3f'%abs(slope2fit)
        distpath = '%s/%s/%s'%(runpath,test_name,distortion)
        # Loop over models to prepare and fit them
        models = ['turbulent'] if simulation else ['turbulent','thermal']
        for model2fit in models:
            # Retrieve path to header file
            head_path = runpath+'/model/header.dat'
            # Retrieve path to fort.13 file
            if previous and mid_slope!=slope2fit and step!=0:
                i = slope2fit - step if slope2fit > mid_slope else slope2fit+step
                path_dist = '0.000' if round(i,3)==0 else 'm%.3f'%abs(i) if i<0 else 'p%.3f'%abs(i)
                fort_path = runpath+'/'+fit_name+'/'+path_dist+'/'+model2fit+'/'+model2fit+'_fit.13'
            else:
                fort_path = runpath+'/model/'+model2fit+'.13'
            # Modify fort.13 and header information
            fort_header_old,fort_content_old,comp,twoq = store_data(fort_path,head_path)
            fort_header_new,fort_content_new,qred,qblue = fort_update(fort_header_old,fort_content_old,atom,qso,sample,slope2fit,mgisotope,shape,whitmore,arm,explist,settings,stdev)
            # Check conditions and run fit if allowed
            skip1 = ( arm=='red' and len(qred)==0 )
            skip2 = ( arm=='blue' and len(qblue)==0 )
            skip3 = ( arm=='redblue' and len(qred)==0 and len(qblue)==0 )
            skip4 = ( sys.argv[1]=='run' and '--catchup' in sys.argv and os.path.exists(runpath+'/'+distortion+'/thermal'+modflag+'/fort.26')==True )
            skip5 = ( sys.argv[1]=='results' and system in outliers )
            if skip1 or skip2 or skip3 or skip4 or skip5:
                continue
            # Loop over number of VPFIT iterations
            for nrep in range(repeat):
                # Create fitting mode flag if several VPFIT iterations are requested
                modflag = '' if nrep==0 else '_%i'%(nrep+1)
                print('|  |  |- Distortion slope:',distpath.split('/')[-1])
                print('|  |  |  |- Processing %s fitting...'%model2fit)
                print('|  |  |  |- VPFIT iteration:',nrep+1)
                modpath = distpath+'/'+model2fit+modflag
                os.system('mkdir -p '+modpath)
                os.chdir(modpath)
                # Prepare input fort.13 for distortion slope
                prepare_model(model2fit,fort_header_new,fort_content_new,simulation)
                # Set up VPFIT files
                os.system('cp %s atom.dat'%atomdir)
                numpy.savetxt('vp_setup.dat',vpsetup,fmt="%s")
                os.environ['ATOMDIR']=os.path.abspath('./atom.dat')
                os.environ['VPFSETUP']=os.path.abspath('./vp_setup.dat')
                # Remove and re-create link to data folder
                if os.path.islink('data'): os.system('rm data')
                os.system('ln -s ../../../model/data')
                if '--iterone' in sys.argv:            
                    open('fitcommands','w').write('e\n\n\n'+model2fit+'_ini.13\nn\nn\n')
                elif '--illcond' in sys.argv:
                    open('fitcommands','w').write('f\nil\n\n\n'+model2fit+'_ini.13\nn\nn\n')
                else:
                    open('fitcommands','w').write('f\n\n\n'+model2fit+'_ini.13\nn\nn\n')
                os.system(vpfit+' < fitcommands > termout')
                if os.path.exists('fort.26')==True:
                    create_fit13(model2fit)
        # Compress results for supercomputer calculations
        if compress:
            destination = path.replace('list','execute')+'/'
            os.chdir(path)
            target   = system+'/'+model+'/sims/'+simtest+'/'+test+'/'+distortion
            filename = target.replace('/','--')
            os.system('tar -zcvf '+filename+'.tar.gz '+target+'/')
            os.system('rm -rf '+target+'/')
            os.system('mkdir -p '+destination)
            os.system('mv '+filename+'.tar.gz '+destination)
