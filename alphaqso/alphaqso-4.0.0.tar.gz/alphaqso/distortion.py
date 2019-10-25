import os,sys,numpy,re,math

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
        distlist = numpy.hstack((numpy.arange(slope,distmax+0.001,+distsep),
                                 numpy.arange(slope,distmin-0.001,-distsep)))
        distplot = sorted(numpy.delete(distlist,0))
    return distlist,distplot

def getshift(left,right,slope,qso=None,sample=None,explist=None,settings=None,shape=False,whitmore=False,stdev=0):
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
    # Load files
    pathdata = os.path.dirname(os.path.realpath(__file__)) + '/data/'
    explist  = explist if explist!=None else 'uvesexp.dat' if 'SQ12' in sample else 'hiresexp.dat'
    explist  = numpy.genfromtxt(explist,names=True,dtype=object,comments='!')
    settings = pathdata+'settings.dat' if settings==None and 'SQ12' in sample else settings
    settings = numpy.genfromtxt(settings,names=True,dtype=object,comments='!',skip_header=4)
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
    if 'SQ12' in sample:
        # If Whitmore distortion model and non-zero slope
        if whitmore and slope!=0:
            # Calculate the shift based on the Whitmore model
            shift = uves_whitmore(middle,slope)
        # If selected system is using UVES SQUADER data
        else:
            # Search position of the quasar in the list of UVES exposures (explist)
            pos = numpy.where(explist['name']==qso.encode())[0][0]
            # Initialize total shift and exposure time parameter
            sumshift = sumcount = 0
            # Loop in the list of UVES exposures until break is called
            for l in range (pos,len(explist)):
                # If quasar name in list different from the selected system
                if explist['name'][l]!=qso.encode():
                    # Break the loop
                    break
                # For each exposure, loop over all the existing settings
                for k in range(len(settings)):
                    # Condition 1: Central wavelength of setting same than the exposure
                    cond1 = settings['cent'][k]==explist['cent'][l]
                    # Condition 2: Optical arm of setting same than the exposure
                    cond2 = settings['arm'][k]==explist['arm'][l]
                    # Condition 3: Optical mode of setting same than the exposure
                    cond3 = settings['mode'][k]==explist['mode'][l]
                    # If the 3 conditions are satisfied
                    if cond1==cond2==cond3==True:
                        # Define starting wavelength (in Angstrom) from value in the list of settings (in nm)
                        wbeg  = 10*float(settings['TS_min'][k])
                        # Define central wavelength (in Angstrom) from value in the list of settings (in nm)
                        cent  = 10*float(settings['cent'][k])
                        # Define ending wavelength (in Angstrom) from value in the list of settings (in nm)
                        wend  = 10*float(settings['TS_max'][k])
                        # Break the loop in the list of settings as the correct setting has been matched
                        break
                # If creating simulated spectrum and expind option used, define a random slope based on exposure settings
                if stdev!=0:
                    # If no slope already attributed or exposure not yet tabulated in shifts
                    if len(shifts)==0 or str(explist['dataset'][l]) not in shifts[:,0]:
                        # Determine slope for this exposure using gaussian distribution
                        slope = numpy.random.normal(slope,stdev)
                        # Store the exposure name and associated slope value calculated in shifts
                        shifts = numpy.vstack((shifts,[str(explist['dataset'][l]),str(slope)]))
                    # If exposure already tabulated in shifts
                    if len(shifts)>0 and str(explist['dataset'][l]) in shifts[:,0]:
                        # Find index position of this exposure in shifts
                        idx   = numpy.where(shifts[:,0]==explist['dataset'][l])[0][0]
                        # Extract previously calculated and stored slope value for this exposure
                        slope = float(shifts[idx,1])
                if explist['arm'][l]==b'BLUE' and wbeg < left and right < wend:
                    sumshift = sumshift + numpy.sqrt(float(explist['exptime'][l])) * uves_slope(cent,middle,slope)
                    sumcount = sumcount + numpy.sqrt(float(explist['exptime'][l]))
                    blflag = 1
                if explist['arm'][l]==b'RED' and wbeg < left and right < wend:
                    sumshift = sumshift + numpy.sqrt(float(explist['exptime'][l])) * uves_slope(cent,middle,slope)
                    sumcount = sumcount + numpy.sqrt(float(explist['exptime'][l]))
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
    if ('CH01' or 'SA03') in sample:
        if slope==0:
            shift = 0
        elif whitmore and shape=='amplitude':
            shift = shift + hires_amplitude(left,right,slope)
        elif whitmore and shape=='slope':
            shift = shift + hires_slope(middle,slope)
        elif 'SA03' in sample:
            pos = numpy.where(numpy.logical_and(explist['name']==qso.encode(),explist['sample']==sample.encode()))[0][0]
            sumshift = sumcount = 0
            for l in range (pos,len(explist)):
                if explist['name'][l]!=qso.encode():
                    break
                wbeg = float(explist['blue'][l])
                cent = float(explist['cent'][l])
                wend = float(explist['red'][l])
                if wbeg < left and right < wend:
                    sumshift = sumshift + numpy.sqrt(float(explist['exptime'][l])) * uves_slope(cent,middle,slope)
                    sumcount = sumcount + numpy.sqrt(float(explist['exptime'][l]))
            shift = sumshift / sumcount
    return '{0:.4f}'.format(float(shift)/1000.)
