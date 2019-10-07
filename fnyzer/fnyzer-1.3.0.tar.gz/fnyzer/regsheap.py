from __future__ import division, print_function
from itertools import product
import numpy as np
import heapq
import statsmodels.api as sm
import copy

#import warnings

class regsheap:
    """
    Create and store in a priority queue regions that represent a piecewise
    linear approximation of a function. Such regions comply with the format
    required for flexible nets.

    See hillpwlnet.py for an example of use.

    Note:
      - the function to be approximated is assumed to depend just on the marking m
      - the resulting approximation is assigned to just one intensity arc
    """

    def __init__(self, proregs, func, parnames, maxmsr = 1e-2, maxregs = 10, 
                 sampoints = 10, pref = 'reg'):
        """
        Create a a priority queue with regions to be associated with the 'regs'
        of a flexible net and with an intensity handler.

        Parameters:
        proregs: Dictionary with the initial borders of the regions (see exaple above)
        func: The dynamics of the regions are given by func which is approximated by a 
              linear function.
              The function func takes a matrix as an argument, the first column of the
              matrix is a constant vector 1 and the rest of the columns of the matrix
              are the paramenters of the function sorted alphabetically.
        parnames: Dictionary that associates names of the elements connected with the
              intensity handler to the names of the parameters used in the linear
              expression.
              parnames['lap'] refers to the name of the variable to which the linear
                 regression is assigned (usually sarc).
              parnames['place'] refers to the name of the paramenter associated 
                 to sedge ('place', 'shandler')
              The linear dynamics of each regions are obtained by linear
              regression (ordinary least squares). Once the regions are created, the 
              region with maximum msr (mean squared residual) is split.
        maxmsr, maxregs: The regions are further split until maxregs is reached or 
              the msr of every region is lower than maxmsr.
        sampoints: Number of points to be used in each dimension for the linear 
              approximation (regression)
        pref: The names of the regions are prefixed with pref
        """
        self.heap = self.createregs(proregs, func, parnames, sampoints, pref) # Initial heap
        while len(self.heap)<maxregs and -heapq.nsmallest(1,self.heap)[0][0]> maxmsr:
            spregion = heapq.heappop(self.heap) # Split this region
            auxproreg = spregion[2] # borders to split
            print("Splitting region with borders:", str(auxproreg))
            newproregs = {key:[auxproreg[key][0], (auxproreg[key][0]+auxproreg[key][1])/2.0, auxproreg[key][1]] for key in auxproreg}
            auxheap = self.createregs(newproregs, func, parnames, sampoints, spregion[1])
            self.heap = list(heapq.merge(self.heap, auxheap))
    
    def createregs(self, proregs, func, parnames, sampoints = 10, pref = 'reg'):
        """Create orthogonal regions on the marking according to the limits 
           specified in proregs"""
        localheap = []
        limits = {}
        for key in proregs.keys():
            limits[key] = [(key, proregs[key][i], proregs[key][i+1]) for i in range(len(proregs[key])-1)]
        for num, border in enumerate(product(*[limits[key] for key in limits])):
            regname = pref+'_'+str(num)
            regborders = {border[ind][0]:[border[ind][1],border[ind][2]] for ind in range(len(border))} # Border of the region expressed as a dictionary
            shdyn, msr = self.reglindyns(regborders, func, parnames, sampoints) # Linear dynamics in the region
            listborders = []  # Borders of the region expressed as a list of dictionaries
            for ind in range(len(border)):
                listborders.append("m['"+border[ind][0]+"'] >= "+str(border[ind][1]))
                listborders.append("m['"+border[ind][0]+"'] <= "+str(border[ind][2]))
            region = (-msr, regname, regborders, shdyn, listborders) # A region is a tuple of five components. msr is negated beacuse heap is ordered by <
            heapq.heappush(localheap, region)
        return localheap
    
    def reglindyns(self, regborders, func, parnames, sampoints):
        """Create a list containing a string with the linear dynamics of the
           regions contained in regborders.
           Return that list and mean squared residual"""
        def strs(num):
            return ' '+str(num) if num < 0 else ' +'+str(num)
        linsp = {key:np.linspace(regborders[key][0], regborders[key][1], sampoints) for key in regborders}
        for it, key in enumerate(sorted(linsp)):
            aux = [e[it] for e in product(*[linsp[key] for key in sorted(linsp)])]
            if it == 0:
                X = np.ones(len(aux))
            X = np.column_stack((X, aux))
        fobs = func(X)
        results = sm.OLS(fobs, X).fit()
        if min(results.fittedvalues)<0: # http://statsmodels.sourceforge.net/stable/generated/statsmodels.regression.linear_model.RegressionResults.html?highlight=regressionresults
#            warnings.warn("Warning: Negative predicted value for region with borders: "+str(regborders))
            print("Warning: Negative predicted value for region with borders:", str(regborders))
        ks = results.params
        cppnames = copy.deepcopy(parnames)
        auxstr = cppnames.pop('lap')+' == ' # assign linear function to this parameter
        auxstr += strs(ks[0]) # Intercept
        for i, key in enumerate(sorted(cppnames)):
            auxstr += strs(ks[i+1])+'*'+cppnames[key]
        msr = results.ssr/results.nobs # Mean squared residual
        return [auxstr], msr
        
    def regborders(self):
        """Return dictionary of borders in flexible net format"""
        return {reg[1]:reg[4] for reg in self.heap}
    
    def regnames(self):
        """Return list of names of regions"""
        return [reg[1] for reg in self.heap]

    def shdyns(self):
        """Return dictionary of dynamics for intensity handlers"""
        return {reg[1]:reg[3] for reg in self.heap}

