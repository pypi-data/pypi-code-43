import velplot,os,numpy

def fit_fort(fortfile,fit,error,illcond,pcvals,version):
    '''
    Do Voigt fitting and update model.
    '''
    opfile = open('fitcommands','w')
    if error:
        opfile.write('e\n')             # Run fit command + enter
    else:
        opfile.write('f\n')             # Run fit command + enter
    if pcvals:                          # If development tools called...
        if illcond:
            opfile.write('il\n')
        opfile.write('\n')              # ...used default setup -> enter only
    opfile.write('\n')                  # Used default parameter (logN) -> enter only
    opfile.write(fortfile+'\n')   # Insert fort file name + enter
    opfile.write('n\n')                 # Do not plot the region + enter
    opfile.write('\n')                  # Do not fit more line and exit VPFIT -> enter only
    opfile.close()

    os.system(version+' < fitcommands')

    if fit or illcond:
    
        ''' Read fort.13 and store header and first guesses '''
    
        i,flag,header,guesses = 0,0,[],[]
        line13 = [line.replace('\n','') for line in open(fortfile,'r')]
        while i < len(line13):
            if '*' in line13[i]:
                flag = flag+1
            if '*' not in line13[i] and flag==1:
                header.append(line13[i]+'\n')
            if '*' not in line13[i] and flag==2:            
                guesses.append(line13[i]+'\n')
            i = i + 1
    
        ''' Take results from fort.18 '''
    
        i,results = 0,[]
        line18 = numpy.loadtxt('fort.18',dtype='str',delimiter='\n')
        for i in range(len(line18)-1,0,-1):
            if 'chi-squared' in line18[i]:
                a = i + 2
                break
        for i in range(a,len(line18)):
            results.append(line18[i]+'\n')
            if len(line18[i])==1:
                break
                
        ''' Update fort.13 and embed results from fort.18 '''
    
        fort = open(fortfile,'w')
        for line in ['*\n']+header+['*\n']+results+guesses:
            fort.write(line)
        fort.close()
        
