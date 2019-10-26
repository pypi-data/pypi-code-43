import os,sys,numpy
from astropy.io import fits

def check_file_path(input_files):
    for i,input_file in enumerate(input_files):
        if input_file!=None:
            assert os.path.exists(input_file), 'File not found at %s not found. Abort.'%input_file
            input_files[i] = os.path.abspath(input_file)
    return input_files

def get_coddam(sheetname,dbkey):
    sheet_id = {'qsolist':26063364,'dipole':1491749328,'curlist':175866280,'publist':353421904,'distres':684542576}
    url = "https://docs.google.com/spreadsheets/d/{0}/export?format=csv&gid={1}".format(dbkey,sheet_id[sheetname])
    r = requests.get(url)
    sio = io.StringIO( r.text, newline=None)
    output = read_csv(sio,skiprows=1)
    return output

def get_fit_name(instrument,mode,sample):
    """
    Get fitting repository name. DEPRECATED!
    """
    name = instrument + '-'
    name = name + 'v10_slope'  if instrument=='hires'        else name
    name = name + 'v10_all'    if instrument=='uves'         else name
    name = name + '_jw'        if '--whitmore' in sys.argv   else name
    name = name + '_prev'      if '--previous' in sys.argv   else name
    name = name + '-' + mode   if mode in ['global','model'] else name
    name = name + '-' + sample if sample!=None               else name
    return name

def get_test_name(instrument=None,distsep=None,slope=0,chisq=1.E-5,vpversion='10',arm=None,shape='slope',
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

def get_path_to_model(system,target_system,simulation,whitmore,database,stdev,mid_slope,snr,target_model,selection):
    simtest,model = None,None
    if simulation and system==target_system and target_system not in outliers and (database['whitmore'][i]=='yes')==whitmore:
        sim = 'sim2' if stdev!=0 else 'sim1'
        slope = float(database['%s mid%02i'%(sim,100*stdev)][i]) if mid_slope==None else mid_slope
        tilt = '0.000' if round(slope,3)==0 else 'm%.3f'%abs(slope) if slope<0 else 'p%.3f'%abs(slope)
        simtest = 'complex_%s_%.2f'%(tilt,stdev)
        simtest = simtest if snr==None else simtest+'_snr%.E'%snr
        model = database['%s model'%sim][i] if target_model==None else target_model
        model = 'model-%.1f'%float(model)
    if target_system!=None and target_system==system:
        model = target_model if selection==None else database[selection][i]
        model = None if model==None else 'model-%.1f'%float(model)
    if selection!=None and database[selection][i]!='-':
        model = database[selection][i]
        model = 'model-%.1f'%float(model)
    if instrument==database['instrument'][i].lower():
        model = 'model-7.1'
    return simtest,model

def get_system_list():
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
            if simulation:
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

def read_spec(specfile):
    '''
    Read spectrum and extract wavelength and flux dataset.
    '''
    datatype = specfile.split('.')[-1]
    wavefile = specfile.replace('.fits','.wav.fits')
    if datatype=='fits' and os.path.exists(wavefile)==True:
        fh = fits.open(wavefile)
        hd = fh[0].header
        specwa = fh[0].data
        fh = fits.open(specfile)
        hd = fh[0].header
        specfl = fh[0].data        
    elif datatype=='fits':
        fh = fits.open(specfile)
        hd = fh[0].header
        d  = fh[0].data
        if ('CTYPE1' in hd and hd['CTYPE1'] in ['LAMBDA','LINEAR']) or ('DC-FLAG' in hd and hd['DC-FLAG']=='0'):
            specwa = hd['CRVAL1'] + (hd['CRPIX1'] - 1 + numpy.arange(hd['NAXIS1']))*hd['CDELT1']
        else:
            specwa = 10**(hd['CRVAL1'] + (hd['CRPIX1'] - 1 + numpy.arange(hd['NAXIS1']))*hd['CDELT1'])
        if len(d.shape)==1:
            specfl = d[:]
            specer = None
        else:
            specfl = d[0,:]
            specer = d[1,:]
    else:
        sp = numpy.loadtxt(specfile,comments='!')
        specwa = sp[:,0]
        specfl = sp[:,0]
        specer = sp[:,2]
    return specwa,specfl,specer
