import os,numpy,re
from .utils import read_spec,check_file_path
from .forthandle import create_fit13
from .vpfit import vpfit_commands,vpfit_setup
from .distortion import getshift
from .constants import *

def create_simulated_model(path,vpfit,instrument,qso,sample,slope,snr,explist=None,settings=None,shape='slope',chisq=1.E-5,atomdir=None,vpfsetup=None,expind=False):

    # Get absolute path for further calls
    explist,settings,atomdir,vpfsetup = check_file_path([explist,settings,atomdir,vpfsetup])

    # Extract VPFIT information
    vpfit,atom,atomdir,vpsetup,vpfsetup = vpfit_setup(vpfit,instrument,no_alpha=True,copy=True,atomdir=atomdir,vpfsetup=vpfsetup)
        
    # Copy transition list, fort.18 and fort.26 files in model folder
    path = os.path.abspath(path)
    os.system('mkdir -p model/original model/data')
    os.system('cp %s/model/header.dat model/'%path)
    os.system('cp %s/model/turbulent.18 model/fort.18'%path)
    os.system('cp %s/model/turbulent.26 model/fort.26'%path)
    os.chdir('model')
    
    # Create fort_fit.13 from the fort.26 file and store contents in fort13 array
    create_fit13('fort',simulation=True)
    fort13 = open('fort_fit.13','r')
    fort13 = [line.strip() for line in fort13]
    os.system('rm fort*')
    
    # Initialise output files
    file1  = open('original/fort.13','w')
    file2  = open('turbulent.13','w')
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
            spec = line.split()[0].split('/')[-1]
            regs = numpy.vstack((regs,[float(line.split()[2]),float(line.split()[3])]))
            head = line.replace(line.split()[0],'data/'+spec)
            file1.write(head+'\n')
            file2.write(line.replace(line.split()[0],'data/spec%02i.txt'%(idx))+'\n')
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
    
    # Go to relevant folder and create symlink to data folder
    os.chdir('original')
    if os.path.exists('data'): os.system('rm data')
    os.system('ln -s %s/data'%path)
    
    # Prepare input commands to generate chunks on VPFIT
    hdin = numpy.loadtxt('../header.dat',dtype=str,delimiter='\n')
    vpfit_commands(len(hdin))
    
    # Set up VPFIT files
    os.system('cp %s atom.dat'%atomdir)
    numpy.savetxt('vp_setup.dat',vpsetup,fmt="%s")
    os.environ['ATOMDIR']=os.path.abspath('./atom.dat')
    os.environ['VPFSETUP']=os.path.abspath('./vp_setup.dat')
    # Run VPFIT and create chunks for original fort.13
    os.system(vpfit+' < fitcommands > termout')
    
    # Remove temporary files and move chunks to specific folder
    os.system('rm fitcommands termout')
    os.system('mkdir -p chunks/')
    os.system('mv vpfit_chunk* chunks/')
    
    # Extract data chunks, modify error array and add noise
    shifts = numpy.empty((0,2))
    os.chdir('../')
    wa,fl,er = read_spec('original/data/'+spec)
    
    # Create artificial data
    for ireg in range(len(regs)):
        data  = numpy.loadtxt('original/chunks/vpfit_chunk%03i.txt'%(ireg+1),comments='!')
        # Initialize non-used parameters called in getshift function
        shift = float(getshift(regs[ireg,0],regs[ireg,1],slope,qso,sample,explist,settings))
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
            ierror = error[j] if snr==None else 1./snr
            iflux  = flux[j] if ierror<0 else flux[j]+numpy.random.normal(0,ierror)
            ofile.write('{0:>21} {1:>25} {2:>30}\n'.format('%.13f'%iwave,'%.16f'%iflux,'%.16E'%ierror))
        ofile.close()
        
    if expind:
        outfile = open('shifts.dat','w')
        for i in range(len(shifts)):
            outfile.write(shifts[i,0]+'  '+shifts[i,1]+'\n')
        outfile.close()

