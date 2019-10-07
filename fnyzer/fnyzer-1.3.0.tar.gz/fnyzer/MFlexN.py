from __future__ import division, print_function
from fnyzer import FlexN
from fnyzer import GFlexN
from fnyzer import LFlexN
from copy import deepcopy
import time
import pickle

class MFlexN:
    """Class for Model Pedrictive Control (MPC) of a Flexible Net"""
    #  The same net structure will be used for all the steps

    def __init__(self, netdata):
        """MPC options:
         firstinlen: length of the first interval, i.e., period (this is also
             the minimum time length allowed for flexible intervals)
         numsteps:   number of optimization steps, i.e., number of LFlexN to
             optimize. It holds finaltime=numsteps*firstinlen
         maxnumins:  maximum number of intervals (including first interval),
             i.e., horizon in terms of number of intervals, of each step
             (it has to be >= 1)
         flexins:    True if you want intervals to stretch until they cover up
             to the final time. False implies intervals have length equal to
             firstinlen
         In addition to these values, finaltime (overall final time of the
             optimization (not of the step)) will be computed
        """
        # Overall final time of the optimization        
        netdata['options']['mpc']['finaltime'] = (
            netdata['options']['mpc']['numsteps']
            * netdata['options']['mpc']['firstinlen']) 
        # Default options
        for opt in FlexN.defoptions:
            if opt not in netdata['options']:
                netdata['options'][opt] = FlexN.defoptions[opt]
        if (netdata['options']['writexls'] 
                and 'xlsfile' not in netdata['options']):
            netdata['options']['xlsfile'] = netdata['name'] + ".xls"
        if (netdata['options']['savenet']
                and 'netfile' not in netdata['options']):
             netdata['options']['netfile']  = netdata['name'] + ".pkl"
        # copy dict netdata (it will be used as template for all the steps)             
        self.netdata = netdata 
        for key in netdata: # copy all net data to attributes
            setattr(self, key, netdata[key])
        self.lndata = [] # List of netdata, one per step
        self.lnets = [] # List of LFlexN, one per step
        """MPC summary net (sumnet) with the first interval of every step"""
        numsteps = self.options['mpc']['numsteps']
        firstinlen = self.options['mpc']['firstinlen']
        if numsteps > 1:
            self.sumnet = LFlexN({
                'mappers': [{'net':deepcopy(self.netdata), 
                'thetas': numsteps*[firstinlen]}], 
                'options':deepcopy(self.options),
                'solver': self.solver
                })
            # Dictionary to store info about the results and performance of the
            # program                                           
            self.sumnet.info = {'perf': {}, 'result': {}} 
        else:
            self.sumnet = -1 # This will be overwritten by optimmpc
        

    def optimmpc(self):
        """Optimize objective function according to MPC"""
        lmodels = [] # List of programming problems, one per step
        for k in range(self.options['mpc']['numsteps']):
            print('Step: ', k)
            currenttime = k*self.options['mpc']['firstinlen']
            ndata = deepcopy(self.netdata) # new data for net at step k
            if k > 0: # Set initial marking and actions according previous final marking, actions and resets
                if isinstance(self.lnets[k-1], LFlexN): # Get previous markings, actions and intensities
                    prevm = {pl:self.lnets[k-1].qnets[0].places[pl].m for pl in ndata['places']}
                    prevavm = {pl:self.lnets[k-1].qnets[0].places[pl].avm for pl in ndata['places']}                    
                    prevat= {tr:self.lnets[k-1].qnets[0].trans[tr].at for tr in ndata['trans']}
                    prevl= {tr:self.lnets[k-1].qnets[0].trans[tr].l for tr in ndata['trans']}                    
                    prevavl= {tr:self.lnets[k-1].qnets[0].trans[tr].avl for tr in ndata['trans']}                    
                else:
                    prevm = {pl:self.lnets[k-1].places[pl].m for pl in ndata['places']}
                    prevavm = {pl:self.lnets[k-1].places[pl].avm for pl in ndata['places']}                    
                    prevat= {tr:self.lnets[k-1].trans[tr].at for tr in ndata['trans']}
                    prevl= {tr:self.lnets[k-1].trans[tr].l for tr in ndata['trans']}                    
                    prevavl= {tr:self.lnets[k-1].trans[tr].avl for tr in ndata['trans']}                                        
                for pl in ndata['places']: # Set initial marking and actions to final marking and actions of first interval of previous step                    
                    ndata['places'][pl] = max(0, prevm[pl]) # Use max() to avoid potential small negative values
                for tr in ndata['trans']:
                    ndata['trans'][tr]['a0'] = max(0, prevat[tr]) # Use max() to avoid potential small negative values
                if 'resets' in self.netdata: # Check if there are resets to handle
                    if 'm0cons' not in ndata:
                        ndata['m0cons'] = []
                    if 'a0cons' not in ndata:
                        ndata['a0cons'] = []
                    for reset in self.netdata['resets']: # Remark: Iterating over self.netdata instead of ndata to decrease ntimes 
                        if ('ntimes' not in reset) or (reset['ntimes']>=1): # Check if the reset is still active
                            dictvars = {
                                'time':currenttime, 'm':prevm, 'avm':prevavm, 
                                'at':prevat, 'l':prevl, 'avl':prevavl
                                }
                            if eval(reset['cond'], dictvars):
                                if 'ntimes' in reset:
                                    reset['ntimes'] -= 1
                                if 'm0cons' in reset: # If there are initial markings to reset
                                    for con in reset['m0cons']: # Process all constraints
                                        connum = deepcopy(con)
                                        for pl in ndata['places']:
                                            connum = connum.replace("m['"+pl+"']", str(prevm[pl])) # Replace by final previous marking
                                            if "m0['"+pl+"']" in connum: # Remove initial marking assignment of places in the constraint
                                                ndata['places'][pl] = None
                                        ndata['m0cons'].append(connum)
                                if 'a0cons' in reset: # If there are initial actions to reset
                                    for con in reset['a0cons']: # Process all constraints
                                        connum = deepcopy(con)
                                        for tr in ndata['trans']:
                                            connum = connum.replace("at['"+tr+"']", str(prevat[tr])) # Replace by final previous action
                                            if "a0['"+tr+"']" in connum: # Remove initial action assignment of transitions in the constraint
                                                ndata['trans'][tr]['a0'] = None
                                        ndata['a0cons'].append(connum)
            thetas = self.computethetas(k)
            numins = len(thetas) if isinstance(thetas, list) else 1
            ndata['theta'] = thetas
            # Include time independent and time dependent constraints
            if 'extracons' in ndata and ndata['extracons']: # There are extra contraints to include
                ndata['extracons'] = ndata['extracons'][numins-1] # Extra constraints for numins number of intervals
            if 'textracons' in ndata and ndata['textracons']: # There are timed contraints to handle
                for tcons in ndata['textracons'][numins-1]:
                    if eval(tcons['cond'], {'time':currenttime}):
                        if 'extracons' in ndata:
                            ndata['extracons'].append(tcons['cons'])
                        else:
                            ndata['extracons'] = [tcons['cons']]
            if not isinstance(thetas, list): # Just one interval in this step
                if isinstance(ndata['obj'], list):
                    ndata['obj'] = ndata['obj'][0] # Objective function for net with just one iterval
                self.lndata.append(deepcopy(ndata))
                self.lnets.append(GFlexN(self.lndata[k]) if 'regs' in ndata else FlexN(self.lndata[k]))
            else: # Several intervals in this step
                ndatain = {'mappers':[{'net':ndata, 'thetas':thetas}]}  # Net data for LFlexN
                ndatain['obj'] = ndata['obj'][numins-1] # Objective function for net with len(thetas) itervals
                ndatain['solver'] = ndata['solver']
                ndatain['options'] = ndata['options']
                if 'extracons' in ndata:
                    ndatain['extracons'] = ndata['extracons']
                self.lndata.append(deepcopy(ndatain))
                self.lnets.append(LFlexN(self.lndata[k]))
            # Optimize step
            lmodels.append(self.lnets[k].optimtr())
            # Fill summary net sumnet
            if self.options['mpc']['numsteps'] > 1: # Copy first interval
                if hasattr(self.lnets[k], 'qnets'):
                    self.sumnet.qnets[k] = deepcopy(self.lnets[k].qnets[0])
                else:
                    self.sumnet.qnets[k] = deepcopy(self.lnets[k])
                # Overwrite tau0 and tauf to absolute time
                self.sumnet.qnets[k].tau0 = k*self.options['mpc']['firstinlen']
                self.sumnet.qnets[k].tauf = (k+1)*self.options['mpc']['firstinlen']
            else:
                self.sumnet = self.lnets[0]
        # Compute overall variables of summary net sumnet
        if self.options['mpc']['numsteps'] > 1:
            Qnet = self.sumnet.Qnets[0] 
            vdido = GFlexN.vdimdomtr if hasattr(Qnet,'regs') else FlexN.vdimdomtr
            for var in vdido:
                auxQdict = getattr(Qnet, vdido[var]['dim'])
                if vdido[var]['Qtype'] == 'ini': # Initial value
                    auxqdict = getattr(self.sumnet.qnets[0], vdido[var]['dim'])
                    for item in auxQdict:
                        setattr(auxQdict[item], var, getattr(auxqdict[item], var))
                elif vdido[var]['Qtype'] == 'fin': # Final value
                    auxqdict = getattr(self.sumnet.qnets[-1], vdido[var]['dim'])
                    for item in auxQdict:
                        setattr(auxQdict[item], var, getattr(auxqdict[item], var))
                elif vdido[var]['Qtype'] == 'add': # Sum
                    for item in auxQdict:
                        suma = 0
                        for k in range(self.options['mpc']['numsteps']):
                            auxqdict = getattr(self.sumnet.qnets[k], vdido[var]['dim'])     
                            suma += getattr(auxqdict[item], var)
                        setattr(auxQdict[item], var, suma)
                elif vdido[var]['Qtype'] == 'av': # Average
                    for item in auxQdict:
                        ave = 0
                        for k in range(self.options['mpc']['numsteps']):
                            auxqdict = getattr(self.sumnet.qnets[k], vdido[var]['dim'])     
                            ave += getattr(auxqdict[item], var)*self.sumnet.mappers[0]['thetas'][k]
                        setattr(auxQdict[item], var, ave/sum(self.sumnet.mappers[0]['thetas']))
            self.sumnet.objval = [lnet.objval for lnet in self.lnets]
        else:
            self.sumnet.objval = self.lnets[0].objval
        return lmodels

    def optimize(self):
        """Optimize"""
        ttic = time.time()
        model = self.optimmpc()
        self.sumnet.info['perf']['Wall time[total]'] = time.time()-ttic
        """Process options"""    
        """Print model"""
        if 'printmodel' in self.options and self.options['printmodel']:
            for idx, mod in enumerate(model):
                print('Step: ', idx)
                mod.pprint()
        """Print variables, i.e., result"""
        if 'printres' in self.options and self.options['printres']:
            for idx, nt in enumerate(self.lnets):
                print('Step: ', idx)
                nt.printres()
        """Save net object to file"""
        if 'savenet' in self.options and self.options['savenet']:
            output = open(self.options['netfile'], 'wb')
            pickle.dump(self, output)
            output.close()
        """Plot variables"""
        if 'plotres' in self.options and self.options['plotres']:
            self.plotres()
        """Write spreadsheet"""
        if 'writexls' in self.options and self.options['writexls']:
            self.writexls(self.options['xlsfile'])
        """Return model"""
        return model
            
    def computethetas(self, k):
        """Compute lengths of the time intervals for step k"""
        firstinlen = self.options['mpc']['firstinlen']
        maxnumins = self.options['mpc']['maxnumins']
        flexins = self.options['mpc']['flexins']
        fintime = self.options['mpc']['finaltime']
        initime = k*self.options['mpc']['firstinlen'] # initial time of current step

        thetas = [firstinlen]
        if maxnumins > 1:
            if flexins and fintime >= initime + maxnumins*firstinlen:
                thetas.extend((maxnumins-1)*[(fintime-initime-firstinlen)/(maxnumins-1)])
            else: # Not enough time left for flexible intervals or flexins = False
                nlains = min([maxnumins-1, int(round((fintime-initime-firstinlen)/firstinlen))])  # Number of look ahead intervals
                thetas.extend(nlains*[firstinlen])

        return thetas if len(thetas)>1 else thetas[0]
            
    def writexls(self, xlsfile):
        """Write results to spreadsheet file xlsfile"""
        self.sumnet.info['result'] = deepcopy(self.lnets[0].info['result'])
        for key in self.lnets[0].info['perf']:
            self.sumnet.info['perf'][key] = sum(self.lnets[k].info['perf'][key] 
                                                for k in range(self.options['mpc']['numsteps']) 
                                                if key in self.lnets[k].info['perf']) # Some keys might not be in all lnets, eg. 'Python processor time[wl,wu,W]' in unguarded nets
        wb = self.sumnet.genxlsdata(wb=None, namesh='MPC', writeinfo=True)
        if self.options['mpc']['numsteps'] > 1:        
            for step, lnet in enumerate(self.lnets):
                wb = lnet.genxlsdata(wb, namesh='Step_'+str(step), writeinfo=False, initau=step*self.options['mpc']['firstinlen'])
        wb.save(xlsfile)
        
    def plotres(self, plotvars = None, periods = 'all'):
        """Plot results"""
        if self.options['mpc']['numsteps'] > 1:
            self.sumnet.plotres(plotvars, periods)
            
