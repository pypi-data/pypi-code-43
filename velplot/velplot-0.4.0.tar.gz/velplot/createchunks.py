import velplot,os,numpy

def create_chunks(fortfile,pcvals,version,cont):
    '''
    Generate data chunk for each fitted region.

    Parameters
    ----------
    fortfile : str
      Path to input fort.13 or fort.26 file.
    pcvals : bool
      Flag to check if pcvals command in vp_setup.dat
    version : str
      VPFIT executable filename
    '''
    opfile = open('fitcommands','w')
    opfile.write('d\n')                 # Run display command + enter
    if pcvals:                          # If development tools called...
        opfile.write('\n')              # ...used default setup -> enter only
    opfile.write('\n')                  # Used default selfeter (logN) -> enter only
    opfile.write(fortfile+'\n')         # Insert fort file name + enter
    for line in velplot.table1:
        if cont and '.fits' in line[0]:
            opfile.write('\n')
    opfile.write('\n')                  # Plot the fitting region (default is yes) -> enter only
    if len(velplot.table1)>1:           # If more than one transitions...
        opfile.write('\n')              # ...select first transition to start with (default)
    opfile.write('as\n\n\n')
    for line in velplot.table1:
        opfile.write('\n\n\n\n')
    #if len(velplot.table1)>1:           # If more than one transitions...
    #    opfile.write('\n')              # ...select first transition to start with (default)
    opfile.write('n\n\n')
    opfile.close()
    try:
        os_cmd = version+' < fitcommands > termout'
        if os.system(os_cmd) != 0:
            raise Exception('%s does not exist'%version)
    except:
        if 'Zero wavelength range' in open('termout').read():
            print('\n\tERROR: A fitting region has no available data! Check your spectrum and/or model.\n')
        else:
            print("""\n\tThere is a problem creating the chunks. Try the following --cont argument and check that the path to data files in header is valid.\n""")
        quit()
    output = numpy.loadtxt('termout',dtype='str',delimiter='\n')
    for i in range(len(output)):
        if 'Statistics for each region :' in output[i]:
            i,k = i+2,0
            while 'Plot?' not in output[i]:
                velplot.header[k,-4] = 'n/a' if '*' in output[i].split()[2] else '%.4f'%(float(output[i].split()[2]))
                velplot.header[k,-3] = 'n/a' if '*' in output[i].split()[2] else '%.4f'%(float(output[i].split()[2])/float(output[i].split()[4]))
                velplot.header[k,-2] = output[i].split()[3]
                velplot.header[k,-1] = output[i].split()[4]
                k = k + 1
                i = i + 2
    if os.path.exists('chunks')==False:
        os.system('mkdir chunks')
        
    os.system('mv vpfit_chunk* chunks/')
    os.system('rm fitcommands termout')
