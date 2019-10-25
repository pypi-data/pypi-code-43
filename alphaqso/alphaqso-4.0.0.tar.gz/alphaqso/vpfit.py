import os,sys,numpy,shutil

def isfloat(value):
    """
    Check if string is float.
    """
    try:
      float(value)
      return True
    except ValueError:
      return False

def vpfit_setup(vpfit,instrument=None,chisq=1.E-5,no_alpha=False,atomdir=None,vpfsetup=None,copy=False):
    """
    VPFIT settings

    Note
    =====
    If running on the NCI/Raijin cluster, the absolute path is the following:
    `/home/561/vxd561/ASTRO/code/vpfit10/vpfit`
    """
    # Get full path to VPFIT executable
    vpfit = os.path.abspath(vpfit) if os.path.exists(vpfit) else shutil.which(vpfit)
    # Get path to atomic data file
    if atomdir==None:
        pathdata = os.path.dirname(os.path.realpath(__file__)) + '/data/'
        atomdir  = pathdata + 'atom.dat'
        atomdir  = pathdata + 'atom_new.dat'       if '--newatom'   in sys.argv else atomdir
        atomdir  = pathdata + 'atom_murphy.dat'    if '--murphy'    in sys.argv else atomdir
        atomdir  = pathdata + 'atom_mgisotope.dat' if '--mgisotope' in sys.argv else atomdir
    else:
        atomdir  = os.path.abspath(atomdir)
    # Store atomic data file into array
    atom = make_atom_list(atomdir)
    # Get path to VPFIT setting file
    if vpfsetup==None:
        vpfsetup = 'vp_setup_king.dat' if '9.5-king' in vpfit else 'vp_setup_hires.dat' if instrument=='hires' else 'vp_setup_uves.dat'
    else:
        vpfsetup = os.path.abspath(vpfsetup)
    # Store VPFIT settings into array
    vpsetup = numpy.loadtxt(vpfsetup,dtype=str,delimiter='\n',comments='!')
    for i,row in enumerate(vpsetup):
        if 'NOVARS' in row and no_alpha:
            vpsetup[i] = 'NOVARS 3'
    if '9.5-king' not in vpfit:
        vpsetup = numpy.hstack((vpsetup,['chisqthres %.E 2 %.E'%(chisq,chisq)]))
    return vpfit,atom,os.path.abspath(atomdir),vpsetup,os.path.abspath(vpfsetup)

def make_atom_list(atompath):
    """
    Store data from atom.dat
    """
    atom = numpy.empty((0,6))
    atomdat = numpy.loadtxt(atompath,dtype='str',delimiter='\n')
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

def atomic_info(atom,atomid):
    """
    Find transition in atom list and extract information.

    Parameters
    ----------
    atomid : string
      Name of the transition, written as ion_wavelength.
    """
    pathdata = os.path.dirname(os.path.realpath(__file__)) + '/data/'
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
    opfile.write('\n')                  # ...used default setup -> enter only
    opfile.write('\n')                  # Used default selfeter (logN) -> enter only
    opfile.write('%s\n'%fort)           # Insert fort file name + enter
    opfile.write('\n')                  # Plot the fitting region (default is yes) -> enter only
    if nregs>1:                         # If more than one transitions...
        opfile.write('\n')              # ...select first transition to start with (default)
    opfile.write('as\n\n\n')
    for line in range(nregs):
        opfile.write('\n\n\n\n')
    opfile.write('n\n\n')
    opfile.close()
