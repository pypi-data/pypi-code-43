from __future__ import division, print_function
import keyword
from fnyzer import netel # Net elements
import pyomo.environ as pyomo
from pyomo.environ import Constraint, Set
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
import time
import warnings
import re
from copy import deepcopy
import xlwt
import pickle

class FlexN:
    """Flexible Net"""
    # Default options
    defoptions = {
        'antype': 'tr', # Analysis type: 'tr' = transient, 'un' = untimed, 'st' = steady state, 'cst' = constant steady state
        'epsiloncompF': 1e-3, # epsilon used in the exit condition of computetdepF
        'epsilonLU': 1e-6, # epsilon to check if L[k] and U[k] are too close. If U[k]<=L[k]+epsilonLU, then k is removed from L, U, E, F and moved to Ec[k], and Fc[k] is set to the original U[k]    
        'maxitcompF': 20, # maximum number of iterations used in the exit condition of computetdepF
        'allsatoE': True, # If True all the intensity arcs will be included in E and the corresponding components of F will be set to float('-inf')
        'printres': False, # If True print values of variables and objective function
        'writexls': True, # If True write values of variables and objective function to the spreadsheet 'xlsfile'                  
        'writevars': 'all', # Variables to be written to the spreadsheet               
        'writeLUnegsa': False, # If False the LU components with one element and negative weight are not written
         # 'xlsfile': This key will be initialized in __init__  Name of the spreadsheet where the results will be written                  
        'savenet': True, # If True save net after optimization, i.e., with all the computed variables, as a Python object to file 'netfile'
        # 'netfile': This key will be initialized in __init__  Name of the file where the net object will be saved
        'printmodel': False, # If True print the programming problem (variables, constraints, objective function)
        # Default options for guarded nets
        'dsspe': {'type': 'shift', 'q': 20}, # Specification of the intervals ds=[0,d1,..,dq-1,dq] to linearize the products of variables are generated. type can be either 'exp':exponential or 'uni':uniform or 'rand':uniform+random or 'shift':slightly shifted uniform. 'q' is the number of intervals
        'epsilonalga': 1e-3, # epsilon used to set alphar and gammar according to avdeltar. 
                             # epsilonalga must be lower than 1/k where k is the number of regions of the partition with more number of regions
                             # avoid very low epsilonalga as it can cause numerical issues in the solver, e.g., the solver might violate a constraint by close to tolerance values
        'scalebs': 5, # Parameter to scale bounds wl and wu and W so that they are not tight
        # Default options for nets with intermediate states
        'plotres': False, #  If True plot the variables specified in 'plotvars'
        'plotvars': {'evm': 'all'} # Dictionary specifying the variables to plot, Eg: {'l0':['t1','t2'], 'evm': 'all'}
        }
                 
    """Variable names, dimension and domains for analysis without average values, e.g., untimed"""
    vdimdomun= {
        'm0'    : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # initial marking
        'm'     : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # final marking
        'mup'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # final mup
        'a0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # initial actions
        'sigma' : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # sigma = produced actions
        'at'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # at
        'l'     : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # lambda
        'l0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # lambda0
        'ae'    : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals},   # ae
        'dm'    : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals},   # d m
        'mue'   : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals},   # final mue
        'dl'    : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals}    # d lambda
        }
    
    """Variable names, dimension, domains and Qtypes for transient analysis"""
    """Qtype determines how the value of the variable is computed over a macro period:
       'ini' : the initial value of the macro period is taken
       'fin' : the final value of the macro period is taken
       'add' : the sum over the periods composing the macroperiod is taken
       'av'  : the average over the periods composing the macroperiod is taken"""
    vdimdomtr= {
        'm0'    : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'ini'},   # initial marking
        'm'     : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # final marking
        'mup'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # final mup
        'a0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'ini'},   # initial actions
        'sigma' : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'add'},   # sigma
        'at'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # at
        'l'     : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # lambda
        'l0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # lambda0
        'ae'    : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals, 'Qtype': 'add'},   # ae
        'dm'    : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'add'},   # delta m
        'mue'   : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # final mue
        'dl'    : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # d lambda
        'dsigma': {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'add'},   # d sigma
        'avm'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average marking
        'avmup' : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average mup
        'avmue' : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average mue
        'avdl'  : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average d lambda
        'avl'   : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average lambda
        'avsigma':{'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average sigma
        'avdsigma':{'dim': 'sarcs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average d sigma
        'avat'  : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average at
        'avae'  : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},    # average ae
        'avdm'  : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'}     # average d m
        }

    """Variable names, dimension and domains for steady state analysis"""
    vdimdomst= {
        'm0'    : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # initial marking
        'avm'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # average marking
        'avmup' : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # average mup
        'avmue' : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals},   # average mue
        'avdl'  : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals},   # average delta lambda
        'avl'   : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # average lambda
        'avsigmatau':{'dim':'trans','dom': pyomo.NonNegativeReals},   # average sigma
        'avattau':{'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # average at
        'avaetau':{'dim': 'vedges', 'dom': pyomo.NonNegativeReals},   # average ae
        'avdmtau':{'dim': 'varcs',  'dom': pyomo.NonNegativeReals},   # average delta m
        'a0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # initial actions
        'sigma' : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # sigma
        'at'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # at
        'l0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # lambda0
        'ae'    : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals},   # ae
        'dm'    : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals}    # delta m
        }

    def __init__(self, netdata):
        """Set default options for non specified options"""
        if 'options' not in netdata:
            netdata['options'] = {}
        self.options = deepcopy(netdata['options'])
        for opt in FlexN.defoptions:
            if opt not in self.options:
                self.options[opt] = FlexN.defoptions[opt]
        if self.options['writexls'] and 'xlsfile' not in self.options:
            self.options['xlsfile'] = netdata['name'] + ".xls"
        if self.options['savenet'] and 'netfile' not in self.options:
            self.options['netfile'] = netdata['name'] + ".pkl"
        """Attributes of the net object"""
        self.info = {'perf': {}, 'result': {}} # Dictionary to store info about the results and performance of the program
        """Places, transitions, handlers, arcs and edges"""
        self.places = {} # Dictionary of places
        self.trans = {}  # Dictionary of transitions
        self.vhandlers = {}  # Dictionary of event handlers
        self.varcs = {}  # Dictionary of event arcs
        self.vedges = {}  # Dictionary of event edges
        self.shandlers = {}  # Dictionary of intensity handlers
        self.sarcs = {}  # Dictionary of intensity arcs
        self.sedges = {}  # Dictionary of intensity edges

        """Matrices"""
        self.AB = {}     # The values of matrices A and B are not stored explicitly. 
                         # AB is a dictionary with {vh_n : value} where vh is the name of the
                         # event handler and n is the number of constraint associated to vh.
                         #  value is a dictionary such that:
                         #   value['expr'] is the linear constraint expressed with nicknames for variables of arcs and edges
                         #   value['nickae'] is a dictionary relating nicknames to arcs and edges
                         #   value['arcs'] is a list of nicknames associated to arcs
                         #   value['edges'] is a list of nicknames associated to edges
        self.Ys = {}     # Matrix Y_sigma is a dictionary, the keys are transition names, i.e., rows.
                         # The value of each key is a list of names of edges connected to the transition
        self.Zm = {}     # Matrix Z_m is a dictionary, the keys are place names, i.e., rows.
                         # The value of each key is a list of tuples (name of arc, 1|-1), 1(-1) for output(input) place
        self.CD = {}     # Same structure as AB
        self.Ym = {}     # Same structure as Ys
        self.Zl = {}     # Same structure as Zm
        self.m0cons = [] # Initial marking constraints
        self.mcons = []  # Final marking constraints for untimed and transient. Average marking constraints for steady state
        self.mbounds = []  # Bounds for the marking for every time instant
        self.a0cons = [] # Initial actions constraints
        self.l0cons = [] # Defaults intensity constraints
        self.actfplaces = [] # List of names of places with tokens forced to work at the end of the interval and in the untimed setting
        self.actavplaces = [] # List of names of places with tokens forced to work over the time interval
        self.exftrans =[] # List of names of transitions with produced actions forced to be executed at the end of the interval and in the untimed setting
        self.exavtrans =[] # List of names of transitions with actions forced to be executed instantaneously
        self.Ec = []
        self.Fc = []
        self.E = [] 
        self.F = []
        self.L = []
        self.U = []
        """Preprocess net data"""
        upddata = deepcopy(netdata) # Auxiliary dictionary to update data
        places=upddata['places'] if 'places' in upddata else []
        trans=upddata['trans'] if 'trans' in upddata else []
        vhandlers=upddata['vhandlers'] if 'vhandlers' in upddata else []
        shandlers=upddata['shandlers'] if 'shandlers' in upddata else []
        #Evaluate values that can be equal to 'all'
        if 'actfplaces' in upddata:
            if upddata['actfplaces'] == 'all':
                upddata['actfplaces'] = list(places.keys())
        if 'actavplaces' in upddata:
            if upddata['actavplaces'] == 'all':
                upddata['actavplaces'] = list(places.keys())
        if 'exftrans' in upddata:
            if upddata['exftrans'] == 'all':
                upddata['exftrans'] = list(trans.keys())
        if 'exavtrans' in upddata:
            if upddata['exavtrans'] == 'all':
                upddata['exavtrans'] = list(trans.keys())
        """Add places, transitions, vhandlers and shandlers"""
        if places:
            for pl in places:
                    self.addplace(pl, places[pl])
        if trans:
            for tr in trans:
                self.addtransition(tr, trans[tr])
        if vhandlers:
            for vh in vhandlers:
                self.addvhandler(vh, vhandlers[vh])
        if shandlers:
            for sh in shandlers:
                self.addshandler(sh, shandlers[sh])
        """Check if all intensity arcs must be included in E"""
        if self.options['allsatoE']:
            if 'E' not in upddata: # It is assumed that E is in upddata iff F is in uppdata (and have the same length)
                upddata['E'], upddata['F'] = [], []
            upddata['E'] = ([{sa:1} for sa in self.sarcs.keys()] 
                        +[{sa:-1} for sa in self.sarcs.keys()] + upddata['E'])
            upddata['F'] = (2*len(self.sarcs.keys())*[float('-inf')] 
                        + upddata['F']) # Initialize to -inf
        """Add rest of data"""
        for key in upddata:
            if key not in ['places', 'trans', 'vhandlers', 'shandlers', 'regs',
                           'parts', 'options']:
                setattr(self, key, upddata[key])

        
    def addplace(self, plname, info=None):
        """Create a place with name plname and info. 
           info can be either None, a number or a dictionary.
           If info is a nonnegative number, create equality constraint for initial marking equal to info.
           If info is a dictionary create attribute info in the place with that dictionary
           and create  equality constraint for initial marking 'm0', if 'm0' is a key of info.
           To establish bounds on m0 use self.m0cons"""
        self.places[plname] = netel.Place(plname)
        if isinstance(info, dict):
            if 'm0' in info:
                if info['m0'] is not None and info['m0'] >= 0:
                    self.places[plname].m0 = info['m0']
                info.pop('m0')
            if info:
                self.places[plname].info = info
        elif info is not None and info >= 0:
            self.places[plname].m0 = info

    def addtransition(self, trname, info=None):
        """Create a transition with name trname and info. 
           info can be either None or a dictionary.
           Create equality constraints for default intensity l0 and initial 
           actions a0 if the specified values are nonnegative.
           To establish bounds on l0 and a0 use self.l0cons and  self.a0cons"""        
        self.trans[trname] = netel.Transition(trname)
        if info is not None:
            if 'l0' in info and info['l0'] is not None and info['l0'] >= 0:
                self.trans[trname].l0 = info['l0']
                info.pop('l0')
            if 'a0' in info and info['a0'] is not None and info['a0'] >= 0:
                self.trans[trname].a0 = info['a0']
                info.pop('a0')
            if info:
                self.trans[trname].info = info

    def addvhandler(self, vhname, vhdata, **kwargs):
        """Create an event handler with name vhname, matrices given by vhdata, and optional attributes
         vhdata is a list [dd, r1, r2, ...] of at least two elements where dd is a dictionary
         with nicknames for all the variables associated to arcs and edges of the handler, and r* are strings 
         containing linear expressions relating those variables. Example of vhdata: 
         [{'a':('p1','v1'), 'b':('v1','p2'), 'c':('t1','v1')},'3*a - c == b', '-b <= 2*c', '2*b>=c'] """
        """Add event handler, arcs, edges. Update matrices Ys and Zm"""
        for key in vhdata[0]: 
            if vhdata[0][key][1] in self.trans: # Standard form for event edges (tran, vhandler)
                vhdata[0][key] = (vhdata[0][key][1], vhdata[0][key][0])
        self.vhandlers[vhname] = netel.Vhandler(vhname, vhdata)
        for key in kwargs:
            setattr(self.vhandlers[vhname], key, kwargs[key])
        for key in vhdata[0]:
            if key in keyword.kwlist:
                raise ValueError("Python keywords cannot be used as nicknames "
                    "in handlers. Keyword:'"+key+"', Handler:'"+vhname+"'")
            if vhdata[0][key][0] in self.trans: # Add new event edge
                trname = vhdata[0][key][0]
                self.addvedge((trname,vhname))
                self.vhandlers[vhname].cont.append(trname)
                self.vhandlers[vhname].edges.append(key)
                self.trans[trname].convh.append(vhname)
                if trname in self.Ys:
                    self.Ys[trname].append((trname,vhname))
                else:
                    self.Ys[trname] = [(trname,vhname)]
            elif vhdata[0][key][0] in self.places:#Add new event arc from place
                plname = vhdata[0][key][0]
                self.addvarc((plname,vhname)) 
                self.vhandlers[vhname].inp.append(plname)
                self.vhandlers[vhname].arcs.append(key)
                self.places[plname].outvh.append(vhname)
                if plname in self.Zm:
                    self.Zm[plname].append(((plname,vhname),-1))
                else:
                    self.Zm[plname] = [((plname,vhname),-1)]
            elif vhdata[0][key][1] in self.places: # Add new event arc to place                        
                plname = vhdata[0][key][1]
                self.addvarc((vhname,plname)) 
                self.vhandlers[vhname].outp.append(plname)
                self.vhandlers[vhname].arcs.append(key)
                self.places[plname].invh.append(vhname)
                if plname in self.Zm:
                    self.Zm[plname].append(((vhname,plname),1))
                else:
                    self.Zm[plname] = [((vhname,plname),1)]
            else:
                raise ValueError('Place or transition not found')
        """Update AB"""
        for idx,expr in enumerate(vhdata[1:]):
            self.AB[vhname+'_'+str(idx)] = {
                'expr':  expr, 
                'nickae':self.vhandlers[vhname].nickae,
                'arcs':  self.vhandlers[vhname].arcs,
                'edges': self.vhandlers[vhname].edges
                }

                    
    def addvarc(self, vaname, **kwargs): 
        """Create an event arc with name vaname and optional attributes"""
        self.varcs[vaname] = netel.Varc(vaname)
        for key in kwargs:
            setattr(self.varcs[vaname], key, kwargs[key])

    def addvedge(self, vename, **kwargs): 
        """Create an event edge with name vename and optional attributes"""
        self.vedges[vename] = netel.Vedge(vename)
        for key in kwargs:
            setattr(self.vedges[vename], key, kwargs[key])

    def addshandler(self, shname, shdata, **kwargs):
        """Create an intensity handler with guarded intensity arcs with name shname, matrices given by shdata, and optional attributes.
         shdata is a list [dd, comp1, comp2,..] of at least two elements where dd is a dictionary
         with nicknames for all the variables associated to arcs and edges of the handler, and 
         comps are the components containing linear expressions relating those variables.
         If comp is a string then it expresses linear relationships for unguarded intensity arcs.
         If comp is a dictionay the each key is a region, and each value is a list of strings expressing
         linear relationships for that region (it is assumed that all the arcs in a given string have the same guards).
         Example of shdata:
         [{'a': ('p1','s1'), 'x': ('s1','t1'), 'y': ('s1','t2'), 'z': ('s1','t3')}, 
                                                           'x==2*a', # unguarded arc
                                                           {'upr': ['2.1*a <= y', 'y <= 2.2*a'], 
                                                            'lor': ['1.1*a <= y', 'y <= 1.2*a']}, # guarded arc
                                                           'x == z']
        Matrices CD and CDg(CDg=constraints for guarded arcs) and dictionary sarcxguards are created"""
        """Add intensity handler, arcs, edges. Update matrices Ym and Zl"""
        for key in shdata[0]: 
            if shdata[0][key][1] in self.places: # Standard form for intensity edges (place, shandler)
                shdata[0][key] = (shdata[0][key][1], shdata[0][key][0])
        self.shandlers[shname] = netel.Shandler(shname, shdata)
        for key in kwargs:
            setattr(self.shandlers[shname], key, kwargs[key])
        for key in shdata[0]: 
            if key in keyword.kwlist:
                raise ValueError("Python keywords cannot be used as nicknames in handlers. Keyword:'"+key+"', Handler:'"+shname+"'")
            if shdata[0][key][0] in self.places: # Add new intensity edge
                plname = shdata[0][key][0]
                self.addsedge((plname,shname))
                self.shandlers[shname].conp.append(plname)
                self.shandlers[shname].edges.append(key)                
                self.places[plname].consh.append(shname)
                if plname in self.Ym:
                    self.Ym[plname].append((plname,shname))
                else:
                    self.Ym[plname] = [(plname,shname)]
            elif shdata[0][key][0] in self.trans: # Add new intensity arc from transition
                trname = shdata[0][key][0]
                self.addsarc((trname,shname)) 
                self.shandlers[shname].int.append(trname)
                self.shandlers[shname].arcs.append(key)                                    
                self.trans[trname].outsh.append(shname)
                if trname in self.Zl:
                    self.Zl[trname].append(((trname,shname),-1))
                else:
                    self.Zl[trname] = [((trname,shname),-1)]
            elif shdata[0][key][1] in self.trans: # Add new intensity arc to transition                        
                trname = shdata[0][key][1]
                self.addsarc((shname,trname)) 
                self.shandlers[shname].outt.append(trname)
                self.shandlers[shname].arcs.append(key)                
                self.trans[trname].insh.append(shname)
                if trname in self.Zl:
                    self.Zl[trname].append(((shname,trname),1))
                else:
                    self.Zl[trname] = [((shname,trname),1)]
            else:
                raise ValueError('Place or transition not found')
        """Update CD and CDg"""
        # Each component in shdata[1:] can be either a string, i.e., unguarded constraint, or a dictionary, i.e., guarded constraint            
        for idx,comp in enumerate(shdata[1:]):
            if isinstance(comp, str): # Constraint of unguarded arcs
                self.CD[shname+'_'+str(idx)] = {'expr':  comp, 
                                                'nickae':self.shandlers[shname].nickae,
                                                'arcs':  self.shandlers[shname].arcs,
                                                'edges': self.shandlers[shname].edges}
            else:
                for reg in comp:  # Iterate over regions
                    for conidx,cons in enumerate(comp[reg]): # Iterate over constraints of region reg
                        areds = re.findall("(?<![0-9])[_A-Za-z][_a-zA-Z0-9]*",cons) # nicknames of arcs and edges in the constraint. (?<![0-9]) is used to avoid identifiers that are preceded by a digit, i.e., identifier e in 1.023e-14
                        nickarcs = list(set(areds) & set(self.shandlers[shname].arcs)) # nicknames of arcs in the constraint
                        nickedges = list(set(areds) & set(self.shandlers[shname].edges)) # nicknames of edges in the constraint
                        for nickarc in nickarcs:
                            arc = self.shandlers[shname].nickae[nickarc]
                            if reg not in self.sarcs[arc].phi:
                                self.sarcs[arc].phi.append(reg) # Update guards of arc 
                                self.addsarcxguard(arc+(reg,))  # Update sarcxguards
                        self.CDg[shname+'_'+str(idx)+'_'+reg+'_'+str(conidx)] = {
                                                                 'expr':  cons, 
                                                                 'nickae':{ae:self.shandlers[shname].nickae[ae] for ae in areds},
                                                                 'arcs':  deepcopy(nickarcs),
                                                                 'edges': deepcopy(nickedges),
                                                                 'reg':   reg
                                                                 }


    def addsarc(self, saname, **kwargs): 
        """Create an intensity arc with name saname and optional attributes"""
        self.sarcs[saname] = netel.Sarc(saname)
        for key in kwargs:
            setattr(self.sarcs[saname], key, kwargs[key])

    def addsedge(self, sename, **kwargs): 
        """Create an intensity edge with name sename and optional attributes"""
        self.sedges[sename] = netel.Sedge(sename)
        for key in kwargs:
            setattr(self.sedges[sename], key, kwargs[key])


    def computetdepF(self):
        """Compute time dependent F
        Compute components of F that are initialized to -inf.
        Assumptions:
         - The corresponding components of E have one and only one nonnull 
             component
         - The guards of each nonnull components form a partition
         """
        ####
        def compdif(f,fp):
            """Compute differences taking into account -inf"""
            if f == float('-inf') and fp == float('-inf'):
                return 0
            elif fp == float('-inf'):
                return float('inf')
            else:
                return abs(f-fp)
        ####
        if self.E:
            self.rowsu = [index for index, value in enumerate(self.F) 
                                if value > float('-inf')] # rows of matrix E^u
            self.rowsa = list(set(range(len(self.F))) - set(self.rowsu)) 
                # rows of matrix E^a
            listcsg = [ # Constraints for guarded intensity arcs
                'meqmupYmmue', 'CdluleqDmue', 'leql0Zldl', 'mbounds',
                'dleeqdluer', 
                'sigmaa0eqatYsae', 'AdmleqBae', 
                'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                'EcdsigmaeqthetaFc',
                'EudsigmaleqthetaFu',                      
                'EladsigmaleqthetaFla',
                'Emadsigmaeq0', 
                'sigmaeql0thetaZldsigma', 'Jll0leqKl',
                'SrxleqQr',
                'forceactf'
                ]
            listcs = [ # Constraints for unguarded intensity arcs
                'meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'mbounds',
                'sigmaa0eqatYsae', 'AdmleqBae', 
                'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                'EcdsigmaeqthetaFc',
                'EudsigmaleqthetaFu',                      
                'EladsigmaleqthetaFla',
                'Emadsigmaeq0', 
                'sigmaeql0thetaZldsigma', 'Jll0leqKl',
                'forceactf'
                ]
            Ha = deepcopy(self.F)
            it = 0
            dif = self.options['epsiloncompF']+1
            while (    it  < self.options['maxitcompF'] 
                   and dif > self.options['epsiloncompF']):
                it = it + 1
                Fpri = deepcopy(self.F)
                for k in self.rowsa:
                    guards = self.sarcs[list(self.E[k].keys())[0]].phi
                    if guards: # intensity arcs of row k are guarded
                        currentmax = self.F[k]
                        for reg in guards:
                            self.curreg = reg
                            Fmodel = self.buildmodel(listcs=listcsg, 
                                                     vdimdom=self.vdimdomtr)
                            Fmodel.name = 'Fmodel_Timed'
                            opt = SolverFactory(self.solver)
                            Fmodel.obj = pyomo.Objective(
                                expr=sum(self.E[k][sa]*Fmodel.dl[sa]
                                                        for sa in self.E[k]),
                                sense=pyomo.maximize)
                            results = opt.solve(Fmodel)
                            #http://www.pyomo.org/blog/2015/1/8/\
                            #accessing-solver
                            if (results.solver.status == SolverStatus.ok
                                    and results.solver.termination_condition ==
                                        TerminationCondition.optimal):
                                currentmax =max([currentmax,Fmodel.obj.expr()])
                            else:
                                pass # The problem will be infeasible for 
                                     # unreachable regions,so, no warning here
                                     # and the pyomo warning can be ignored.
                                     # Remark: termination_conditions of gurobi
                                     # and cplex can be inconsistent (for the
                                     # same problem one can be unbounded and
                                     # the other infeasible).
                        Ha[k] = currentmax
                        del self.curreg
                    else:
                        Fmodel = self.buildmodel(listcs=listcs, 
                                                 vdimdom=self.vdimdomtr)
                        opt = SolverFactory(self.solver)
                        Fmodel.obj = pyomo.Objective(
                            expr=sum(self.E[k][sa]*Fmodel.dl[sa]
                                                    for sa in self.E[k]), 
                            sense=pyomo.maximize)
                        results = opt.solve(Fmodel)
                        if (results.solver.status == SolverStatus.ok 
                            and results.solver.termination_condition == 
                                TerminationCondition.optimal):
                            Ha[k] = max([self.F[k], Fmodel.obj.expr()])
                        else:
                            print('Solver status:', results.solver.status, 
                            '. Termination condition:', 
                            results.solver.termination_condition)###
                            warnings.warn("Infeasible or unbounded problem "
                                "while computing F["+str(self.E[k])+"]")
                self.F = Ha
                dif = max([compdif(f,fp) for f,fp in zip(self.F, Fpri)])
            if it >= self.options['maxitcompF']:
                warnings.warn("Maximum number of iterations reached while "
                    "computing F (F might not be upperbound for E)")


    def computeLU(self):
        """Compute matrices L and U from E and F"""
        auxE = deepcopy(self.E)
        LUmodel = self.buildmodel(listcs=['EdlleqF'], vdimdom=self.vdimdomun)
        opt = SolverFactory(self.solver)    
        self.L, self.U  = [], []
        for comp in auxE:
            """Compute L"""
            LUmodel.obj = pyomo.Objective(expr=sum(comp[sa]*LUmodel.dl[sa] for sa in comp), 
                                          sense=pyomo.minimize)
            results = opt.solve(LUmodel)
            # http://www.pyomo.org/blog/2015/1/8/accessing-solver
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                self.L.append(LUmodel.obj.expr())
            else:
                warnings.warn("Warning: L["+str(comp)+"] set to -inf")
                self.L.append(-float('inf'))
            LUmodel.del_component('obj')
            """Compute U"""
            LUmodel.obj = pyomo.Objective(expr=sum(comp[sa]*LUmodel.dl[sa] for sa in comp), 
                                          sense=pyomo.maximize)
            results = opt.solve(LUmodel)
            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):            
                self.U.append(LUmodel.obj.expr())
                if self.U[-1] <= self.L[-1]+self.options['epsilonLU']:
                    # Moving to Ec
                    # print("Warning: U["+str(comp)+"]<=L["+str(comp)+"]+epsilonLU. Moving "+str(comp)+" to Ec")
                    self.Ec.append(comp)
                    self.Fc.append(self.U[-1])
                    self.L.pop(-1)
                    self.U.pop(-1)
                    self.F.pop(self.E.index(comp))
                    self.E.remove(comp)
            else:
                warnings.warn("Warning: U["+str(comp)+"] set to inf")
                self.U.append(float('inf'))
            LUmodel.del_component('obj')


    def optimun(self):
        """Optimize objective function objf for untimed constraints USEN"""
        tic = time.clock()
        listcs = ['forceactf', 'forceexef', 'JpmmleqKpm', 'mbounds',
                  'meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa']
        USENmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomun, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(USENmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(USENmodel, self.vdimdomun)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return USENmodel
        else:
            raise ValueError('USENmodel unbounded or infeasible')

    def optimtr(self):
        """Optimize objective function objf for transient constraints TCN"""
        ttic, tic = time.time(), time.clock()
        self.computetdepF()
        self.computeLU()
        self.info['perf']['Python processor time[L,U]'], self.info['perf']['Wall time[L,U]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        listcs = ['forceactf', 'forceactav', 'forceexef', 'forceexeav', 'JpmmleqKpm', 'mbounds', 'avmbounds', 
                  'meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                  'avmeqavmupYmavmue', 'CavdlleqDavmue', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma']
        TCNmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomtr, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(TCNmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(TCNmodel, self.vdimdomtr)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return TCNmodel
        else:
            raise ValueError('TCNmodel unbounded or infeasible')
    
    def optimst(self):
        """Optimize objective function objf for steady state constraints SCN"""
        # F is not computed for steady state. It is only considered if given by the user        
        tic = time.clock()
        listcs = ['forceactav', 'forceexeav', 'JpmavmleqKpm', 'avmbounds',
                  'avmeqavmupYmavmue', 'CavdlleqDavmue', 'avleql0Zlavdl', 'Jll0leqKl',
                  'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau', 'Jmm0leqKm', 'Jaa0leqKa', 
                  'Zmavdmtaueq0',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'avmeqm0Zmdm',
                  'EcavdleqFc', 'EavdlleqF']
        SCNmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomst, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        tic = time.clock()
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(SCNmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(SCNmodel, self.vdimdomst)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return SCNmodel
        else:
            raise ValueError('SCNmodel unbounded or infeasible')

    def optimcst(self):
        """cst and st are equivalent in unguarded nets. 
           Update antype for future checks and call optimst"""
        self.options['antype'] = 'st'
        return self.optimst()

    def optimize(self):
        """Optimize"""
        ttic = time.time()
        if self.options['antype'] == 'tr':
            model = self.optimtr()
        elif self.options['antype'] == 'st':
            model = self.optimst()
        elif self.options['antype'] == 'cst':
            model = self.optimcst()
        elif self.options['antype'] == 'un':
            model = self.optimun()
        else:
            print('No valid analysis type specified for this net')
        self.info['perf']['Wall time[total]'] = time.time()-ttic
        """Process options"""    
        """Print model"""
        if 'printmodel' in self.options and self.options['printmodel']:
            model.pprint()
        """Print variables, i.e., result"""
        if 'printres' in self.options and self.options['printres']:
            self.printres()
        """Write spreadsheet"""
        if 'writexls' in self.options and self.options['writexls']:
            self.writexls(self.options['xlsfile'])
        """Save net object to file"""
        if 'savenet' in self.options and self.options['savenet']:
            output = open(self.options['netfile'], 'wb')
            pickle.dump(self, output)
            output.close()
        """Return model"""
        return model


    def buildmodel(self, listcs, vdimdom, obj={}, extracons=[]):
        """Build mathematical model from a list of constraints listcs, 
           a list of extra constraints extracons and a dictionary with an 
           objective function obj on variables defined in vdimdom"""
        model = pyomo.ConcreteModel()
        """Create variables"""
        class Cqv: # Class with attributes linked to variables
            pass
        qv = Cqv()
        for var in vdimdom:
            auxdict = getattr(self, vdimdom[var]['dim'])
            setattr(model, var, pyomo.Var(auxdict.keys(), within=vdimdom[var]['dom']))
            setattr(qv, var, getattr(model, var))# Create object qv linking attributes to variables of current period
        """Create constraints"""
        qc = self.createcons(qv=qv, listcs=listcs) # qc: Class with attributes linked to constraints
        """Add constraints to the model"""
        for con in vars(qc).keys():
            setattr(model, con, getattr(qc, con))
        """Create extra constraints"""    
        if extracons:
            model.ConExtra = self.createextrac(model, extracons) # Extra constraints
        """Create objective function"""    
        if obj:
            model.obj = self.createobj(model, obj)
        return model


    def createextrac(self, model, extracons):
        """Create extra constraints from dictionaries"""
        def ConExtra(model, r):
            # Any type of extra constraint
            return eval(extracons[r], {var.name:getattr(model,var.name) for var in model.component_objects(pyomo.Var)})
        return pyomo.Constraint(range(len(extracons)), rule=ConExtra)

        
    def createobj(self, model, obj):
        """Create objective function from string or dictionary"""
        def ObjRule(model):
            return eval(obj['f'], {var.name:getattr(model,var.name) for var in model.component_objects(pyomo.Var)})
        if  obj['sense']=='min':
            return pyomo.Objective(rule=ObjRule, sense=pyomo.minimize)
        elif obj['sense']=='max':
            return pyomo.Objective(rule=ObjRule, sense=pyomo.maximize)
        else:
            raise ValueError('Only max and min are allowed for the objective function')


    def createcons(self, qv, listcs):
        """Create constraints on variables qv from list of constraints listcs
           Tokens in self.actfplaces are forced to be active at the final state if forceactf is in listcs
           Tokens in self.actavplaces are forced to be active during the interal if forceactav is in listcs
           Actions in self.exftrans are forced to be executed at the final state if forceexef is in listcs
           Actions in self.exavtrans are forced to be executed instantaneously if forceexeav is in listcs"""
        class Cqc: # Class with attributes linked to constraints
            pass
        qc = Cqc()
        """Initial marking constraints. Jm m0 <= Km"""
        if 'Jmm0leqKm' in listcs:
            def eqm0(dummy, pl): # Initial marking constraints specified as equality when creating places
                return qv.m0[pl] == self.places[pl].m0
            qc.eqm0 = Constraint([pl for pl in self.places if hasattr(self.places[pl], 'm0')], rule=eqm0)
            if self.m0cons:
                def Jmm0leqKm(dummy, r):
                    return eval(self.m0cons[r], {'m0':getattr(qv,'m0')})
                qc.Jmm0leqKm = Constraint(range(len(self.m0cons)), rule=Jmm0leqKm)
        """Final marking constraints. J'm m <= K'm"""
        if 'JpmmleqKpm' in listcs:
            if self.mcons:
                def JpmmleqKpm(dummy, r):
                    return eval(self.mcons[r], {'m':getattr(qv,'m')})
                qc.JpmmleqKpm = Constraint(range(len(self.mcons)), rule=JpmmleqKpm)
        """Average marking (at steady state) constraints. J'm avm <= K'm. This used for steady state analysis only. 
           To constraint average marking in any state analysis use avmbounds"""
        if 'JpmavmleqKpm' in listcs:
            if self.mcons:
                def JpmavmleqKpm(dummy, r):
                    return eval(self.mcons[r], {'m':getattr(qv,'avm')})
                qc.JpmavmleqKpm = Constraint(range(len(self.mcons)), rule=JpmavmleqKpm)
        """Marking bounds (these same bounds are applied to avm if avmbounds is in listcs)"""
        if 'mbounds' in listcs:
            if self.mbounds:
                def funmbounds(dummy, r):
                    return eval(self.mbounds[r], {'m':getattr(qv,'m')})
                qc.mbounds = Constraint(range(len(self.mbounds)), rule=funmbounds)
        """Average marking bounds"""
        if 'avmbounds' in listcs:
            if self.mbounds:
                # Bound avm according to mbounds
                def funavmbounds(dummy, r):
                    return eval(self.mbounds[r], {'m':getattr(qv,'avm')})
                qc.avmbounds = Constraint(range(len(self.mbounds)), rule=funavmbounds)
                # Bound avmr according to mbounds
                if hasattr(self, 'regs'):
                    def regmbrs_init(dummy):
                        return ((reg,r) for reg in self.regs for r in range(len(self.mbounds)))              
                    regmbrs = Set(dimen=2, initialize=regmbrs_init)
                    def funavmboundsr(dummy, reg, r):
                        avmrstr = self.mbounds[r].replace("]", ",reg]")
                        dicvars = {'m':getattr(qv,'avmr')}
                        dicvars['reg'] = reg
                        return eval(avmrstr, dicvars)
                    qc.avmboundsr = Constraint(regmbrs, rule=funavmboundsr)
        """Default lambda constraints. Jl l0 <= Kl"""
        if 'Jll0leqKl' in listcs:
            def eql0(dummy, tr): # Default lambda constraints specified as equality when creating transitions
                return qv.l0[tr] == self.trans[tr].l0
            qc.eql0 = Constraint([tr for tr in self.trans if hasattr(self.trans[tr], 'l0')], rule=eql0)
            if self.l0cons:
                def Jll0leqKl(dummy, r):
                    return eval(self.l0cons[r], {'l0':getattr(qv,'l0')})
                qc.Jll0leqKl = Constraint(range(len(self.l0cons)), rule=Jll0leqKl)
        """Initial actions constraints. Ja a0 <= Ka"""
        if 'Jaa0leqKa' in listcs:
            def eqa0(dummy, tr): # Initial action specified as equality when creating transitions
                return qv.a0[tr] == self.trans[tr].a0
            qc.eqa0 = Constraint([tr for tr in self.trans if hasattr(self.trans[tr], 'a0')], rule=eqa0)
            if self.a0cons:
                def Jaa0leqKa(dummy, r):
                    return eval(self.a0cons[r], {'a0':getattr(qv,'a0')})
                qc.Jaa0leqKa = Constraint(range(len(self.a0cons)), rule=Jaa0leqKa)
        """Force active tokens"""
        if 'forceactf' in listcs:
            if self.actfplaces:
                def ForFAct(dummy, pl):
                    return qv.mup[pl] == 0
                qc.ForFAct = Constraint(self.actfplaces, rule=ForFAct)
        if 'forceactav' in listcs:
            if self.actavplaces:
                def ForAvAct(dummy, pl):
                    return qv.avmup[pl] == 0
                qc.ForAvAct = Constraint(self.actavplaces, rule=ForAvAct)
                if hasattr(self, 'regs'): # Force at regions to improve results
                    def actpreg_init(dummy):
                        return ((pl,reg) for pl in self.actavplaces for reg in self.regs)              
                    actpreg = Set(dimen=2, initialize=actpreg_init)
                    def ForAvActr(dummy, pl, re):
                        return qv.avmupr[(pl,re)] == 0
                    qc.ForAvActr = Constraint(actpreg, rule=ForAvActr)
        """Force executions"""
        if 'forceexef' in listcs:
            if self.exftrans:
                def ForFEx(dummy, tr):
                    return qv.at[tr] == 0
                qc.ForFEx = Constraint(self.exftrans, rule=ForFEx)
        if 'forceexeav' in listcs:
            if self.exavtrans:
                if hasattr(qv, 'avat'): # Transient state
                    def ForAvEx(dummy, tr):
                        return qv.avat[tr] == 0
                    qc.ForAvEx = Constraint(self.exavtrans, rule=ForAvEx)
                    if hasattr(self, 'regs'): # Force at regions to improve results
                        def extreg_init(dummy):
                            return ((tr,reg) for tr in self.exavtrans for reg in self.regs)              
                        extreg = Set(dimen=2, initialize=extreg_init)
                        def ForAvExr(dummy, tr, re):
                            return qv.avatr[(tr,re)] == 0
                        qc.ForAvExr = Constraint(extreg, rule=ForAvExr)
                else: # Steady state
                    def ForAvEx(dummy, tr):
                        return qv.avattau[tr] == 0
                    qc.ForAvEx = Constraint(self.exavtrans, rule=ForAvEx)
                    if hasattr(self, 'regs'): # Force at regions to improve results
                        def extreg_init(dummy):
                            return ((tr,reg) for tr in self.exavtrans for reg in self.regs)              
                        extreg = Set(dimen=2, initialize=extreg_init)
                        def ForAvExr(dummy, tr, re):
                            return qv.avattaur[(tr,re)] == 0
                        qc.ForAvExr = Constraint(extreg, rule=ForAvExr)
        """E dl <= F"""
        if 'EdlleqF' in listcs:
            def EdlleqF(dummy, r):
                return sum(self.E[r][sa]*qv.dl[sa] for sa in self.E[r]) <= self.F[r]
            qc.EdlleqF = Constraint(range(len(self.E)), rule=EdlleqF)
        """m = mup + Ym mue"""
        if 'meqmupYmmue' in listcs:
            def meqmupYmmue(dummy, p):
                if p in self.Ym:
                    return qv.m[p] == qv.mup[p] + sum(qv.mue[edge] for edge in self.Ym[p])
                else: # Place not connected to shandler
                    return qv.m[p] == qv.mup[p]
            qc.meqmupYmmue = Constraint(self.places.keys(), rule=meqmupYmmue)
        """Cdl <= D mue"""
        if 'CdlleqDmue' in listcs or 'CdluleqDmue' in listcs:
            def CdlleqDmue(dummy, r):
                dicvars = {}
                for arc in self.CD[r]['arcs']:
                    dicvars[arc] = qv.dl[self.CD[r]['nickae'][arc]]
                for edge in self.CD[r]['edges']:
                    dicvars[edge] = qv.mue[self.CD[r]['nickae'][edge]]
                return eval(self.CD[r]['expr'], dicvars)
            qc.CdlleqDmue = Constraint(self.CD.keys(), rule=CdlleqDmue)
        """Cdlu <= D mue"""
        if 'CdluleqDmue' in listcs:
            def CdluleqDmue(dummy, r):
                dicvars = {}
                for arc in self.CDg[r]['arcs']:
                    dicvars[arc] = qv.dlu[self.CDg[r]['nickae'][arc],self.CDg[r]['reg']]
                for edge in self.CDg[r]['edges']:
                    dicvars[edge] = qv.mue[self.CDg[r]['nickae'][edge]]
                return eval(self.CDg[r]['expr'], dicvars)
            qc.CdluleqDmue = Constraint(self.CDg.keys(), rule=CdluleqDmue)
        """dl = delta dlu (qv.dl[(saf,sat)] == sum qv.deltar[g] * qv.dlu[(saf,sat, g)])"""
        if 'dleqdeltadlu' in listcs:
            # Element-wise multiplication to compute deltadlu     
            # Product linearized with four inequalities     
            def dleqdeltadlu_a(dummy, saf, sat, g):
                return qv.deltadlu[(saf,sat,g)] <= qv.deltar[g] * self.wu
            qc.dleqdeltadlu_a = Constraint(self.sarcxguards.keys(), rule=dleqdeltadlu_a)
            def dleqdeltadlu_b(dummy, saf, sat, g):
                return qv.deltadlu[(saf,sat,g)] >= qv.deltar[g] * self.wl
            qc.dleqdeltadlu_b = Constraint(self.sarcxguards.keys(), rule=dleqdeltadlu_b)
            def dleqdeltadlu_c(dummy, saf, sat, g):
                return qv.deltadlu[(saf,sat,g)] <= qv.dlu[(saf,sat,g)] - self.wl*(1-qv.deltar[g])
            qc.dleqdeltadlu_c = Constraint(self.sarcxguards.keys(), rule=dleqdeltadlu_c)
            def dleqdeltadlu_d(dummy, saf, sat, g):
                return qv.deltadlu[(saf,sat,g)] >= qv.dlu[(saf,sat,g)] - self.wu*(1-qv.deltar[g])
            qc.dleqdeltadlu_d = Constraint(self.sarcxguards.keys(), rule=dleqdeltadlu_d)
            # Sum of elements to compute dl
            def dleqdeltadlu_sum(dummy, saf, sat):
                if self.sarcs[(saf, sat)].phi:
                    return qv.dl[(saf, sat)] == sum(qv.deltadlu[(saf,sat,g)] for g in self.sarcs[(saf, sat)].phi)
                else:
                    return Constraint.Feasible # Ignore constraint, sa is not guarded
            qc.dleqdeltadlu_sum = Constraint(self.sarcs.keys(), rule=dleqdeltadlu_sum)
        """sigma = at + Ys ae"""
        if 'sigmaeqatYsae' in listcs:
            def sigmaeqatYsae(dummy, t):
                if t in self.Ys:
                    return qv.sigma[t] == qv.at[t] + sum(qv.ae[edge] for edge in self.Ys[t])
                else: # Transition not connected to vhandler
                    return qv.sigma[t] == qv.at[t]
            qc.sigmaeqatYsae = Constraint(self.trans.keys(), rule=sigmaeqatYsae)
        """sigma + a0 = at + Ys ae"""
        if 'sigmaa0eqatYsae' in listcs:
            def sigmaa0eqatYsae(dummy, t):
                if t in self.Ys:
                    return qv.sigma[t] + qv.a0[t] == qv.at[t] + sum(qv.ae[edge] for edge in self.Ys[t])
                else: # Transition not connected to vhandler
                    return qv.sigma[t] + qv.a0[t] == qv.at[t]
            qc.sigmaa0eqatYsae = Constraint(self.trans.keys(), rule=sigmaa0eqatYsae)
        """a0 = 0"""
        if 'a0eq0' in listcs:
            def a0eq0(dummy, t):
                return qv.a0[t] == 0
            qc.a0eq0 = Constraint(self.trans.keys(), rule=a0eq0)
        """Adm <= B ae"""
        if 'AdmleqBae' in listcs:
            def AdmleqBae(dummy, r):
                dicvars = {}
                for arc in self.AB[r]['arcs']:
                    dicvars[arc] = qv.dm[self.AB[r]['nickae'][arc]]
                for edge in self.AB[r]['edges']:
                    dicvars[edge] = qv.ae[self.AB[r]['nickae'][edge]]
                return eval(self.AB[r]['expr'], dicvars)
            qc.AdmleqBae = Constraint(self.AB.keys(), rule=AdmleqBae)
        """m = m0 + Zm dm"""
        if 'meqm0Zmdm' in listcs:
            def meqm0Zmdm(dummy, p):
                if p in self.Zm:
                    return qv.m[p] == qv.m0[p] + sum(arc[1]*qv.dm[arc[0]] for arc in self.Zm[p])
                else: # Place not connected to vhandler
                    return qv.m[p] == qv.m0[p]
            qc.meqm0Zmdm = Constraint(self.places.keys(), rule=meqm0Zmdm)
        """Ec dsigma = theta Fc"""
        if 'EcdsigmaeqthetaFc' in listcs:
            if self.Ec:
                def EcdsigmaeqthetaFc(dummy, r):
                    return sum(self.Ec[r][sa]*qv.dsigma[sa] for sa in self.Ec[r]) == self.theta*self.Fc[r]
                qc.EcdsigmaeqthetaFc = Constraint(range(len(self.Ec)), rule=EcdsigmaeqthetaFc)
        """E dsigma <= theta F"""
        if 'EdsigmaleqthetaF' in listcs:
            if self.E:
                def EdsigmaleqthetaF(dummy, r):
                    if self.F[r] < float('inf'):
                        return sum(self.E[r][sa]*qv.dsigma[sa] for sa in self.E[r]) <= self.theta*self.F[r]
                    else:
                        return Constraint.Feasible # Ignore constraint as it is trivially satified
                qc.EdsigmaleqthetaF = Constraint(range(len(self.E)), rule=EdsigmaleqthetaF)
        """Eu dsigma <= theta Fu"""
        if 'EudsigmaleqthetaFu' in listcs:
            if self.E:
                def EudsigmaleqthetaFu(dummy, r):
                    if self.F[r] < float('inf'):
                        return sum(self.E[r][sa]*qv.dsigma[sa] for sa in self.E[r]) <= self.theta*self.F[r]
                    else:
                        return Constraint.Feasible # Ignore constraint as it is trivially satified
                qc.EudsigmaleqthetaFu = Constraint(self.rowsu, rule=EudsigmaleqthetaFu)
        """Ela dsigma <= theta Fla"""
        if 'EladsigmaleqthetaFla' in listcs:
            if self.E:
                def EladsigmaleqthetaFla(dummy, r):
                    if self.F[r] > float('-inf'):
                        return sum(self.E[r][sa]*qv.dsigma[sa] for sa in self.E[r]) <= self.theta*self.F[r]
                    else:
                        return Constraint.Feasible # Ignore constraint
                qc.EladsigmaleqthetaFla = Constraint(self.rowsa, rule=EladsigmaleqthetaFla)
        """Ela dsigma = 0"""
        if 'Emadsigmaeq0' in listcs:
            if self.E:
                def Emadsigmaeq0(dummy, r):
                    if self.F[r] == float('-inf'): # and all(val >= 0 for key, val in self.E[r].items()):
                        return sum(self.E[r][sa]*qv.dsigma[sa] for sa in self.E[r]) == 0
                    else:
                        return Constraint.Feasible # Ignore constraint
                qc.Emadsigmaeq0 = Constraint(self.rowsa, rule=Emadsigmaeq0)
        """sigma = l0 theta + Zl dsigma"""
        if 'sigmaeql0thetaZldsigma' in listcs:
            def sigmaeql0thetaZldsigma(dummy, t):
                if t in self.Zl:
                    return qv.sigma[t] == qv.l0[t]*self.theta + sum(arc[1]*qv.dsigma[arc[0]] for arc in self.Zl[t])
                else: # Transition not connected to shandler
                    return qv.sigma[t] == qv.l0[t]*self.theta
            qc.sigmaeql0thetaZldsigma = Constraint(self.trans.keys(), rule=sigmaeql0thetaZldsigma)
        """l = l0 + Zl dl"""
        if 'leql0Zldl' in listcs:
            def leql0Zldl(dummy, t):
                if t in self.Zl:
                    return qv.l[t] == qv.l0[t] + sum(arc[1]*qv.dl[arc[0]] for arc in self.Zl[t])
                else: # Transition not connected to shandler
                    return qv.l[t] == qv.l0[t]
            qc.leql0Zldl = Constraint(self.trans.keys(), rule=leql0Zldl)
        """avm = avmup + Ym avmue"""
        if 'avmeqavmupYmavmue' in listcs:
            def avmeqavmupYmavmue(dummy, p):
                if p in self.Ym:
                    return qv.avm[p] == qv.avmup[p] + sum(qv.avmue[edge] for edge in self.Ym[p])
                else: # Place not connected to shandler
                    return qv.avm[p] == qv.avmup[p]
            qc.avmeqavmupYmavmue = Constraint(self.places.keys(), rule=avmeqavmupYmavmue)
        """C avdl <= D avmue"""
        if 'CavdlleqDavmue' in listcs or 'CavdluleqDavmue' in listcs:
            def CavdlleqDavmue(dummy, r):
                dicvars = {}
                for arc in self.CD[r]['arcs']:
                    dicvars[arc] = qv.avdl[self.CD[r]['nickae'][arc]]
                for edge in self.CD[r]['edges']:
                    dicvars[edge] = qv.avmue[self.CD[r]['nickae'][edge]]
                return eval(self.CD[r]['expr'], dicvars)
            qc.CavdlleqDavmue = Constraint(self.CD.keys(), rule=CavdlleqDavmue)
        """C avdlu <= D avmue"""
        if 'CavdluleqDavmue' in listcs:
            def CavdluleqDavmue(dummy, r):
                dicvars = {}
                for arc in self.CDg[r]['arcs']:
                    dicvars[arc] = qv.avdlu[self.CDg[r]['nickae'][arc],self.CDg[r]['reg']]
                for edge in self.CDg[r]['edges']:
                    dicvars[edge] = qv.avmue[self.CDg[r]['nickae'][edge]]
                return eval(self.CDg[r]['expr'], dicvars)
            qc.CavdluleqDavmue = Constraint(self.CDg.keys(), rule=CavdluleqDavmue)
        """avl = l0 + Zl avdl"""    
        if 'avleql0Zlavdl' in listcs:
            def avleql0Zlavdl(dummy, t):
                if t in self.Zl:
                    return qv.avl[t] == qv.l0[t] + sum(arc[1]*qv.avdl[arc[0]] for arc in self.Zl[t])
                else: # Transition not connected to shandler
                    return qv.avl[t] == qv.l0[t]
            qc.avleql0Zlavdl = Constraint(self.trans.keys(), rule=avleql0Zlavdl)
        """dsigma = avdl theta"""    
        if 'dsigmaeqavdltheta' in listcs:
            def dsigmaeqavdltheta(dummy, sa):
                return qv.dsigma[eval(sa)] == qv.avdl[eval(sa)] * self.theta
            qc.dsigmaeqavdltheta = Constraint([repr(sa) for sa in self.sarcs.keys()], rule=dsigmaeqavdltheta)
        """avsigma = 0.5 l0 theta + Zl avdsigma"""    
        if 'avsigmaeq05l0thetaZlavdsigma' in listcs:
            def avsigmaeq05l0thetaZlavdsigma(dummy, t):
                if t in self.Zl:
                    return qv.avsigma[t] == 0.5 * qv.l0[t] * self.theta + sum(arc[1]*qv.avdsigma[arc[0]] for arc in self.Zl[t])
                else: # Transition not connected to shandler
                    return qv.avsigma[t] == 0.5 * qv.l0[t] * self.theta
            qc.avsigmaeq05l0thetaZlavdsigma = Constraint(self.trans.keys(), rule=avsigmaeq05l0thetaZlavdsigma)
        """avsigma = avat + Ys avae"""
        if 'avsigmaeqavatYsavae' in listcs:
            def avsigmaeqavatYsavae(dummy, t):
                if t in self.Ys:
                    return qv.avsigma[t] == qv.avat[t] + sum(qv.avae[edge] for edge in self.Ys[t])
                else: # Transition not connected to vhandler
                    return qv.avsigma[t] == qv.avat[t]
            qc.avsigmaeqavatYsavae = Constraint(self.trans.keys(), rule=avsigmaeqavatYsavae)
        """avsigma + a0 = avat + Ys avae"""
        if 'avsigmaa0eqavatYsavae' in listcs:
            def avsigmaa0eqavatYsavae(dummy, t):
                if t in self.Ys:
                    return qv.avsigma[t] + qv.a0[t] == qv.avat[t] + sum(qv.avae[edge] for edge in self.Ys[t])
                else: # Transition not connected to vhandler
                    return qv.avsigma[t] + qv.a0[t] == qv.avat[t]
            qc.avsigmaa0eqavatYsavae = Constraint(self.trans.keys(), rule=avsigmaa0eqavatYsavae)
        """A avdm <= B avae"""    
        if 'AavdmleqBavae' in listcs:
            def AavdmleqBavae(dummy, r):
                dicvars = {}
                for arc in self.AB[r]['arcs']:
                    dicvars[arc] = qv.avdm[self.AB[r]['nickae'][arc]]
                for edge in self.AB[r]['edges']:
                    dicvars[edge] = qv.avae[self.AB[r]['nickae'][edge]]
                return eval(self.AB[r]['expr'], dicvars)
            qc.AavdmleqBavae = Constraint(self.AB.keys(), rule=AavdmleqBavae)
        """avm = m0 + Zm avdm"""
        if 'avmeqm0Zmavdm' in listcs:
            def avmeqm0Zmavdm(dummy, p):
                if p in self.Zm:
                    return qv.avm[p] == qv.m0[p] + sum(arc[1]*qv.avdm[arc[0]] for arc in self.Zm[p])
                else: # Place not connected to vhandler
                    return qv.avm[p] == qv.m0[p]
            qc.avmeqm0Zmavdm = Constraint(self.places.keys(), rule=avmeqm0Zmavdm)
        """avae <= ae"""
        if 'avaeleqae' in listcs:
            def avaeleqae(dummy, ve):
                return qv.avae[eval(ve)] <= qv.ae[eval(ve)]
            qc.avaeleqae = Constraint([repr(ve) for ve in self.vedges.keys()], rule=avaeleqae)
        """avdm <= dm"""
        if 'avdmleqdm' in listcs:
            def avdmleqdm(dummy, va):
                return qv.avdm[eval(va)] <= qv.dm[eval(va)]
            qc.avdmleqdm = Constraint([repr(va) for va in self.varcs.keys()], rule=avdmleqdm)
        """avdsigma <= dsigma"""
        if 'avdsigmaleqdsigma' in listcs:
            def avdsigmaleqdsigma(dummy, sa):
                return qv.avdsigma[eval(sa)] <= qv.dsigma[eval(sa)]
            qc.avdsigmaleqdsigma = Constraint([repr(sa) for sa in self.sarcs.keys()], rule=avdsigmaleqdsigma)
        """avsgima <= sigma"""
        if 'avsigmaleqsigma' in listcs:
            def avsigmaleqsigma(dummy, t):
                return qv.avsigma[t] <= qv.sigma[t]
            qc.avsigmaleqsigma = Constraint(self.trans.keys(), rule=avsigmaleqsigma)
        """Ec avdsigma = 0.5 Ec dsigma"""
        if 'Ecavdsigmaeq05Ecdsigma' in listcs:
            def Ecavdsigmaeq05Ecdsigma(dummy, r):
                return sum(self.Ec[r][sa]*qv.avdsigma[sa] for sa in self.Ec[r]) == 0.5 * sum(self.Ec[r][sa]*qv.dsigma[sa] for sa in self.Ec[r])
            qc.Ecavdsigmaeq05Ecdsigma = Constraint(range(len(self.Ec)), rule=Ecavdsigmaeq05Ecdsigma)
        """theta Ek avdsigma <= Uk theta^2/2 - (Uk theta - Ek dsigma)^2/(2 (Uk-Lk)) if -inf<Lk
           theta Ek avdsigma <= Uk theta^2/2 if -inf=Lk"""
        if 'thetaEavdsigmaleqquad2' in listcs:
            def thetaEavdsigmaleqquad2(dummy, k):
                tEkavds = self.theta * sum(self.E[k][sa]*qv.avdsigma[sa] for sa in self.E[k]) # theta Ek avdsigma
                if -float('inf') < self.L[k]:
                    auxe = (self.U[k]*self.theta - sum(self.E[k][sa]*qv.dsigma[sa] for sa in self.E[k]))
                    return tEkavds <= self.U[k]*self.theta*self.theta/2.0 - (auxe*auxe)/float(2*(self.U[k]-self.L[k]))
                else:
                    return tEkavds <= self.U[k]*self.theta*self.theta/2.0
            qc.thetaEavdsigmaleqquad2 = Constraint(range(len(self.E)), rule=thetaEavdsigmaleqquad2)
        """Lk theta^2/2 + (Ek dsigma-Lk theta)^2/ (2(Uk-Lk)) <= theta Ek avdsigma if -inf<Lk
           theta Ek dsigma - Uk theta^2/2 <= theta Ek avdsigma if -inf=Lk"""
        if 'quad2leqthetaEavdsigma' in listcs:
            def quad2leqthetaEavdsigma(dummy, k):
                tEkavds = self.theta * sum(self.E[k][sa]*qv.avdsigma[sa] for sa in self.E[k]) # theta Ek avdsigma
                if -float('inf') < self.L[k]:
                    auxe = (sum(self.E[k][sa]*qv.dsigma[sa] for sa in self.E[k]) - self.L[k]*self.theta)
                    return self.L[k]*self.theta*self.theta/2.0 + (auxe*auxe)/float(2*(self.U[k]-self.L[k])) <= tEkavds
                else:
                    return self.theta*sum(self.E[k][sa]*qv.dsigma[sa] for sa in self.E[k]) - \
                            self.U[k]*self.theta*self.theta/2.0 <= tEkavds
            qc.quad2leqthetaEavdsigma = Constraint(range(len(self.E)), rule=quad2leqthetaEavdsigma)
        """avsigmatau = avl"""
        if 'avsigmataueqavl' in listcs:
            def avsigmataueqavl(dummy, t):
                return qv.avsigmatau[t] == qv.avl[t]
            qc.avsigmataueqavl = Constraint(self.trans.keys(), rule=avsigmataueqavl)
        """avsigmatau = avattau + Ys avaetau"""    
        if 'avsigmataueqavattauYsigmaavaetau' in listcs:
            def avsigmataueqavattauYsigmaavaetau(dummy, t):
                if t in self.Ys:
                    return qv.avsigmatau[t] == qv.avattau[t] + sum(qv.avaetau[edge] for edge in self.Ys[t])
                else: # Transition not connected to vhandler
                    return qv.avsigmatau[t] == qv.avattau[t]
            qc.avsigmataueqavattauYsigmaavaetau = Constraint(self.trans.keys(), rule=avsigmataueqavattauYsigmaavaetau)
        """A avdmtau <= B avaetau"""    
        if 'AavdmtauleqBavaetau' in listcs:
            def AavdmtauleqBavaetau(dummy, r):
                dicvars = {}
                for arc in self.AB[r]['arcs']:
                    dicvars[arc] = qv.avdmtau[self.AB[r]['nickae'][arc]]
                for edge in self.AB[r]['edges']:
                    dicvars[edge] = qv.avaetau[self.AB[r]['nickae'][edge]]
                return eval(self.AB[r]['expr'], dicvars)
            qc.AavdmtauleqBavaetau = Constraint(self.AB.keys(), rule=AavdmtauleqBavaetau)
        """Zm avdmtau = 0"""
        if 'Zmavdmtaueq0' in listcs:
            def Zmavdmtaueq0(dummy, p):
                if p in self.Zm:
                    return sum(arc[1]*qv.avdmtau[arc[0]] for arc in self.Zm[p]) == 0
                else: # Place not connected to vhandler
                    return Constraint.Feasible
            qc.Zmavdmtaueq0 = Constraint(self.places.keys(), rule=Zmavdmtaueq0)
        """avm = m0 + Zm dm"""
        if 'avmeqm0Zmdm' in listcs:
            def avmeqm0Zmdm(dummy, p):
                if p in self.Zm:
                    return qv.avm[p] == qv.m0[p] + sum(arc[1]*qv.dm[arc[0]] for arc in self.Zm[p])
                else: # Place not connected to vhandler
                    return qv.avm[p] == qv.m0[p]
            qc.avmeqm0Zmdm = Constraint(self.places.keys(), rule=avmeqm0Zmdm)
        """Ec avdl = Fc"""
        if 'EcavdleqFc' in listcs:
            if self.Ec:
                def EcavdleqFc(dummy, r):
                    return sum(self.Ec[r][sa]*qv.avdl[sa] for sa in self.Ec[r]) == self.Fc[r]
                qc.EcavdleqFc = Constraint(range(len(self.Ec)), rule=EcavdleqFc)
        """E avdl <= F"""
        if 'EavdlleqF' in listcs:
            if self.E and self.F: # F is not computed for steady state. It is only considered if given by the user
                def EavdlleqF(dummy, r):
                    if self.F[r] > float('-inf'):
                        return sum(self.E[r][sa]*qv.avdl[sa] for sa in self.E[r]) <= self.F[r]
                    else:
                        return Constraint.Feasible # Ignore constraint as it is trivially satified
                qc.EavdlleqF = Constraint(range(len(self.E)), rule=EavdlleqF)
        """Sr x <= Qr + W(1-deltar)"""
        if 'SrxleqQrW1deltar' in listcs:
            def regrow_init(dummy):
                return ((reg,row) for reg in self.regs for row in range(len(self.regs[reg].SQrows)))              
            regrow = Set(dimen=2, initialize=regrow_init)
            def SrxleqQrW1deltar(dummy, reg, row):
                dicvars = {var:getattr(qv,var) for var in FlexN.vdimdomtr if hasattr(qv,var)} # vdimdomun could be used instead of vdimdomtr but then var dsigma is not available
                dicvars['deltar'] = qv.deltar
                dicvars['W'] = self.W
                dicvars['reg'] = reg
                if self.regs[reg].SQrows[row].find('<=') >= 0:
                    return eval(self.regs[reg].SQrows[row]+"+W*(1-deltar[reg])", dicvars)
                elif self.regs[reg].SQrows[row].find('>=') >= 0:                    
                    return eval(self.regs[reg].SQrows[row]+"-W*(1-deltar[reg])", dicvars)
                else:
                    raise ValueError('Only <= and >= are allowed for SQ matrices')
            qc.SrxleqQrW1deltar = Constraint(regrow, rule=SrxleqQrW1deltar)
#        """delta[e,(e,r)] = deltar. Deprecated, no variable avdelta exists, just avdeltar"""
#        if 'deltaeereqdeltar' in listcs:
#            def deltaeereqdeltar(dummy, arcre):
#                return qv.delta[eval(arcre)] == qv.deltar[eval(arcre)[2]]
#            qc.deltaeereqdeltar = Constraint([repr(arcre) for arcre in self.sarcxguards.keys()], rule=deltaeereqdeltar)
        """sum deltar = 1"""
        if 'sumdeltareq1' in listcs:
            if self.parts:
                def sumdeltareq1(dummy, part):
                    return sum(qv.deltar[reg] for reg in self.parts[part].regs) == 1
                qc.sumdeltareq1 = Constraint(self.parts.keys(), rule=sumdeltareq1)
        """sum alphar = 1"""
        if 'sumalphareq1' in listcs:
            if self.parts:
                def sumalphareq1(dummy, part):
                    return sum(qv.alphar[reg] for reg in self.parts[part].regs) == 1
                qc.sumalphareq1 = Constraint(self.parts.keys(), rule=sumalphareq1)
        """avdl = alpha avdlg (qv.avdl[sa] == sum_{g in sa} qv.alphar[g] * qv.avdlg[sa])"""
        if 'avdleqalphaavdlg' in listcs:
            # Computation of alphaavdlg
            def avdleqalphaavdlg_a(dummy, saf, sat, g):
                return qv.alphaavdlg[(saf,sat,g)] <= qv.alphar[g]*self.wu
            qc.avdleqalphaavdlg_a = Constraint(self.sarcxguards.keys(), rule=avdleqalphaavdlg_a)
            def avdleqalphaavdlg_b(dummy, saf, sat, g):
                return qv.alphaavdlg[(saf,sat,g)] <= qv.avdlg[(saf,sat,g)]
            qc.avdleqalphaavdlg_b = Constraint(self.sarcxguards.keys(), rule=avdleqalphaavdlg_b)
            def avdleqalphaavdlg_c(dummy, saf, sat, g):
                return qv.alphaavdlg[(saf,sat,g)] >= qv.avdlg[(saf,sat,g)] - self.wu*(1-qv.alphar[g])
            qc.avdleqalphaavdlg_c = Constraint(self.sarcxguards.keys(), rule=avdleqalphaavdlg_c)
            # Sum of elements to compute avdl
            def avdleqalphaavdlg_sum(dummy, saf, sat):
                if self.sarcs[(saf,sat)].phi:
                    return qv.avdl[(saf,sat)] == sum(qv.alphaavdlg[(saf, sat, g)] for g in self.sarcs[(saf,sat)].phi)
                else:
                    return Constraint.Feasible # Ignore constraint, sa is not guarded
            qc.avdleqalphaavdlg_sum = Constraint(self.sarcs.keys(), rule=avdleqalphaavdlg_sum)
        """avdl = avdelta avdlg (qv.avdl[(saf,sat)] == sum qv.avdeltar[g] * qv.avdlg[(saf,sat,g)])"""
        if 'avdleqavdeltaavdlg' in listcs:
            # Element-wise multiplication to compute avdeltaavdlg 
            # Computation of beta
            def avdleqavdeltaavdlg_a(dummy, re, q):
                return self.ds[q]-qv.avdeltar[re] <= 2*(1-qv.beta[(re,q)])
            qc.avdleqavdeltaavdlg_a = Constraint(self.regxqs.keys(), rule=avdleqavdeltaavdlg_a)
            def avdleqavdeltaavdlg_b(dummy, re, q):
                return self.ds[q]-qv.avdeltar[re] >= -2*qv.beta[(re,q)]
            qc.avdleqavdeltaavdlg_b = Constraint(self.regxqs.keys(), rule=avdleqavdeltaavdlg_b)
            # Computation of betaavdlg
            def avdleqavdeltaavdlg_c(dummy, saf, sat, g, q):
                return qv.betaavdlg[(saf,sat,g,q)] <= qv.beta[(g,q)]*self.wu
            qc.avdleqavdeltaavdlg_c = Constraint(self.sarcxguardxqs.keys(), rule=avdleqavdeltaavdlg_c)
            def avdleqavdeltaavdlg_d(dummy, saf, sat, g, q):
                return qv.betaavdlg[(saf,sat,g,q)] <= qv.avdlg[(saf,sat,g)]
            qc.avdleqavdeltaavdlg_d = Constraint(self.sarcxguardxqs.keys(), rule=avdleqavdeltaavdlg_d)
            def avdleqavdeltaavdlg_e(dummy, saf, sat, g, q):
                return qv.betaavdlg[(saf,sat,g,q)] >= qv.avdlg[(saf,sat,g)] - self.wu*(1-qv.beta[(g,q)])
            qc.avdleqavdeltaavdlg_e = Constraint(self.sarcxguardxqs.keys(), rule=avdleqavdeltaavdlg_e)
            # Computation of avdeltaavdlg
            def avdleqavdeltaavdlg_f(dummy, saf, sat, g):
                q = len(self.ds)-1
                return sum(qv.betaavdlg[(saf,sat,g,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaavdlg[(saf,sat,g)]
            qc.avdleqavdeltaavdlg_f = Constraint(self.sarcxguards.keys(), rule=avdleqavdeltaavdlg_f)
            def avdleqavdeltaavdlg_g(dummy, saf, sat, g):
                q = len(self.ds)-1
                return qv.avdeltaavdlg[(saf,sat,g)] <= qv.avdlg[(saf,sat,g)]-sum((qv.avdlg[(saf,sat,g)]-qv.betaavdlg[(saf,sat,g,j)])*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdleqavdeltaavdlg_g = Constraint(self.sarcxguards.keys(), rule=avdleqavdeltaavdlg_g)
            # Sum of elements to compute avdl
            def avdleqavdeltaavdlg_h(dummy, saf, sat):
                if self.sarcs[(saf,sat)].phi:
                    return qv.avdl[(saf,sat)] == sum(qv.avdeltaavdlg[(saf,sat,reg)] for reg in self.sarcs[(saf,sat)].phi)
                else:
                    return Constraint.Feasible # Ignore constraint, (saf,sat) is not guarded
            qc.avdleqavdeltaavdlg_h = Constraint(self.sarcs.keys(), rule=avdleqavdeltaavdlg_h)
            # avdl[e] = avdlg[(e,r)] if r is the only region visited of its partition (to improve linearization errors)                
            def avdlleqavdlrwu(dummy, saf, sat, g):
                return qv.avdl[saf,sat] <= qv.avdlg[(saf,sat,g)] + self.wu*(1-qv.gammar[g])
            qc.avdlleqavdlrwu = Constraint(self.sarcxguards.keys(), rule=avdlleqavdlrwu)
            def avdlgeqavdlr2wu(dummy, saf, sat, g):
                return qv.avdl[saf,sat] >= qv.avdlg[(saf,sat,g)] - 2*self.wu*(1-qv.gammar[g])
            qc.avdlgeqavdlr2wu = Constraint(self.sarcxguards.keys(), rule=avdlgeqavdlr2wu)
        """Sr avzr <= Qr + W(1-alphar)"""
        if 'SravzrleqQrW1alphar' in listcs:
            def regrowsq_init(dummy):
                return ((reg,row) for reg in self.regs for row in range(len(self.regs[reg].SQrows)))              
            regrowsq = Set(dimen=2, initialize=regrowsq_init)
            def SravzrleqQrW1alphar(dummy, reg, row):
                dicvars = {var:getattr(qv,'av'+var+'r') for var in FlexN.vdimdomtr if hasattr(qv,'av'+var+'r')}
                dicvars['alphar'] = qv.alphar
                dicvars['W'] = self.W
                dicvars['reg'] = reg
                sqrreg = self.regs[reg].SQrows[row].replace("]", ",reg]")
                if sqrreg.find('<=') >= 0:
                    return eval(sqrreg+"+W*(1-alphar[reg])", dicvars)
                elif sqrreg.find('>=') >= 0:                    
                    return eval(sqrreg+"-W*(1-alphar[reg])", dicvars)
                else:
                    raise ValueError('Only <= and >= are allowed for SQ matrices')
            qc.SravzrleqQrW1alphar = Constraint(regrowsq, rule=SravzrleqQrW1alphar)
        """avmr = avmupr + Ym avmuer"""
        if 'avmreqavmuprYmavmuer' in listcs:
            def avmreqavmuprYmavmuer(dummy, pl, re):
                if pl in self.Ym:
                    return qv.avmr[(pl,re)] == qv.avmupr[(pl,re)] + sum(qv.avmuer[(edge[0],edge[1],re)] for edge in self.Ym[pl])
                else: # Place not connected to shandler
                    return qv.avmr[(pl,re)] == qv.avmupr[(pl,re)]
            qc.avmreqavmuprYmavmuer = Constraint(self.placexregs.keys(), rule=avmreqavmuprYmavmuer)
        """C avdlr <= D avmuer"""
        if 'CavdlrleqDavmuer' in listcs or 'CavdlurleqDavmuer' in listcs:
            def regrowcd_init(dummy):
                return ((reg,row) for reg in self.regs for row in self.CD.keys())              
            regrowcd = Set(dimen=2, initialize=regrowcd_init)
            def CavdlrleqDavmuer(dummy, reg, row):
                dicvars = {}
                for arc in self.CD[row]['arcs']:
                    dicvars[arc] = qv.avdlr[self.CD[row]['nickae'][arc],reg]
                for edge in self.CD[row]['edges']:
                    dicvars[edge] = qv.avmuer[self.CD[row]['nickae'][edge],reg]
                return eval(self.CD[row]['expr'], dicvars)
            qc.CavdlrleqDavmuer = Constraint(regrowcd, rule=CavdlrleqDavmuer)
        """C avdlur <= D avmuer"""
        if 'CavdlurleqDavmuer' in listcs:
            def regrowcdg_init(dummy):
                return ((reg,row) for reg in self.regs for row in self.CDg.keys())              
            regrowcdg = Set(dimen=2, initialize=regrowcdg_init)
            def CavdlurleqDavmuer(dummy, reg, row):
                dicvars = {}
                for arc in self.CDg[row]['arcs']:
                    dicvars[arc] = qv.avdlur[self.CDg[row]['nickae'][arc],self.CDg[row]['reg'],reg]
                for edge in self.CDg[row]['edges']:
                    dicvars[edge] = qv.avmuer[self.CDg[row]['nickae'][edge],reg]
                return eval(self.CDg[row]['expr'], dicvars)
            qc.CavdlurleqDavmuer = Constraint(regrowcdg, rule=CavdlurleqDavmuer)
        """avlr = l0 + Zl avdlr"""    
        if 'avlreql0Zlavdlr' in listcs:
            def avlreql0Zlavdlr(dummy, tr, re):
                if tr in self.Zl:
                    return qv.avlr[(tr,re)] == qv.l0[tr] + sum(arc[1]*qv.avdlr[(arc[0][0],arc[0][1],re)] for arc in self.Zl[tr])
                else: # Transition not connected to shandler
                    return qv.avlr[(tr,re)] == qv.l0[tr]
            qc.avlreql0Zlavdlr = Constraint(self.tranxregs.keys(), rule=avlreql0Zlavdlr)
        """avsigmataur = avattaur + Ys avaetaur"""    
        if 'avsigmataureqavattaurYsigmaavaetaur' in listcs:
            def avsigmataureqavattaurYsigmaavaetaur(dummy, tr, re):
                if tr in self.Ys:
                    return qv.avsigmataur[(tr, re)] == qv.avattaur[(tr, re)] + sum(qv.avaetaur[(edge[0],edge[1],re)] for edge in self.Ys[tr])
                else: # Transition not connected to vhandler
                    return qv.avsigmataur[(tr, re)] == qv.avattaur[(tr, re)]
            qc.avsigmataureqavattaurYsigmaavaetaur = Constraint(self.tranxregs.keys(), rule=avsigmataureqavattaurYsigmaavaetaur)
        """A avdmtaur <= B avaetaur"""    
        if 'AavdmtaurleqBavaetaur' in listcs:
            def regrowabtaur_init(dummy):
                return ((reg,row) for reg in self.regs for row in self.AB.keys())              
            regrowabtaur = Set(dimen=2, initialize=regrowabtaur_init)
            def AavdmtaurleqBavaetaur(dummy, reg, row):
                dicvars = {}
                for arc in self.AB[row]['arcs']:
                    dicvars[arc] = qv.avdmtaur[self.AB[row]['nickae'][arc],reg]
                for edge in self.AB[row]['edges']:
                    dicvars[edge] = qv.avaetaur[self.AB[row]['nickae'][edge],reg]
                return eval(self.AB[row]['expr'], dicvars)
            qc.AavdmtaurleqBavaetaur = Constraint(regrowabtaur, rule=AavdmtaurleqBavaetaur)
        """sigmar = atr + Ys aer"""    
        if 'sigmareqatrYsigmaaer' in listcs:
            def sigmareqatrYsigmaaer(dummy, tr, re):
                if tr in self.Ys:
                    return qv.sigmar[(tr,re)] == qv.atr[(tr,re)] + sum(qv.aer[(edge[0],edge[1],re)] for edge in self.Ys[tr])
                else: # Transition not connected to vhandler
                    return qv.sigmar[(tr,re)] == qv.atr[(tr,re)]
            qc.sigmareqatrYsigmaaer = Constraint(self.tranxregs.keys(), rule=sigmareqatrYsigmaaer)
        """sigmar + a0 = atr + Ys aer"""    
        if 'sigmara0eqatrYsigmaaer' in listcs:
            def sigmara0eqatrYsigmaaer(dummy, tr, re):
                if tr in self.Ys:
                    return qv.sigmar[(tr,re)] + qv.a0[tr] == qv.atr[(tr,re)] + sum(qv.aer[(edge[0],edge[1],re)] for edge in self.Ys[tr])
                else: # Transition not connected to vhandler
                    return qv.sigmar[(tr,re)] + qv.a0[tr] == qv.atr[(tr,re)]
            qc.sigmara0eqatrYsigmaaer = Constraint(self.tranxregs.keys(), rule=sigmara0eqatrYsigmaaer)
        """A dmr <= B aer"""    
        if 'AdmrleqBaer' in listcs:
            def regrowab_init(dummy):
                return ((reg,row) for reg in self.regs for row in self.AB.keys())              
            regrowab = Set(dimen=2, initialize=regrowab_init)
            def AdmrleqBaer(dummy, reg, row):
                dicvars = {}
                for arc in self.AB[row]['arcs']:
                    dicvars[arc] = qv.dmr[self.AB[row]['nickae'][arc],reg]
                for edge in self.AB[row]['edges']:
                    dicvars[edge] = qv.aer[self.AB[row]['nickae'][edge],reg]
                return eval(self.AB[row]['expr'], dicvars)
            qc.AdmrleqBaer = Constraint(regrowab, rule=AdmrleqBaer)
        """avmr = m0 + Zm dmr"""    
        if 'avmreqm0Zmdmr' in listcs:
            def avmreqm0Zmdmr(dummy, pl, re):
                if pl in self.Zm:
                    return qv.avmr[(pl,re)] == qv.m0[pl] + sum(arc[1]*qv.dmr[(arc[0][0],arc[0][1],re)] for arc in self.Zm[pl])
                else: # Transition not connected to shandler
                    return qv.avmr[(pl,re)] == qv.m0[pl]
            qc.avmreqm0Zmdmr = Constraint(self.placexregs.keys(), rule=avmreqm0Zmdmr)
#        """avdelta[e,(e,r)] = avdeltar. Deprecated, no variable avdelta exists, just avdeltar"""
#        if 'avdeltaeereqavdeltar' in listcs:
#            def avdeltaeereqavdeltar(dummy, arcre):
#                return qv.avdelta[eval(arcre)] == qv.avdeltar[eval(arcre)[2]]
#            qc.avdeltaeereqavdeltar = Constraint([repr(arcre) for arcre in self.sarcxguards.keys()], rule=avdeltaeereqavdeltar)
#        """avdlg[(e,r)] = avdlur[(e,r)]. Warning: This constraint should not be used as avdlur can be negative and avdlg is nonnegative"""
#        if 'avdlgereqavdlurer' in listcs:
#            def avdlgereqavdlurer(dummy, saf, sat, gu):
#                return qv.avdlg[(saf,sat,gu)] == qv.avdlur[(saf,sat,gu,gu)]
#            qc.avdlgereqavdlurer = Constraint(self.sarcxguards.keys(), rule=avdlgereqavdlurer)
        """avdlg[(e,r)] = alphar avdlur[(e,r)]"""
        if 'avdlgereqalpharavdlurer' in listcs:
            def avdlgereqalpharavdlurer_a(dummy, saf, sat, gu):
                return qv.avdlg[(saf,sat,gu)] <= qv.alphar[gu]*self.wu
            qc.avdlgereqalpharavdlurer_a = Constraint(self.sarcxguards.keys(), rule=avdlgereqalpharavdlurer_a)
            def avdlgereqalpharavdlurer_b(dummy, saf, sat, gu):
                return qv.avdlg[(saf,sat,gu)] >= qv.alphar[gu]*self.wl
            qc.avdlgereqalpharavdlurer_b = Constraint(self.sarcxguards.keys(), rule=avdlgereqalpharavdlurer_b)
            def avdlgereqalpharavdlurer_c(dummy, saf, sat, gu):
                return qv.avdlg[(saf,sat,gu)] <= qv.avdlur[(saf,sat,gu,gu)] - self.wl*(1-qv.alphar[gu])
            qc.avdlgereqalpharavdlurer_c = Constraint(self.sarcxguards.keys(), rule=avdlgereqalpharavdlurer_c)
            def avdlgereqalpharavdlurer_d(dummy, saf, sat, gu):
                return qv.avdlg[(saf,sat,gu)] >= qv.avdlur[(saf,sat,gu,gu)] - self.wu*(1-qv.alphar[gu])
            qc.avdlgereqalpharavdlurer_d = Constraint(self.sarcxguards.keys(), rule=avdlgereqalpharavdlurer_d)
#        """avdlr[e] = avdlur[(e,r)]. Warning: This constraint should not be used as avdlur can be negative and avdlr is nonnegative"""
#        if 'avdlreeqavdlurer' in listcs:
#            def avdlreeqavdlurer(dummy, saf, sat, gu):
#                return qv.avdlr[(saf,sat,gu)] == qv.avdlur[(saf,sat,gu,gu)]
#            qc.avdlreeqavdlurer = Constraint(self.sarcxguards.keys(), rule=avdlreeqavdlurer)
        """avdlr[e] = alphar avdlur[(e,r)]"""
        if 'avdlreeqalpharavdlurer' in listcs:
            def avdlreeqalpharavdlurer_a(dummy, saf, sat, gu):
                return qv.avdlr[(saf,sat,gu)] <= qv.alphar[gu]*self.wu
            qc.avdlreeqalpharavdlurer_a = Constraint(self.sarcxguards.keys(), rule=avdlreeqalpharavdlurer_a)
            def avdlreeqalpharavdlurer_b(dummy, saf, sat, gu):
                return qv.avdlr[(saf,sat,gu)] >= qv.alphar[gu]*self.wl
            qc.avdlreeqalpharavdlurer_b = Constraint(self.sarcxguards.keys(), rule=avdlreeqalpharavdlurer_b)
            def avdlreeqalpharavdlurer_c(dummy, saf, sat, gu):
                return qv.avdlr[(saf,sat,gu)] <= qv.avdlur[(saf,sat,gu,gu)] - self.wl*(1-qv.alphar[gu])
            qc.avdlreeqalpharavdlurer_c = Constraint(self.sarcxguards.keys(), rule=avdlreeqalpharavdlurer_c)
            def avdlreeqalpharavdlurer_d(dummy, saf, sat, gu):
                return qv.avdlr[(saf,sat,gu)] >= qv.avdlur[(saf,sat,gu,gu)] - self.wu*(1-qv.alphar[gu])
            qc.avdlreeqalpharavdlurer_d = Constraint(self.sarcxguards.keys(), rule=avdlreeqalpharavdlurer_d)
        """sum avdeltar = 1"""
        if 'sumavdeltareq1' in listcs:
            if self.parts:
                def sumavdeltareq1(dummy, part):
                    return sum(qv.avdeltar[reg] for reg in self.parts[part].regs) == 1
                qc.sumavdeltareq1 = Constraint(self.parts.keys(), rule=sumavdeltareq1)
        """avz = sum alpharavzr"""
        if 'avzeqsumalpharavzr' in listcs:
            # Variables to be computed ['avm', 'avmup', 'avmue', 'avdlu', 'avdl', 'avl', 'avsigmatau', 'avattau', 'avaetau', 'avdmtau']
            """avm = sum alpharavmr"""
            def alpharavmr_a(dummy, pl, re):
                return qv.alpharavmr[(pl,re)] <= qv.alphar[re]*self.wu
            qc.alpharavmr_a = Constraint(self.placexregs.keys(), rule=alpharavmr_a)
            def alpharavmr_b(dummy, pl, re):
                return qv.alpharavmr[(pl,re)] <= qv.avmr[(pl,re)]
            qc.alpharavmr_b = Constraint(self.placexregs.keys(), rule=alpharavmr_b)
            def alpharavmr_c(dummy, pl, re):
                return qv.alpharavmr[(pl,re)] >= qv.avmr[(pl,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavmr_c = Constraint(self.placexregs.keys(), rule=alpharavmr_c)
            # avm = sum alpharavmr
            if self.parts:
                def partpl_init(dummy):
                    return ((part,pl) for part in self.parts for pl in self.places)              
                partpl = Set(dimen=2, initialize=partpl_init)
                def avmeqsumalpharavmr(dummy, part, pl):
                    return qv.avm[pl] == sum(qv.alpharavmr[(pl,re)] for re in self.parts[part].regs)
                qc.avmeqsumalpharavmr = Constraint(partpl, rule=avmeqsumalpharavmr)
            """avmup = sum alpharavmupr"""
            def alpharavmupr_a(dummy, pl, re):
                return qv.alpharavmupr[(pl,re)] <= qv.alphar[re]*self.wu
            qc.alpharavmupr_a = Constraint(self.placexregs.keys(), rule=alpharavmupr_a)
            def alpharavmupr_b(dummy, pl, re):
                return qv.alpharavmupr[(pl,re)] <= qv.avmupr[(pl,re)]
            qc.alpharavmupr_b = Constraint(self.placexregs.keys(), rule=alpharavmupr_b)
            def alpharavmupr_c(dummy, pl, re):
                return qv.alpharavmupr[(pl,re)] >= qv.avmupr[(pl,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavmupr_c = Constraint(self.placexregs.keys(), rule=alpharavmupr_c)
            # avmup = sum alpharavmupr
            if self.parts:
                def partpl_init(dummy):
                    return ((part,pl) for part in self.parts for pl in self.places)              
                partpl = Set(dimen=2, initialize=partpl_init)
                def avmupeqsumalpharavmupr(dummy, part, pl):
                    return qv.avmup[pl] == sum(qv.alpharavmupr[(pl,re)] for re in self.parts[part].regs)
                qc.avmupeqsumalpharavmupr = Constraint(partpl, rule=avmupeqsumalpharavmupr)
            """avmue = sum alpharavmuer"""
            def alpharavmuer_a(dummy, sf, st, re):
                return qv.alpharavmuer[(sf,st,re)] <= qv.alphar[re]*self.wu
            qc.alpharavmuer_a = Constraint(self.sedgexregs.keys(), rule=alpharavmuer_a)
            def alpharavmuer_b(dummy, sf, st, re):
                return qv.alpharavmuer[(sf,st,re)] <= qv.avmuer[(sf,st,re)]
            qc.alpharavmuer_b = Constraint(self.sedgexregs.keys(), rule=alpharavmuer_b)
            def alpharavmuer_c(dummy, sf, st, re):
                return qv.alpharavmuer[(sf,st,re)] >= qv.avmuer[(sf,st,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavmuer_c = Constraint(self.sedgexregs.keys(), rule=alpharavmuer_c)
            # avmue = sum alpharavmuer
            if self.parts:
                def partse_init(dummy):
                    return ((part,se[0],se[1]) for part in self.parts for se in self.sedges)              
                partse = Set(dimen=3, initialize=partse_init)
                def avmueeqsumalpharavmuer(dummy, part, sf, st):
                    return qv.avmue[sf,st] == sum(qv.alpharavmuer[(sf,st,re)] for re in self.parts[part].regs)
                qc.avmueeqsumalpharavmuer = Constraint(partse, rule=avmueeqsumalpharavmuer)
            """avsigmatau = sum alpharavsigmataur"""
            def alpharavsigmataur_a(dummy, tr, re):
                return qv.alpharavsigmataur[(tr,re)] <= qv.alphar[re]*self.wu
            qc.alpharavsigmataur_a = Constraint(self.tranxregs.keys(), rule=alpharavsigmataur_a)
            def alpharavsigmataur_b(dummy, tr, re):
                return qv.alpharavsigmataur[(tr,re)] <= qv.avsigmataur[(tr,re)]
            qc.alpharavsigmataur_b = Constraint(self.tranxregs.keys(), rule=alpharavsigmataur_b)
            def alpharavsigmataur_c(dummy, tr, re):
                return qv.alpharavsigmataur[(tr,re)] >= qv.avsigmataur[(tr,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavsigmataur_c = Constraint(self.tranxregs.keys(), rule=alpharavsigmataur_c)
            # avsigmatau = sum alpharavsigmataur
            if self.parts:
                def parttr_init(dummy):
                    return ((part,tr) for part in self.parts for tr in self.trans)              
                parttr = Set(dimen=2, initialize=parttr_init)
                def avsigmataueqsumalpharavsigmataur(dummy, part, tr):
                    return qv.avsigmatau[tr] == sum(qv.alpharavsigmataur[(tr,re)] for re in self.parts[part].regs)
                qc.avsigmataueqsumalpharavsigmataur = Constraint(parttr, rule=avsigmataueqsumalpharavsigmataur)
            """avattau = sum alpharavattaur"""
            def alpharavattaur_a(dummy, tr, re):
                return qv.alpharavattaur[(tr,re)] <= qv.alphar[re]*self.wu
            qc.alpharavattaur_a = Constraint(self.tranxregs.keys(), rule=alpharavattaur_a)
            def alpharavattaur_b(dummy, tr, re):
                return qv.alpharavattaur[(tr,re)] <= qv.avattaur[(tr,re)]
            qc.alpharavattaur_b = Constraint(self.tranxregs.keys(), rule=alpharavattaur_b)
            def alpharavattaur_c(dummy, tr, re):
                return qv.alpharavattaur[(tr,re)] >= qv.avattaur[(tr,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavattaur_c = Constraint(self.tranxregs.keys(), rule=alpharavattaur_c)
            # avattau = sum alpharavattaur
            if self.parts:
                def parttr_init(dummy):
                    return ((part,tr) for part in self.parts for tr in self.trans)              
                parttr = Set(dimen=2, initialize=parttr_init)
                def avattaueqsumalpharavattaur(dummy, part, tr):
                    return qv.avattau[tr] == sum(qv.alpharavattaur[(tr,re)] for re in self.parts[part].regs)
                qc.avattaueqsumalpharavattaur = Constraint(parttr, rule=avattaueqsumalpharavattaur)
            """avaetau = sum alpharavaetaur"""
            def alpharavaetaur_a(dummy, vf, vt, re):
                return qv.alpharavaetaur[(vf,vt,re)] <= qv.alphar[re]*self.wu
            qc.alpharavaetaur_a = Constraint(self.vedgexregs.keys(), rule=alpharavaetaur_a)
            def alpharavaetaur_b(dummy, vf, vt, re):
                return qv.alpharavaetaur[(vf,vt,re)] <= qv.avaetaur[(vf,vt,re)]
            qc.alpharavaetaur_b = Constraint(self.vedgexregs.keys(), rule=alpharavaetaur_b)
            def alpharavaetaur_c(dummy, vf, vt, re):
                return qv.alpharavaetaur[(vf,vt,re)] >= qv.avaetaur[(vf,vt,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavaetaur_c = Constraint(self.vedgexregs.keys(), rule=alpharavaetaur_c)
            # avaetau = sum alpharavaetaur
            if self.parts:
                def partve_init(dummy):
                    return ((part,ve[0],ve[1]) for part in self.parts for ve in self.vedges)              
                partve = Set(dimen=3, initialize=partve_init)
                def avaetaueqsumalpharavaetaur(dummy, part, vf, vt):
                    return qv.avaetau[vf,vt] == sum(qv.alpharavaetaur[(vf,vt,re)] for re in self.parts[part].regs)
                qc.avaetaueqsumalpharavaetaur = Constraint(partve, rule=avaetaueqsumalpharavaetaur)
            """avdmtau = sum alpharavdmtaur"""
            def alpharavdmtaur_a(dummy, vf, vt, re):
                return qv.alpharavdmtaur[(vf,vt,re)] <= qv.alphar[re]*self.wu
            qc.alpharavdmtaur_a = Constraint(self.varcxregs.keys(), rule=alpharavdmtaur_a)
            def alpharavdmtaur_b(dummy, vf, vt, re):
                return qv.alpharavdmtaur[(vf,vt,re)] <= qv.avdmtaur[(vf,vt,re)]
            qc.alpharavdmtaur_b = Constraint(self.varcxregs.keys(), rule=alpharavdmtaur_b)
            def alpharavdmtaur_c(dummy, vf, vt, re):
                return qv.alpharavdmtaur[(vf,vt,re)] >= qv.avdmtaur[(vf,vt,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavdmtaur_c = Constraint(self.varcxregs.keys(), rule=alpharavdmtaur_c)
            # avdmtau = sum alpharavdmtaur
            if self.parts:
                def partva_init(dummy):
                    return ((part,va[0],va[1]) for part in self.parts for va in self.varcs)              
                partva = Set(dimen=3, initialize=partva_init)
                def avdmtaueqsumalpharavdmtaur(dummy, part, vf, vt):
                    return qv.avdmtau[vf,vt] == sum(qv.alpharavdmtaur[(vf,vt,re)] for re in self.parts[part].regs)
                qc.avdmtaueqsumalpharavdmtaur = Constraint(partva, rule=avdmtaueqsumalpharavdmtaur)
        """avz = sum avdeltaravzr"""
        if 'avzeqsumavdeltaravzr' in listcs: 
            # Assume betas are computed, i.e., constraints avdleqavdeltaavdlg_a and avdleqavdeltaavdlg_b are included
            # Variables to be computed ['avm', 'avmup', 'avmue', 'avsigmatau', 'avattau', 'avaetau', 'avdmtau']
            #                           'avdlu', 'avdl', 'avl' and 'avdsigmatau' are not computed because they do not play role in the constraints            
            """avm = sum avdeltaravmr"""
            # Computation of betaavmr
            def betaavmr_a(dummy, pl, re, q):
                return qv.betaavmr[(pl,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavmr_a = Constraint(self.placexregxqs.keys(), rule=betaavmr_a)
            def betaavmr_b(dummy, pl, re, q):
                return qv.betaavmr[(pl,re,q)] <= qv.avmr[(pl,re)]
            qc.betaavmr_b = Constraint(self.placexregxqs.keys(), rule=betaavmr_b)
            def betaavmr_c(dummy, pl, re, q):
                return qv.betaavmr[(pl,re,q)] >= qv.avmr[(pl,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavmr_c = Constraint(self.placexregxqs.keys(), rule=betaavmr_c)
            # Computation of avdeltaravmr
            def avdeltaravmr_a(dummy, pl, re):
                q = len(self.ds)-1
                return sum(qv.betaavmr[(pl,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravmr[(pl,re)]
            qc.avdeltaravmr_a = Constraint(self.placexregs.keys(), rule=avdeltaravmr_a)
            def avdeltaravmr_b(dummy, pl, re):
                q = len(self.ds)-1
                return qv.avdeltaravmr[(pl,re)] <= qv.avmr[(pl,re)]-sum(qv.avmr[(pl,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavmr[(pl,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravmr_b = Constraint(self.placexregs.keys(), rule=avdeltaravmr_b)
            # avdeltaravmr = alphar avdeltaravmr (to reduce linearization errors)
            def avdeltaravmr_c(dummy, pl, re):
                return qv.avdeltaravmr[(pl,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravmr_c = Constraint(self.placexregs.keys(), rule=avdeltaravmr_c)
            # avm = sum avdeltaravmr
            if self.parts:
                def partpl_init(dummy):
                    return ((part,pl) for part in self.parts for pl in self.places)              
                partpl = Set(dimen=2, initialize=partpl_init)
                def avmeqsumavdeltaravmr(dummy, part, pl):
                    return qv.avm[pl] == sum(qv.avdeltaravmr[(pl,re)] for re in self.parts[part].regs)
                qc.avmeqsumavdeltaravmr = Constraint(partpl, rule=avmeqsumavdeltaravmr)
                # avm = avmr if r is the only region visited of its partition (to improve linearization errors)
                def avmleqavmrwu(dummy, pl, re):
                    return qv.avm[pl] <= qv.avmr[(pl,re)] + self.wu*(1-qv.gammar[re])
                qc.avmleqavmrwu = Constraint(self.placexregs.keys(), rule=avmleqavmrwu)
                def avmgeqavmr2wu(dummy, pl, re):
                    return qv.avm[pl] >= qv.avmr[(pl,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avmgeqavmr2wu = Constraint(self.placexregs.keys(), rule=avmgeqavmr2wu)
            """avmup = sum avdeltaravmupr"""
            # Computation of betaavmupr
            def betaavmupr_a(dummy, pl, re, q):
                return qv.betaavmupr[(pl,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavmupr_a = Constraint(self.placexregxqs.keys(), rule=betaavmupr_a)
            def betaavmupr_b(dummy, pl, re, q):
                return qv.betaavmupr[(pl,re,q)] <= qv.avmupr[(pl,re)]
            qc.betaavmupr_b = Constraint(self.placexregxqs.keys(), rule=betaavmupr_b)
            def betaavmupr_c(dummy, pl, re, q):
                return qv.betaavmupr[(pl,re,q)] >= qv.avmupr[(pl,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavmupr_c = Constraint(self.placexregxqs.keys(), rule=betaavmupr_c)
            # Computation of avdeltaravmupr
            def avdeltaravmupr_a(dummy, pl, re):
                q = len(self.ds)-1
                return sum(qv.betaavmupr[(pl,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravmupr[(pl,re)]
            qc.avdeltaravmupr_a = Constraint(self.placexregs.keys(), rule=avdeltaravmupr_a)
            def avdeltaravmupr_b(dummy, pl, re):
                q = len(self.ds)-1
                return qv.avdeltaravmupr[(pl,re)] <= qv.avmupr[(pl,re)]-sum(qv.avmupr[(pl,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavmupr[(pl,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravmupr_b = Constraint(self.placexregs.keys(), rule=avdeltaravmupr_b)
            # avdeltaravmupr = alphar avdeltaravmupr (to reduce linearization errors)
            def avdeltaravmupr_c(dummy, pl, re):
                return qv.avdeltaravmupr[(pl,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravmupr_c = Constraint(self.placexregs.keys(), rule=avdeltaravmupr_c)
            # avmup = sum avdeltaravmupr
            if self.parts:
                def partpl_init(dummy):
                    return ((part,pl) for part in self.parts for pl in self.places)              
                partpl = Set(dimen=2, initialize=partpl_init)
                def avmupeqsumavdeltaravmupr(dummy, part, pl):
                    return qv.avmup[pl] == sum(qv.avdeltaravmupr[(pl,re)] for re in self.parts[part].regs)
                qc.avmupeqsumavdeltaravmupr = Constraint(partpl, rule=avmupeqsumavdeltaravmupr)
                # avmup = avmupr if r is the only region visited of its partition (to improve linearization errors)                
                def avmupleqavmuprwu(dummy, pl, re):
                    return qv.avmup[pl] <= qv.avmupr[(pl,re)] + self.wu*(1-qv.gammar[re])
                qc.avmupleqavmuprwu = Constraint(self.placexregs.keys(), rule=avmupleqavmuprwu)
                def avmupgeqavmupr2wu(dummy, pl, re):
                    return qv.avmup[pl] >= qv.avmupr[(pl,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avmupgeqavmupr2wu = Constraint(self.placexregs.keys(), rule=avmupgeqavmupr2wu)
            """avmue = sum avdeltaravmuer"""
            # Computation of betaavmuer
            def betaavmuer_a(dummy, sf, st, re, q):
                return qv.betaavmuer[(sf,st,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavmuer_a = Constraint(self.sedgexregxqs.keys(), rule=betaavmuer_a)
            def betaavmuer_b(dummy, sf, st, re, q):
                return qv.betaavmuer[(sf,st,re,q)] <= qv.avmuer[(sf,st,re)]
            qc.betaavmuer_b = Constraint(self.sedgexregxqs.keys(), rule=betaavmuer_b)
            def betaavmuer_c(dummy, sf, st, re, q):
                return qv.betaavmuer[(sf,st,re,q)] >= qv.avmuer[(sf,st,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavmuer_c = Constraint(self.sedgexregxqs.keys(), rule=betaavmuer_c)
            # Computation of avdeltaravmuer
            def avdeltaravmuer_a(dummy, sf, st, re):
                q = len(self.ds)-1
                return sum(qv.betaavmuer[(sf,st,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravmuer[(sf,st,re)]
            qc.avdeltaravmuer_a = Constraint(self.sedgexregs.keys(), rule=avdeltaravmuer_a)
            def avdeltaravmuer_b(dummy, sf, st, re):
                q = len(self.ds)-1
                return qv.avdeltaravmuer[(sf,st,re)] <= qv.avmuer[(sf, st,re)]-sum(qv.avmuer[(sf, st,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavmuer[(sf, st,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravmuer_b = Constraint(self.sedgexregs.keys(), rule=avdeltaravmuer_b)
            # avdeltaravmuer = alphar avdeltaravmuer (to reduce linearization errors)
            def avdeltaravmuer_c(dummy, sf, st, re):
                return qv.avdeltaravmuer[(sf,st,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravmuer_c = Constraint(self.sedgexregs.keys(), rule=avdeltaravmuer_c)
            # avmue = sum avdeltaravmuer
            if self.parts:
                def partse_init(dummy):
                    return ((part,se[0],se[1]) for part in self.parts for se in self.sedges)              
                partse = Set(dimen=3, initialize=partse_init)
                def avmueeqsumavdeltaravmuer(dummy, part, sf, st):
                    return qv.avmue[sf,st] == sum(qv.avdeltaravmuer[(sf,st,re)] for re in self.parts[part].regs)
                qc.avmueeqsumavdeltaravmuer = Constraint(partse, rule=avmueeqsumavdeltaravmuer)
                # avmue = avmuer if r is the only region visited of its partition (to improve linearization errors)                
                def avmueleqavmuerwu(dummy, sf, st, re):
                    return qv.avmue[sf,st] <= qv.avmuer[(sf,st,re)] + self.wu*(1-qv.gammar[re])
                qc.avmueleqavmuerwu = Constraint(self.sedgexregs.keys(), rule=avmueleqavmuerwu)
                def avmuegeqavmuer2wu(dummy, sf, st, re):
                    return qv.avmue[sf,st] >= qv.avmuer[(sf,st,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avmuegeqavmuer2wu = Constraint(self.sedgexregs.keys(), rule=avmuegeqavmuer2wu)
            """avsigmatau = sum avdeltaravsigmataur"""
            # Computation of betaavsigmataur
            def betaavsigmataur_a(dummy, tr, re, q):
                return qv.betaavsigmataur[(tr,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavsigmataur_a = Constraint(self.tranxregxqs.keys(), rule=betaavsigmataur_a)
            def betaavsigmataur_b(dummy, tr, re, q):
                return qv.betaavsigmataur[(tr,re,q)] <= qv.avsigmataur[(tr,re)]
            qc.betaavsigmataur_b = Constraint(self.tranxregxqs.keys(), rule=betaavsigmataur_b)
            def betaavsigmataur_c(dummy, tr, re, q):
                return qv.betaavsigmataur[(tr,re,q)] >= qv.avsigmataur[(tr,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavsigmataur_c = Constraint(self.tranxregxqs.keys(), rule=betaavsigmataur_c)
            # Computation of avdeltaravsigmataur
            def avdeltaravsigmataur_a(dummy, tr, re):
                q = len(self.ds)-1
                return sum(qv.betaavsigmataur[(tr,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravsigmataur[(tr,re)]
            qc.avdeltaravsigmataur_a = Constraint(self.tranxregs.keys(), rule=avdeltaravsigmataur_a)
            def avdeltaravsigmataur_b(dummy, tr, re):
                q = len(self.ds)-1
                return qv.avdeltaravsigmataur[(tr,re)] <= qv.avsigmataur[(tr,re)]-sum(qv.avsigmataur[(tr,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavsigmataur[(tr,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravsigmataur_b = Constraint(self.tranxregs.keys(), rule=avdeltaravsigmataur_b)
            # avdeltaravsigmataur = alphar avdeltaravsigmataur (to reduce linearization errors)
            def avdeltaravsigmataur_c(dummy, tr, re):
                return qv.avdeltaravsigmataur[(tr,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravsigmataur_c = Constraint(self.tranxregs.keys(), rule=avdeltaravsigmataur_c)
            # avsigmatau = sum avdeltaravsigmataur
            if self.parts:
                def parttr_init(dummy):
                    return ((part,tr) for part in self.parts for tr in self.trans)              
                parttr = Set(dimen=2, initialize=parttr_init)
                def avsigmataueqsumavdeltaravsigmataur(dummy, part, tr):
                    return qv.avsigmatau[tr] == sum(qv.avdeltaravsigmataur[(tr,re)] for re in self.parts[part].regs)
                qc.avsigmataueqsumavdeltaravsigmataur = Constraint(parttr, rule=avsigmataueqsumavdeltaravsigmataur)
                # avsigmatau = avsigmataur if r is the only region visited of its partition (to improve linearization errors)                
                def avsigmatauleqavsigmataurwu(dummy, tr, re):
                    return qv.avsigmatau[tr] <= qv.avsigmataur[(tr,re)] + self.wu*(1-qv.gammar[re])
                qc.avsigmatauleqavsigmataurwu = Constraint(self.tranxregs.keys(), rule=avsigmatauleqavsigmataurwu)
                def avsigmataugeqavsigmataur2wu(dummy, tr, re):
                    return qv.avsigmatau[tr] >= qv.avsigmataur[(tr,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avsigmataugeqavsigmataur2wu = Constraint(self.tranxregs.keys(), rule=avsigmataugeqavsigmataur2wu)
            """avattau = sum avdeltaravattaur"""
            # Computation of betaavattaur
            def betaavattaur_a(dummy, tr, re, q):
                return qv.betaavattaur[(tr,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavattaur_a = Constraint(self.tranxregxqs.keys(), rule=betaavattaur_a)
            def betaavattaur_b(dummy, tr, re, q):
                return qv.betaavattaur[(tr,re,q)] <= qv.avattaur[(tr,re)]
            qc.betaavattaur_b = Constraint(self.tranxregxqs.keys(), rule=betaavattaur_b)
            def betaavattaur_c(dummy, tr, re, q):
                return qv.betaavattaur[(tr,re,q)] >= qv.avattaur[(tr,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavattaur_c = Constraint(self.tranxregxqs.keys(), rule=betaavattaur_c)
            # Computation of avdeltaravattaur
            def avdeltaravattaur_a(dummy, tr, re):
                q = len(self.ds)-1
                return sum(qv.betaavattaur[(tr,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravattaur[(tr,re)]
            qc.avdeltaravattaur_a = Constraint(self.tranxregs.keys(), rule=avdeltaravattaur_a)
            def avdeltaravattaur_b(dummy, tr, re):
                q = len(self.ds)-1
                return qv.avdeltaravattaur[(tr,re)] <= qv.avattaur[(tr,re)]-sum(qv.avattaur[(tr,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavattaur[(tr,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravattaur_b = Constraint(self.tranxregs.keys(), rule=avdeltaravattaur_b)
            # avdeltaravattaur = alphar avdeltaravattaur (to reduce linearization errors)
            def avdeltaravattaur_c(dummy, tr, re):
                return qv.avdeltaravattaur[(tr,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravattaur_c = Constraint(self.tranxregs.keys(), rule=avdeltaravattaur_c)
            # avattau = sum avdeltaravattaur
            if self.parts:
                def parttr_init(dummy):
                    return ((part,tr) for part in self.parts for tr in self.trans)              
                parttr = Set(dimen=2, initialize=parttr_init)
                def avattaueqsumavdeltaravattaur(dummy, part, tr):
                    return qv.avattau[tr] == sum(qv.avdeltaravattaur[(tr,re)] for re in self.parts[part].regs)
                qc.avattaueqsumavdeltaravattaur = Constraint(parttr, rule=avattaueqsumavdeltaravattaur)
                # avattau = avattaur if r is the only region visited of its partition (to improve linearization errors)                
                def avattauleqavattaurwu(dummy, tr, re):
                    return qv.avattau[tr] <= qv.avattaur[(tr,re)] + self.wu*(1-qv.gammar[re])
                qc.avattauleqavattaurwu = Constraint(self.tranxregs.keys(), rule=avattauleqavattaurwu)
                def avattaugeqavattaur2wu(dummy, tr, re):
                    return qv.avattau[tr] >= qv.avattaur[(tr,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avattaugeqavattaur2wu = Constraint(self.tranxregs.keys(), rule=avattaugeqavattaur2wu)
            """avaetau = sum avdeltaravaetaur"""
            # Computation of betaavaetaur
            def betaavaetaur_a(dummy, vf, vt, re, q):
                return qv.betaavaetaur[(vf,vt,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavaetaur_a = Constraint(self.vedgexregxqs.keys(), rule=betaavaetaur_a)
            def betaavaetaur_b(dummy, vf, vt, re, q):
                return qv.betaavaetaur[(vf,vt,re,q)] <= qv.avaetaur[(vf,vt,re)]
            qc.betaavaetaur_b = Constraint(self.vedgexregxqs.keys(), rule=betaavaetaur_b)
            def betaavaetaur_c(dummy, vf, vt, re, q):
                return qv.betaavaetaur[(vf,vt,re,q)] >= qv.avaetaur[(vf,vt,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavaetaur_c = Constraint(self.vedgexregxqs.keys(), rule=betaavaetaur_c)
            # Computation of avdeltaravaetaur
            def avdeltaravaetaur_a(dummy, vf, vt, re):
                q = len(self.ds)-1
                return sum(qv.betaavaetaur[(vf,vt,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravaetaur[(vf,vt,re)]
            qc.avdeltaravaetaur_a = Constraint(self.vedgexregs.keys(), rule=avdeltaravaetaur_a)
            def avdeltaravaetaur_b(dummy, vf, vt, re):
                q = len(self.ds)-1
                return qv.avdeltaravaetaur[(vf,vt,re)] <= qv.avaetaur[(vf, vt,re)]-sum(qv.avaetaur[(vf, vt,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavaetaur[(vf, vt,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravaetaur_b = Constraint(self.vedgexregs.keys(), rule=avdeltaravaetaur_b)
            # avdeltaravaetaur = alphar avdeltaravaetaur (to reduce linearization errors)
            def avdeltaravaetaur_c(dummy, vf, vt, re):
                return qv.avdeltaravaetaur[(vf,vt,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravaetaur_c = Constraint(self.vedgexregs.keys(), rule=avdeltaravaetaur_c)
            # avaetau = sum avdeltaravaetaur
            if self.parts:
                def partve_init(dummy):
                    return ((part,ve[0],ve[1]) for part in self.parts for ve in self.vedges)              
                partve = Set(dimen=3, initialize=partve_init)
                def avaetaueqsumavdeltaravaetaur(dummy, part, vf, vt):
                    return qv.avaetau[vf,vt] == sum(qv.avdeltaravaetaur[(vf,vt,re)] for re in self.parts[part].regs)
                qc.avaetaueqsumavdeltaravaetaur = Constraint(partve, rule=avaetaueqsumavdeltaravaetaur)
                # avaetau = avaetaur if r is the only region visited of its partition (to improve linearization errors)                
                def avaetauleqavaetaurwu(dummy, vf, vt, re):
                    return qv.avaetau[vf,vt] <= qv.avaetaur[(vf, vt,re)] + self.wu*(1-qv.gammar[re])
                qc.avaetauleqavaetaurwu = Constraint(self.vedgexregs.keys(), rule=avaetauleqavaetaurwu)
                def avaetaugeqavaetaur2wu(dummy, vf, vt, re):
                    return qv.avaetau[vf,vt] >= qv.avaetaur[(vf, vt,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avaetaugeqavaetaur2wu = Constraint(self.vedgexregs.keys(), rule=avaetaugeqavaetaur2wu)
            """avdmtau = sum avdeltaravdmtaur"""
            # Computation of betaavdmtaur
            def betaavdmtaur_a(dummy, vf, vt, re, q):
                return qv.betaavdmtaur[(vf,vt,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavdmtaur_a = Constraint(self.varcxregxqs.keys(), rule=betaavdmtaur_a)
            def betaavdmtaur_b(dummy, vf, vt, re, q):
                return qv.betaavdmtaur[(vf,vt,re,q)] <= qv.avdmtaur[(vf,vt,re)]
            qc.betaavdmtaur_b = Constraint(self.varcxregxqs.keys(), rule=betaavdmtaur_b)
            def betaavdmtaur_c(dummy, vf, vt, re, q):
                return qv.betaavdmtaur[(vf,vt,re,q)] >= qv.avdmtaur[(vf,vt,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavdmtaur_c = Constraint(self.varcxregxqs.keys(), rule=betaavdmtaur_c)
            # Computation of avdeltaravdmtaur
            def avdeltaravdmtaur_a(dummy, vf, vt, re):
                q = len(self.ds)-1
                return sum(qv.betaavdmtaur[(vf,vt,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravdmtaur[(vf,vt,re)]
            qc.avdeltaravdmtaur_a = Constraint(self.varcxregs.keys(), rule=avdeltaravdmtaur_a)
            def avdeltaravdmtaur_b(dummy, vf, vt, re):
                q = len(self.ds)-1
                return qv.avdeltaravdmtaur[(vf,vt,re)] <= qv.avdmtaur[(vf,vt,re)]-sum(qv.avdmtaur[(vf, vt,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavdmtaur[(vf, vt,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravdmtaur_b = Constraint(self.varcxregs.keys(), rule=avdeltaravdmtaur_b)
            # avdeltaravdmtaur = alphar avdeltaravdmtaur (to reduce linearization errors)
            def avdeltaravdmtaur_c(dummy, vf, vt, re):
                return qv.avdeltaravdmtaur[(vf,vt,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravdmtaur_c = Constraint(self.varcxregs.keys(), rule=avdeltaravdmtaur_c)
            # avdmtau = sum avdeltaravdmtaur
            if self.parts:
                def partva_init(dummy):
                    return ((part,va[0],va[1]) for part in self.parts for va in self.varcs)              
                partva = Set(dimen=3, initialize=partva_init)
                def avdmtaueqsumavdeltaravdmtaur(dummy, part, vf, vt):
                    return qv.avdmtau[vf,vt] == sum(qv.avdeltaravdmtaur[(vf,vt,re)] for re in self.parts[part].regs)
                qc.avdmtaueqsumavdeltaravdmtaur = Constraint(partva, rule=avdmtaueqsumavdeltaravdmtaur)
                # avdmtau = avdmtaur if r is the only region visited of its partition (to improve linearization errors)                
                def avdmtauleqavdmtaurwu(dummy, vf, vt, re):
                    return qv.avdmtau[vf,vt] <= qv.avdmtaur[(vf,vt,re)] + self.wu*(1-qv.gammar[re])
                qc.avdmtauleqavdmtaurwu = Constraint(self.varcxregs.keys(), rule=avdmtauleqavdmtaurwu)
                def avdmtaugeqavdmtaur2wu(dummy, vf, vt, re):
                    return qv.avdmtau[vf,vt] >= qv.avdmtaur[(vf,vt,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avdmtaugeqavdmtaur2wu = Constraint(self.varcxregs.keys(), rule=avdmtaugeqavdmtaur2wu)
        """avdl[e] <= wutind"""
        if 'avdleleqwutind' in listcs:
            def avdleleqwutind(dummy, saf, sat):
                return qv.avdl[(saf,sat)] <= self.wu
            qc.avdleleqwutind = Constraint(self.sarcs.keys(), rule=avdleleqwutind)
        """sum_R_r in V avdeltar <= sum_R_s in W avdeltas"""
        if 'sumavdeltarVleqsumavdeltasW' in listcs:
            if self.regsin:
                def sumavdeltarVleqsumavdeltasW(dummy, r):
                    return sum(qv.avdeltar[re] for re in self.regsin[r]['sub']) <= sum(qv.avdeltar[re] for re in self.regsin[r]['sup'])
                qc.sumavdeltarVleqsumavdeltasW = Constraint(range(len(self.regsin)), rule=sumavdeltarVleqsumavdeltasW)
        """sum_R_r in V alphar <= sum_R_s in W alphas"""
        if 'sumalpharVleqsumalphasW' in listcs:
            if self.regsin:
                def sumalpharVleqsumalphasW(dummy, r):
                    return sum(qv.alphar[re] for re in self.regsin[r]['sub']) <= sum(qv.alphar[re] for re in self.regsin[r]['sup'])
                qc.sumalpharVleqsumalphasW = Constraint(range(len(self.regsin)), rule=sumalpharVleqsumalphasW)
        """sum_R_r in V' avdeltar = sum_R_s in W' avdeltas"""
        if 'sumavdeltarVpeqsumavdeltasWp' in listcs:
            if self.regseq:
                def sumavdeltarVpeqsumavdeltasWp(dummy, r):
                    return sum(qv.avdeltar[re] for re in self.regseq[r]['V']) == sum(qv.avdeltar[re] for re in self.regseq[r]['W'])
                qc.sumavdeltarVpeqsumavdeltasWp = Constraint(range(len(self.regseq)), rule=sumavdeltarVpeqsumavdeltasWp)
        """sum_R_r in V' avdeltar = sum_R_s in W' avdeltas"""
        if 'sumalpharVpeqsumalphasWp' in listcs:
            if self.regseq:
                def sumalpharVpeqsumalphasWp(dummy, r):
                    return sum(qv.alphar[re] for re in self.regseq[r]['V']) == sum(qv.alphar[re] for re in self.regseq[r]['W'])
                qc.sumalpharVpeqsumalphasWp = Constraint(range(len(self.regseq)), rule=sumalpharVpeqsumalphasWp)
        """sum_R_r in V' avdeltar avzr= sum_R_s in W' avdeltas avzs"""
        # Variables to make equal: avdeltaravmr, avdeltaravmupr, avdeltaravmuer, avdeltaravsigmataur, avdeltaravattaur, avdeltaravaetaur, avdeltaravdmtaur
        #                          'avdeltaravdlur', 'avdeltaravdlr', 'avdeltaravlr', 'avdeltaravdsigmar' are not made equal because they do not play role in the constraints            
        # Warning: It is assumed that the above variables are computed, i.e., 'avzeqsumavdeltaravzr' is in listcs
        if 'sumavdeltaravzrVpeqsumavdeltasavzsWp' in listcs:
            if self.regseq:
                # avdeltaravmr
                def plreq_init(dummy):
                    return ((pl,r) for pl in self.places for r in range(len(self.regseq)))              
                plreq = Set(dimen=2, initialize=plreq_init)
                def regseqavdeltaravmr(dummy, pl, r):
                    return sum(qv.avdeltaravmr[(pl,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravmr[(pl,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravmr = Constraint(plreq, rule=regseqavdeltaravmr)
                # avdeltaravmupr       
                def regseqavdeltaravmupr(dummy, pl, r):
                    return sum(qv.avdeltaravmupr[(pl,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravmupr[(pl,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravmupr = Constraint(plreq, rule=regseqavdeltaravmupr)
                def sereq_init(dummy):
                    return ((se[0],se[1],r) for se in self.sedges for r in range(len(self.regseq)))              
                sereq = Set(dimen=3, initialize=sereq_init)
                # avdeltaravmuer       
                def regseqavdeltaravmuer(dummy, sf, st, r):
                    return sum(qv.avdeltaravmuer[(sf,st,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravmuer[(sf,st,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravmuer = Constraint(sereq, rule=regseqavdeltaravmuer)
                # avdeltaravsigmataur       
                def trreq_init(dummy):
                    return ((tr,r) for tr in self.trans for r in range(len(self.regseq)))              
                trreq = Set(dimen=2, initialize=trreq_init)
                def regseqavdeltaravsigmataur(dummy, tr, r):
                    return sum(qv.avdeltaravsigmataur[(tr,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravsigmataur[(tr,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravsigmataur = Constraint(trreq, rule=regseqavdeltaravsigmataur)
                # avdeltaravattaur       
                def regseqavdeltaravattaur(dummy, tr, r):
                    return sum(qv.avdeltaravattaur[(tr,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravattaur[(tr,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravattaur = Constraint(trreq, rule=regseqavdeltaravattaur)
                # avdeltaravaetaur       
                def vereq_init(dummy):
                    return ((ve[0],ve[1],r) for ve in self.vedges for r in range(len(self.regseq)))              
                vereq = Set(dimen=3, initialize=vereq_init)
                def regseqavdeltaravaetaur(dummy, vf, vt, r):
                    return sum(qv.avdeltaravaetaur[(vf,vt,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravaetaur[(vf,vt,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravaetaur = Constraint(vereq, rule=regseqavdeltaravaetaur)
                # avdeltaravdmtaur       
                def vareq_init(dummy):
                    return ((va[0],va[1],r) for va in self.varcs for r in range(len(self.regseq)))              
                vareq = Set(dimen=3, initialize=vareq_init)
                def regseqavdeltaravdmtaur(dummy, vf, vt, r):
                    return sum(qv.avdeltaravdmtaur[(vf,vt,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravdmtaur[(vf,vt,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravdmtaur = Constraint(vareq, rule=regseqavdeltaravdmtaur)
        """sum_R_r in V' alphar avzr= sum_R_s in W' alphas avzs"""
        # Variables to make equal: alpharavmr, alpharavmupr, alpharavmuer, alpharavsigmataur, alpharavattaur, alpharavaetaur, alpharavdmtaur
        #                          'alpharavdlur', 'alpharavdlr', 'alpharavlr', 'alpharavdsigmar' are not made equal because they do not play role in the constraints            
        # Warning: It is assumed that the above variables are computed, i.e., 'avzeqsumalpharavzr' is in listcs
        if 'sumalpharavzrVpeqsumalphasavzsWp' in listcs: 
            if self.regseq:
                # alpharavmr
                def plreq_init(dummy):
                    return ((pl,r) for pl in self.places for r in range(len(self.regseq)))              
                plreq = Set(dimen=2, initialize=plreq_init)
                def regseqalpharavmr(dummy, pl, r):
                    return sum(qv.alpharavmr[(pl,re)] for re in self.regseq[r]['V']) == sum(qv.alpharavmr[(pl,re)] for re in self.regseq[r]['W'])
                qc.regseqalpharavmr = Constraint(plreq, rule=regseqalpharavmr)
                # alpharavmupr       
                def regseqalpharavmupr(dummy, pl, r):
                    return sum(qv.alpharavmupr[(pl,re)] for re in self.regseq[r]['V']) == sum(qv.alpharavmupr[(pl,re)] for re in self.regseq[r]['W'])
                qc.regseqalpharavmupr = Constraint(plreq, rule=regseqalpharavmupr)
                def sereq_init(dummy):
                    return ((se[0],se[1],r) for se in self.sedges for r in range(len(self.regseq)))              
                sereq = Set(dimen=3, initialize=sereq_init)
                # alpharavmuer       
                def regseqalpharavmuer(dummy, sf, st, r):
                    return sum(qv.alpharavmuer[(sf,st,re)] for re in self.regseq[r]['V']) == sum(qv.alpharavmuer[(sf,st,re)] for re in self.regseq[r]['W'])
                qc.regseqalpharavmuer = Constraint(sereq, rule=regseqalpharavmuer)
                # alpharavsigmataur       
                def trreq_init(dummy):
                    return ((tr,r) for tr in self.trans for r in range(len(self.regseq)))              
                trreq = Set(dimen=2, initialize=trreq_init)
                def regseqalpharavsigmataur(dummy, tr, r):
                    return sum(qv.alpharavsigmataur[(tr,re)] for re in self.regseq[r]['V']) == sum(qv.alpharavsigmataur[(tr,re)] for re in self.regseq[r]['W'])
                qc.regseqalpharavsigmataur = Constraint(trreq, rule=regseqalpharavsigmataur)
                # alpharavattaur       
                def regseqalpharavattaur(dummy, tr, r):
                    return sum(qv.alpharavattaur[(tr,re)] for re in self.regseq[r]['V']) == sum(qv.alpharavattaur[(tr,re)] for re in self.regseq[r]['W'])
                qc.regseqalpharavattaur = Constraint(trreq, rule=regseqalpharavattaur)
                # alpharavaetaur       
                def vereq_init(dummy):
                    return ((ve[0],ve[1],r) for ve in self.vedges for r in range(len(self.regseq)))              
                vereq = Set(dimen=3, initialize=vereq_init)
                def regseqalpharavaetaur(dummy, vf, vt, r):
                    return sum(qv.alpharavaetaur[(vf,vt,re)] for re in self.regseq[r]['V']) == sum(qv.alpharavaetaur[(vf,vt,re)] for re in self.regseq[r]['W'])
                qc.regseqalpharavaetaur = Constraint(vereq, rule=regseqalpharavaetaur)
                # alpharavdmtaur       
                def vareq_init(dummy):
                    return ((va[0],va[1],r) for va in self.varcs for r in range(len(self.regseq)))              
                vareq = Set(dimen=3, initialize=vareq_init)
                def regseqalpharavdmtaur(dummy, vf, vt, r):
                    return sum(qv.alpharavdmtaur[(vf,vt,re)] for re in self.regseq[r]['V']) == sum(qv.alpharavdmtaur[(vf,vt,re)] for re in self.regseq[r]['W'])
                qc.regseqalpharavdmtaur = Constraint(vareq, rule=regseqalpharavdmtaur)
        """Sr x <= Qr"""
        if 'SrxleqQr' in listcs and hasattr(self,'curreg'):
            def SrxleqQr(dummy, row):
                reg = self.curreg
                dicvars = {var:getattr(qv,var) for var in FlexN.vdimdomtr if hasattr(qv,var)} # vdimdomun could be used instead of vdimdomtr but then var dsigma is not available
                return eval(self.regs[reg].SQrows[row], dicvars)
            qc.SrxleqQr = Constraint(range(len(self.regs[self.curreg].SQrows)), rule=SrxleqQr)
        """dl[e] = dlu[(e,r) for every e in E_S^T such that R_r in phi(e)"""
        if 'dleeqdluer' in listcs and hasattr(self,'curreg'):
            def dleeqdluer(dummy, saf, sat):
                sa = (saf,sat)
                if self.curreg in self.sarcs[sa].phi:
                    return qv.dl[sa] == qv.dlu[(saf,sat,self.curreg)]
                else:
                    return Constraint.Feasible
            qc.dleeqdluer = Constraint(self.sarcs.keys(), rule=dleeqdluer)
        """Sr avxr <= Qr + W(1-alphar)"""
        if 'SravxrleqQrW1alphar' in listcs:
            def avregrowsq_init(dummy):
                return ((reg,row) for reg in self.regs for row in range(len(self.regs[reg].SQrows)))              
            avregrowsq = Set(dimen=2, initialize=avregrowsq_init)
            def SravxrleqQrW1alphar(dummy, reg, row):
                dicvars = {var:getattr(qv,'av'+var+'r') for var in FlexN.vdimdomtr if hasattr(qv,'av'+var+'r')}
                dicvars['alphar'] = qv.alphar
                dicvars['W'] = self.W
                dicvars['reg'] = reg
                sqrreg = self.regs[reg].SQrows[row].replace("]", ",reg]")
                if sqrreg.find('<=') >= 0:
                    return eval(sqrreg+"+W*(1-alphar[reg])", dicvars)
                elif sqrreg.find('>=') >= 0:                    
                    return eval(sqrreg+"-W*(1-alphar[reg])", dicvars)
                else:
                    raise ValueError('Only <= and >= are allowed for SQ matrices')
            qc.SravxrleqQrW1alphar = Constraint(avregrowsq, rule=SravxrleqQrW1alphar)
        """avsigmar = avatr + Ys avaer"""    
        if 'avsigmareqavatrYsigmaavaer' in listcs:
            def avsigmareqavatrYsigmaavaer(dummy, tr, re):
                if tr in self.Ys:
                    return qv.avsigmar[(tr, re)] == qv.avatr[(tr, re)] + sum(qv.avaer[(edge[0],edge[1],re)] for edge in self.Ys[tr])
                else: # Transition not connected to vhandler
                    return qv.avsigmar[(tr, re)] == qv.avatr[(tr, re)]
            qc.avsigmareqavatrYsigmaavaer = Constraint(self.tranxregs.keys(), rule=avsigmareqavatrYsigmaavaer)
        """avsigmar + a0 = avatr + Ys avaer"""    
        if 'avsigmara0eqavatrYsigmaavaer' in listcs:
            def avsigmara0eqavatrYsigmaavaer(dummy, tr, re):
                if tr in self.Ys:
                    return qv.avsigmar[(tr, re)] + qv.a0[tr] == qv.avatr[(tr, re)] + sum(qv.avaer[(edge[0],edge[1],re)] for edge in self.Ys[tr])
                else: # Transition not connected to vhandler
                    return qv.avsigmar[(tr, re)] + qv.a0[tr] == qv.avatr[(tr, re)]
            qc.avsigmara0eqavatrYsigmaavaer = Constraint(self.tranxregs.keys(), rule=avsigmara0eqavatrYsigmaavaer)
        """A avdmr <= B avaer"""    
        if 'AavdmrleqBavaer' in listcs:
            def regrowabr_init(dummy):
                return ((reg,row) for reg in self.regs for row in self.AB.keys())              
            regrowabr = Set(dimen=2, initialize=regrowabr_init)
            def AavdmrleqBavaer(dummy, reg, row):
                dicvars = {}
                for arc in self.AB[row]['arcs']:
                    dicvars[arc] = qv.avdmr[self.AB[row]['nickae'][arc],reg]
                for edge in self.AB[row]['edges']:
                    dicvars[edge] = qv.avaer[self.AB[row]['nickae'][edge],reg]
                return eval(self.AB[row]['expr'], dicvars)
            qc.AavdmrleqBavaer = Constraint(regrowabr, rule=AavdmrleqBavaer)
        """avmr = m0 + Zm avdmr"""    
        if 'avmreqm0Zmavdmr' in listcs:
            def avmreqm0Zmavdmr(dummy, pl, re):
                if pl in self.Zm:
                    return qv.avmr[(pl,re)] == qv.m0[pl] + sum(arc[1]*qv.avdmr[(arc[0][0],arc[0][1],re)] for arc in self.Zm[pl])
                else: # Transition not connected to shandler
                    return qv.avmr[(pl,re)] == qv.m0[pl]
            qc.avmreqm0Zmavdmr = Constraint(self.placexregs.keys(), rule=avmreqm0Zmavdmr)
        """epsilon - avdeltar <= 2(1-alphar)""" # Compute alphar and gammar   
        if 'epsavdeltarleq21alphar' in listcs:
            def epsavdeltarleq21alphar(dummy, re):
                return self.options['epsilonalga'] - qv.avdeltar[re] <= 2*(1 - qv.alphar[re])
            qc.epsavdeltarleq21alphar = Constraint(self.regs.keys(), rule=epsavdeltarleq21alphar)
            """avdeltar <= alphar"""    # Round avdeltar to 0 if alphar=0
            def avdeltarlealphar(dummy, re):
                return qv.avdeltar[re] <= qv.alphar[re]
            qc.avdeltarlealphar = Constraint(self.regs.keys(), rule=avdeltarlealphar)
            """1-epsilon <= avdeltar + 2(1-gammar)""" # Compute gammar
            def oneepsleqavldetar21gammar(dummy, re):
                return 1-self.options['epsilonalga'] <= qv.avdeltar[re] + 2*(1 - qv.gammar[re])
            qc.oneepsleqavldetar21gammar = Constraint(self.regs.keys(), rule=oneepsleqavldetar21gammar)
            """1-epsilon >= avdeltar - 2 gammar""" # Compute gammar
            def oneepsgeqavldetar2gammar(dummy, re):
                return 1-self.options['epsilonalga'] >= qv.avdeltar[re] - 2*qv.gammar[re]
            qc.oneepsgeqavldetar2gammar = Constraint(self.regs.keys(), rule=oneepsgeqavldetar2gammar)
        """epsilon - avdeltar >= -2alphar"""    
        if 'epsavdeltargeq2alphar' in listcs:
            def epsavdeltargeq2alphar(dummy, re):
                return self.options['epsilonalga'] - qv.avdeltar[re] >= -2*qv.alphar[re]
            qc.epsavdeltargeq2alphar = Constraint(self.regs.keys(), rule=epsavdeltargeq2alphar)
        """alphar avaer <= ae"""    
        if 'alpharavaerleqae' in listcs:
            # Computation of alpharavaer
            def alpharavaer_a(dummy, vf, vt, re):
                return qv.alpharavaer[(vf,vt,re)] <= qv.alphar[re]*self.wu
            qc.alpharavaer_a = Constraint(self.vedgexregs.keys(), rule=alpharavaer_a)
            def alpharavaer_b(dummy, vf, vt, re):
                return qv.alpharavaer[(vf,vt,re)] <= qv.avaer[(vf,vt,re)]
            qc.alpharavaer_b = Constraint(self.vedgexregs.keys(), rule=alpharavaer_b)
            def alpharavaer_c(dummy, vf, vt, re):
                return qv.alpharavaer[(vf,vt,re)] >= qv.avaer[(vf,vt,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavaer_c = Constraint(self.vedgexregs.keys(), rule=alpharavaer_c)
            # alphar avaer <= ae
            def alpharavaerleqae(dummy, vf, vt, re):
                return qv.alpharavaer[(vf,vt,re)] <= qv.ae[(vf,vt)]
            qc.alpharavaerleqae = Constraint(self.vedgexregs.keys(), rule=alpharavaerleqae)
        """alphar avdmr <= dm"""    
        if 'alpharavdmrleqdm' in listcs:
            # Computation of alpharavdmr
            def alpharavdmr_a(dummy, vf, vt, re):
                return qv.alpharavdmr[(vf,vt,re)] <= qv.alphar[re]*self.wu
            qc.alpharavdmr_a = Constraint(self.varcxregs.keys(), rule=alpharavdmr_a)
            def alpharavdmr_b(dummy, vf, vt, re):
                return qv.alpharavdmr[(vf,vt,re)] <= qv.avdmr[(vf,vt,re)]
            qc.alpharavdmr_b = Constraint(self.varcxregs.keys(), rule=alpharavdmr_b)
            def alpharavdmr_c(dummy, vf, vt, re):
                return qv.alpharavdmr[(vf,vt,re)] >= qv.avdmr[(vf,vt,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavdmr_c = Constraint(self.varcxregs.keys(), rule=alpharavdmr_c)
            # alphar avdmr <= dm
            def alpharavdmrleqdm(dummy, vf, vt, re):
                return qv.alpharavdmr[(vf,vt,re)] <= qv.dm[(vf,vt)]
            qc.alpharavdmrleqdm = Constraint(self.varcxregs.keys(), rule=alpharavdmrleqdm)
        """alphar avdsigmar <= dsigma"""    
        if 'alpharavdsigmarleqdsigma' in listcs:
            # Computation of alpharavdsigmar
            def alpharavdsigmar_a(dummy, sf, st, re):
                return qv.alpharavdsigmar[(sf,st,re)] <= qv.alphar[re]*self.wu
            qc.alpharavdsigmar_a = Constraint(self.sarcxregs.keys(), rule=alpharavdsigmar_a)
            def alpharavdsigmar_b(dummy, sf, st, re):
                return qv.alpharavdsigmar[(sf,st,re)] <= qv.avdsigmar[(sf,st,re)]
            qc.alpharavdsigmar_b = Constraint(self.sarcxregs.keys(), rule=alpharavdsigmar_b)
            def alpharavdsigmar_c(dummy, sf, st, re):
                return qv.alpharavdsigmar[(sf,st,re)] >= qv.avdsigmar[(sf,st,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavdsigmar_c = Constraint(self.sarcxregs.keys(), rule=alpharavdsigmar_c)
            # alphar avdsigmar <= dsigma
            def alpharavdsigmarleqdsigma(dummy, sf, st, re):
                return qv.alpharavdsigmar[(sf,st,re)] <= qv.dsigma[(sf,st)]
            qc.alpharavdsigmarleqdsigma = Constraint(self.sarcxregs.keys(), rule=alpharavdsigmarleqdsigma)
        """alphar avsigmar <= sigma"""    
        if 'alpharavsigmarleqsigma' in listcs:
            # Computation of alpharavsigmar
            def alpharavsigmar_a(dummy, tr, re):
                return qv.alpharavsigmar[(tr,re)] <= qv.alphar[re]*self.wu
            qc.alpharavsigmar_a = Constraint(self.tranxregs.keys(), rule=alpharavsigmar_a)
            def alpharavsigmar_b(dummy, tr, re):
                return qv.alpharavsigmar[(tr,re)] <= qv.avsigmar[(tr,re)]
            qc.alpharavsigmar_b = Constraint(self.tranxregs.keys(), rule=alpharavsigmar_b)
            def alpharavsigmar_c(dummy, tr, re):
                return qv.alpharavsigmar[(tr,re)] >= qv.avsigmar[(tr,re)] - self.wu*(1-qv.alphar[re])
            qc.alpharavsigmar_c = Constraint(self.tranxregs.keys(), rule=alpharavsigmar_c)
            # alphar avsigmar <= sigma
            def alpharavsigmarleqsigma(dummy, tr, re):
                return qv.alpharavsigmar[(tr,re)] <= qv.sigma[tr]
            qc.alpharavsigmarleqsigma = Constraint(self.tranxregs.keys(), rule=alpharavsigmarleqsigma)
        """avx = sum avdeltaravxr"""
        if 'avxeqsumavdeltaravxr' in listcs: 
            # Assume betas are computed, i.e., constraints avdleqavdeltaavdlg_a and avdleqavdeltaavdlg_b are included
            # Variables to be computed ['avm', 'avmup', 'avmue', 'avsigma', 'avat', 'avae', 'avdm']
            #                           'avdlu', 'avdl', 'avl', 'avdsigma' are not computed because they do not play role in the constraints            
            """avm = sum avdeltaravmr"""
            # Computation of betaavmr
            def betaavmr_a(dummy, pl, re, q):
                return qv.betaavmr[(pl,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavmr_a = Constraint(self.placexregxqs.keys(), rule=betaavmr_a)
            def betaavmr_b(dummy, pl, re, q):
                return qv.betaavmr[(pl,re,q)] <= qv.avmr[(pl,re)]
            qc.betaavmr_b = Constraint(self.placexregxqs.keys(), rule=betaavmr_b)
            def betaavmr_c(dummy, pl, re, q):
                return qv.betaavmr[(pl,re,q)] >= qv.avmr[(pl,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavmr_c = Constraint(self.placexregxqs.keys(), rule=betaavmr_c)
            # Computation of avdeltaravmr
            def avdeltaravmr_a(dummy, pl, re):
                q = len(self.ds)-1
                return sum(qv.betaavmr[(pl,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravmr[(pl,re)]
            qc.avdeltaravmr_a = Constraint(self.placexregs.keys(), rule=avdeltaravmr_a)
            def avdeltaravmr_b(dummy, pl, re):
                q = len(self.ds)-1
                return qv.avdeltaravmr[(pl,re)] <= qv.avmr[(pl,re)]-sum(qv.avmr[(pl,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavmr[(pl,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravmr_b = Constraint(self.placexregs.keys(), rule=avdeltaravmr_b)
            # avdeltaravmr = alphar avdeltaravmr (to reduce linearization errors)
            def avdeltaravmr_c(dummy, pl, re):
                return qv.avdeltaravmr[(pl,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravmr_c = Constraint(self.placexregs.keys(), rule=avdeltaravmr_c)
            # avm = sum avdeltaravmr
            if self.parts:
                def partpl_init(dummy):
                    return ((part,pl) for part in self.parts for pl in self.places)              
                partpl = Set(dimen=2, initialize=partpl_init)
                def avmeqsumavdeltaravmr(dummy, part, pl):
                    return qv.avm[pl] == sum(qv.avdeltaravmr[(pl,re)] for re in self.parts[part].regs)
                qc.avmeqsumavdeltaravmr = Constraint(partpl, rule=avmeqsumavdeltaravmr)
                # avm = avmr if r is the only region visited of its partition (to improve linearization errors)
                def avmleqavmrwu(dummy, pl, re):
                    return qv.avm[pl] <= qv.avmr[(pl,re)] + self.wu*(1-qv.gammar[re])
                qc.avmleqavmrwu = Constraint(self.placexregs.keys(), rule=avmleqavmrwu)
                def avmgeqavmr2wu(dummy, pl, re):
                    return qv.avm[pl] >= qv.avmr[(pl,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avmgeqavmr2wu = Constraint(self.placexregs.keys(), rule=avmgeqavmr2wu)
            """avmup = sum avdeltaravmupr"""
            # Computation of betaavmupr
            def betaavmupr_a(dummy, pl, re, q):
                return qv.betaavmupr[(pl,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavmupr_a = Constraint(self.placexregxqs.keys(), rule=betaavmupr_a)
            def betaavmupr_b(dummy, pl, re, q):
                return qv.betaavmupr[(pl,re,q)] <= qv.avmupr[(pl,re)]
            qc.betaavmupr_b = Constraint(self.placexregxqs.keys(), rule=betaavmupr_b)
            def betaavmupr_c(dummy, pl, re, q):
                return qv.betaavmupr[(pl,re,q)] >= qv.avmupr[(pl,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavmupr_c = Constraint(self.placexregxqs.keys(), rule=betaavmupr_c)
            # Computation of avdeltaravmupr
            def avdeltaravmupr_a(dummy, pl, re):
                q = len(self.ds)-1
                return sum(qv.betaavmupr[(pl,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravmupr[(pl,re)]
            qc.avdeltaravmupr_a = Constraint(self.placexregs.keys(), rule=avdeltaravmupr_a)
            def avdeltaravmupr_b(dummy, pl, re):
                q = len(self.ds)-1
                return qv.avdeltaravmupr[(pl,re)] <= qv.avmupr[(pl,re)]-sum(qv.avmupr[(pl,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavmupr[(pl,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravmupr_b = Constraint(self.placexregs.keys(), rule=avdeltaravmupr_b)
            # avdeltaravmupr = alphar avdeltaravmupr (to reduce linearization errors)
            def avdeltaravmupr_c(dummy, pl, re):
                return qv.avdeltaravmupr[(pl,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravmupr_c = Constraint(self.placexregs.keys(), rule=avdeltaravmupr_c)
            # avmup = sum avdeltaravmupr
            if self.parts:
                def partpl_init(dummy):
                    return ((part,pl) for part in self.parts for pl in self.places)              
                partpl = Set(dimen=2, initialize=partpl_init)
                def avmupeqsumavdeltaravmupr(dummy, part, pl):
                    return qv.avmup[pl] == sum(qv.avdeltaravmupr[(pl,re)] for re in self.parts[part].regs)
                qc.avmupeqsumavdeltaravmupr = Constraint(partpl, rule=avmupeqsumavdeltaravmupr)
                # avmup = avmupr if r is the only region visited of its partition (to improve linearization errors)                
                def avmupleqavmuprwu(dummy, pl, re):
                    return qv.avmup[pl] <= qv.avmupr[(pl,re)] + self.wu*(1-qv.gammar[re])
                qc.avmupleqavmuprwu = Constraint(self.placexregs.keys(), rule=avmupleqavmuprwu)
                def avmupgeqavmupr2wu(dummy, pl, re):
                    return qv.avmup[pl] >= qv.avmupr[(pl,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avmupgeqavmupr2wu = Constraint(self.placexregs.keys(), rule=avmupgeqavmupr2wu)
            """avmue = sum avdeltaravmuer"""
            # Computation of betaavmuer
            def betaavmuer_a(dummy, sf, st, re, q):
                return qv.betaavmuer[(sf,st,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavmuer_a = Constraint(self.sedgexregxqs.keys(), rule=betaavmuer_a)
            def betaavmuer_b(dummy, sf, st, re, q):
                return qv.betaavmuer[(sf,st,re,q)] <= qv.avmuer[(sf,st,re)]
            qc.betaavmuer_b = Constraint(self.sedgexregxqs.keys(), rule=betaavmuer_b)
            def betaavmuer_c(dummy, sf, st, re, q):
                return qv.betaavmuer[(sf,st,re,q)] >= qv.avmuer[(sf,st,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavmuer_c = Constraint(self.sedgexregxqs.keys(), rule=betaavmuer_c)
            # Computation of avdeltaravmuer
            def avdeltaravmuer_a(dummy, sf, st, re):
                q = len(self.ds)-1
                return sum(qv.betaavmuer[(sf,st,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravmuer[(sf,st,re)]
            qc.avdeltaravmuer_a = Constraint(self.sedgexregs.keys(), rule=avdeltaravmuer_a)
            def avdeltaravmuer_b(dummy, sf, st, re):
                q = len(self.ds)-1
                return qv.avdeltaravmuer[(sf,st,re)] <= qv.avmuer[(sf, st,re)]-sum(qv.avmuer[(sf, st,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavmuer[(sf, st,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravmuer_b = Constraint(self.sedgexregs.keys(), rule=avdeltaravmuer_b)
            # avdeltaravmuer = alphar avdeltaravmuer (to reduce linearization errors)
            def avdeltaravmuer_c(dummy, sf, st, re):
                return qv.avdeltaravmuer[(sf,st,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravmuer_c = Constraint(self.sedgexregs.keys(), rule=avdeltaravmuer_c)
            # avmue = sum avdeltaravmuer
            if self.parts:
                def partse_init(dummy):
                    return ((part,se[0],se[1]) for part in self.parts for se in self.sedges)              
                partse = Set(dimen=3, initialize=partse_init)
                def avmueeqsumavdeltaravmuer(dummy, part, sf, st):
                    return qv.avmue[sf,st] == sum(qv.avdeltaravmuer[(sf,st,re)] for re in self.parts[part].regs)
                qc.avmueeqsumavdeltaravmuer = Constraint(partse, rule=avmueeqsumavdeltaravmuer)
                # avmue = avmuer if r is the only region visited of its partition (to improve linearization errors)                
                def avmueleqavmuerwu(dummy, sf, st, re):
                    return qv.avmue[sf,st] <= qv.avmuer[(sf,st,re)] + self.wu*(1-qv.gammar[re])
                qc.avmueleqavmuerwu = Constraint(self.sedgexregs.keys(), rule=avmueleqavmuerwu)
                def avmuegeqavmuer2wu(dummy, sf, st, re):
                    return qv.avmue[sf,st] >= qv.avmuer[(sf,st,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avmuegeqavmuer2wu = Constraint(self.sedgexregs.keys(), rule=avmuegeqavmuer2wu)
            """avdlu, avdl, avl not computed as sums of averages of regions (notice dlu can be negative, avdl and avl do not play roles in the evolution)"""
            """avsigma = sum avdeltaravsigmar"""
            # Computation of betaavsigmar
            def betaavsigmar_a(dummy, tr, re, q):
                return qv.betaavsigmar[(tr,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavsigmar_a = Constraint(self.tranxregxqs.keys(), rule=betaavsigmar_a)
            def betaavsigmar_b(dummy, tr, re, q):
                return qv.betaavsigmar[(tr,re,q)] <= qv.avsigmar[(tr,re)]
            qc.betaavsigmar_b = Constraint(self.tranxregxqs.keys(), rule=betaavsigmar_b)
            def betaavsigmar_c(dummy, tr, re, q):
                return qv.betaavsigmar[(tr,re,q)] >= qv.avsigmar[(tr,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavsigmar_c = Constraint(self.tranxregxqs.keys(), rule=betaavsigmar_c)
            # Computation of avdeltaravsigmar
            def avdeltaravsigmar_a(dummy, tr, re):
                q = len(self.ds)-1
                return sum(qv.betaavsigmar[(tr,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravsigmar[(tr,re)]
            qc.avdeltaravsigmar_a = Constraint(self.tranxregs.keys(), rule=avdeltaravsigmar_a)
            def avdeltaravsigmar_b(dummy, tr, re):
                q = len(self.ds)-1
                return qv.avdeltaravsigmar[(tr,re)] <= qv.avsigmar[(tr,re)]-sum(qv.avsigmar[(tr,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavsigmar[(tr,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravsigmar_b = Constraint(self.tranxregs.keys(), rule=avdeltaravsigmar_b)
            # avdeltaravsigmar = alphar avdeltaravsigmar (to reduce linearization errors)
            def avdeltaravsigmar_c(dummy, tr, re):
                return qv.avdeltaravsigmar[(tr,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravsigmar_c = Constraint(self.tranxregs.keys(), rule=avdeltaravsigmar_c)
            # avsigma = sum avdeltaravsigmar
            if self.parts:
                def parttr_init(dummy):
                    return ((part,tr) for part in self.parts for tr in self.trans)              
                parttr = Set(dimen=2, initialize=parttr_init)
                def avsigmaeqsumavdeltaravsigmar(dummy, part, tr):
                    return qv.avsigma[tr] == sum(qv.avdeltaravsigmar[(tr,re)] for re in self.parts[part].regs)
                qc.avsigmaeqsumavdeltaravsigmar = Constraint(parttr, rule=avsigmaeqsumavdeltaravsigmar)
                # avsigma = avsigmar if r is the only region visited of its partition (to improve linearization errors)                
                def avsigmaleqavsigmarwu(dummy, tr, re):
                    return qv.avsigma[tr] <= qv.avsigmar[(tr,re)] + self.wu*(1-qv.gammar[re])
                qc.avsigmaleqavsigmarwu = Constraint(self.tranxregs.keys(), rule=avsigmaleqavsigmarwu)
                def avsigmageqavsigmar2wu(dummy, tr, re):
                    return qv.avsigma[tr] >= qv.avsigmar[(tr,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avsigmageqavsigmar2wu = Constraint(self.tranxregs.keys(), rule=avsigmageqavsigmar2wu)
            """avat = sum avdeltaravatr"""
            # Computation of betaavatr
            def betaavatr_a(dummy, tr, re, q):
                return qv.betaavatr[(tr,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavatr_a = Constraint(self.tranxregxqs.keys(), rule=betaavatr_a)
            def betaavatr_b(dummy, tr, re, q):
                return qv.betaavatr[(tr,re,q)] <= qv.avatr[(tr,re)]
            qc.betaavatr_b = Constraint(self.tranxregxqs.keys(), rule=betaavatr_b)
            def betaavatr_c(dummy, tr, re, q):
                return qv.betaavatr[(tr,re,q)] >= qv.avatr[(tr,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavatr_c = Constraint(self.tranxregxqs.keys(), rule=betaavatr_c)
            # Computation of avdeltaravatr
            def avdeltaravatr_a(dummy, tr, re):
                q = len(self.ds)-1
                return sum(qv.betaavatr[(tr,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravatr[(tr,re)]
            qc.avdeltaravatr_a = Constraint(self.tranxregs.keys(), rule=avdeltaravatr_a)
            def avdeltaravatr_b(dummy, tr, re):
                q = len(self.ds)-1
                return qv.avdeltaravatr[(tr,re)] <= qv.avatr[(tr,re)]-sum(qv.avatr[(tr,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavatr[(tr,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravatr_b = Constraint(self.tranxregs.keys(), rule=avdeltaravatr_b)
            # avdeltaravatr = alphar avdeltaravatr (to reduce linearization errors)
            def avdeltaravatr_c(dummy, tr, re):
                return qv.avdeltaravatr[(tr,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravatr_c = Constraint(self.tranxregs.keys(), rule=avdeltaravatr_c)
            # avat = sum avdeltaravatr
            if self.parts:
                def parttr_init(dummy):
                    return ((part,tr) for part in self.parts for tr in self.trans)              
                parttr = Set(dimen=2, initialize=parttr_init)
                def avateqsumavdeltaravatr(dummy, part, tr):
                    return qv.avat[tr] == sum(qv.avdeltaravatr[(tr,re)] for re in self.parts[part].regs)
                qc.avateqsumavdeltaravatr = Constraint(parttr, rule=avateqsumavdeltaravatr)
                # avat = avatr if r is the only region visited of its partition (to improve linearization errors)                
                def avatleqavatrwu(dummy, tr, re):
                    return qv.avat[tr] <= qv.avatr[(tr,re)] + self.wu*(1-qv.gammar[re])
                qc.avatleqavatrwu = Constraint(self.tranxregs.keys(), rule=avatleqavatrwu)
                def avatgeqavatr2wu(dummy, tr, re):
                    return qv.avat[tr] >= qv.avatr[(tr,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avatgeqavatr2wu = Constraint(self.tranxregs.keys(), rule=avatgeqavatr2wu)
            """avae = sum avdeltaravaer"""
            # Computation of betaavaer
            def betaavaer_a(dummy, vf, vt, re, q):
                return qv.betaavaer[(vf,vt,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavaer_a = Constraint(self.vedgexregxqs.keys(), rule=betaavaer_a)
            def betaavaer_b(dummy, vf, vt, re, q):
                return qv.betaavaer[(vf,vt,re,q)] <= qv.avaer[(vf,vt,re)]
            qc.betaavaer_b = Constraint(self.vedgexregxqs.keys(), rule=betaavaer_b)
            def betaavaer_c(dummy, vf, vt, re, q):
                return qv.betaavaer[(vf,vt,re,q)] >= qv.avaer[(vf,vt,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavaer_c = Constraint(self.vedgexregxqs.keys(), rule=betaavaer_c)
            # Computation of avdeltaravaer
            def avdeltaravaer_a(dummy, vf, vt, re):
                q = len(self.ds)-1
                return sum(qv.betaavaer[(vf,vt,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravaer[(vf,vt,re)]
            qc.avdeltaravaer_a = Constraint(self.vedgexregs.keys(), rule=avdeltaravaer_a)
            def avdeltaravaer_b(dummy, vf, vt, re):
                q = len(self.ds)-1
                return qv.avdeltaravaer[(vf,vt,re)] <= qv.avaer[(vf, vt,re)]-sum(qv.avaer[(vf, vt,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavaer[(vf, vt,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravaer_b = Constraint(self.vedgexregs.keys(), rule=avdeltaravaer_b)
            # avdeltaravaer = alphar avdeltaravaer (to reduce linearization errors)
            def avdeltaravaer_c(dummy, vf, vt, re):
                return qv.avdeltaravaer[(vf,vt,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravaer_c = Constraint(self.vedgexregs.keys(), rule=avdeltaravaer_c)
            # avae = sum avdeltaravaer
            if self.parts:
                def partve_init(dummy):
                    return ((part,ve[0],ve[1]) for part in self.parts for ve in self.vedges)              
                partve = Set(dimen=3, initialize=partve_init)
                def avaeeqsumavdeltaravaer(dummy, part, vf, vt):
                    return qv.avae[vf,vt] == sum(qv.avdeltaravaer[(vf,vt,re)] for re in self.parts[part].regs)
                qc.avaeeqsumavdeltaravaer = Constraint(partve, rule=avaeeqsumavdeltaravaer)
                # avae = avaer if r is the only region visited of its partition (to improve linearization errors)                
                def avaeleqavaerwu(dummy, vf, vt, re):
                    return qv.avae[vf,vt] <= qv.avaer[(vf,vt,re)] + self.wu*(1-qv.gammar[re])
                qc.avaeleqavaerwu = Constraint(self.vedgexregs.keys(), rule=avaeleqavaerwu)
                def avaegeqavaer2wu(dummy, vf, vt, re):
                    return qv.avae[vf,vt] >= qv.avaer[(vf,vt,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avaegeqavaer2wu = Constraint(self.vedgexregs.keys(), rule=avaegeqavaer2wu)
            """avdm = sum avdeltaravdmr"""
            # Computation of betaavdmr
            def betaavdmr_a(dummy, vf, vt, re, q):
                return qv.betaavdmr[(vf,vt,re,q)] <= qv.beta[(re,q)]*self.wu
            qc.betaavdmr_a = Constraint(self.varcxregxqs.keys(), rule=betaavdmr_a)
            def betaavdmr_b(dummy, vf, vt, re, q):
                return qv.betaavdmr[(vf,vt,re,q)] <= qv.avdmr[(vf,vt,re)]
            qc.betaavdmr_b = Constraint(self.varcxregxqs.keys(), rule=betaavdmr_b)
            def betaavdmr_c(dummy, vf, vt, re, q):
                return qv.betaavdmr[(vf,vt,re,q)] >= qv.avdmr[(vf,vt,re)] - self.wu*(1-qv.beta[(re,q)])
            qc.betaavdmr_c = Constraint(self.varcxregxqs.keys(), rule=betaavdmr_c)
            # Computation of avdeltaravdmr
            def avdeltaravdmr_a(dummy, vf, vt, re):
                q = len(self.ds)-1
                return sum(qv.betaavdmr[(vf,vt,re,j)]*(self.ds[j]-self.ds[j-1]) for j in range(1,q)) <= qv.avdeltaravdmr[(vf,vt,re)]
            qc.avdeltaravdmr_a = Constraint(self.varcxregs.keys(), rule=avdeltaravdmr_a)
            def avdeltaravdmr_b(dummy, vf, vt, re):
                q = len(self.ds)-1
                return qv.avdeltaravdmr[(vf,vt,re)] <= qv.avdmr[(vf,vt,re)]-sum(qv.avdmr[(vf, vt,re)]*(self.ds[j+1]-self.ds[j])-qv.betaavdmr[(vf, vt,re,j)]*(self.ds[j+1]-self.ds[j]) for j in range(1,q))
            qc.avdeltaravdmr_b = Constraint(self.varcxregs.keys(), rule=avdeltaravdmr_b)
            # avdeltaravdmr = alphar avdeltaravdmr (to reduce linearization errors)
            def avdeltaravdmr_c(dummy, vf, vt, re):
                return qv.avdeltaravdmr[(vf,vt,re)] <= qv.alphar[re] * self.wu
            qc.avdeltaravdmr_c = Constraint(self.varcxregs.keys(), rule=avdeltaravdmr_c)
            # avdm = sum avdeltaravdmr
            if self.parts:
                def partva_init(dummy):
                    return ((part,va[0],va[1]) for part in self.parts for va in self.varcs)              
                partva = Set(dimen=3, initialize=partva_init)
                def avdmeqsumavdeltaravdmr(dummy, part, vf, vt):
                    return qv.avdm[vf,vt] == sum(qv.avdeltaravdmr[(vf,vt,re)] for re in self.parts[part].regs)
                qc.avdmeqsumavdeltaravdmr = Constraint(partva, rule=avdmeqsumavdeltaravdmr)
                # avdm = avdmr if r is the only region visited of its partition (to improve linearization errors)                
                def avdmleqavdmrwu(dummy, vf, vt, re):
                    return qv.avdm[vf,vt] <= qv.avdmr[(vf,vt,re)] + self.wu*(1-qv.gammar[re])
                qc.avdmleqavdmrwu = Constraint(self.varcxregs.keys(), rule=avdmleqavdmrwu)
                def avdmgeqavdmr2wu(dummy, vf, vt, re):
                    return qv.avdm[vf,vt] >= qv.avdmr[(vf,vt,re)] - 2*self.wu*(1-qv.gammar[re])
                qc.avdmgeqavdmr2wu = Constraint(self.varcxregs.keys(), rule=avdmgeqavdmr2wu)
        """sum_R_r in V' avdeltar avxr= sum_R_s in W' avdeltas avxs"""
        # Variables to make equal: avdeltaravmr, avdeltaravmupr, avdeltaravmuer, avdeltaravsigmar, avdeltaravatr, avdeltaravaer, avdeltaravdmr
        #                          'avdeltaravdlur', 'avdeltaravdlr', 'avdeltaravlr', 'avdeltaravdsigmar' are not made equal because they do not play role in the constraints            
        # Warning: It is assumed that the above variables are computed, i.e., 'avxeqsumavdeltaravxr' is in listcs
        if 'sumavdeltaravxrVpeqsumavdeltasavxsWp' in listcs:
            if self.regseq:
                # avdeltaravmr
                def plreq_init(dummy):
                    return ((pl,r) for pl in self.places for r in range(len(self.regseq)))              
                plreq = Set(dimen=2, initialize=plreq_init)
                def regseqavdeltaravmr(dummy, pl, r):
                    return sum(qv.avdeltaravmr[(pl,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravmr[(pl,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravmr = Constraint(plreq, rule=regseqavdeltaravmr)
                # avdeltaravmupr       
                def regseqavdeltaravmupr(dummy, pl, r):
                    return sum(qv.avdeltaravmupr[(pl,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravmupr[(pl,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravmupr = Constraint(plreq, rule=regseqavdeltaravmupr)
                def sereq_init(dummy):
                    return ((se[0],se[1],r) for se in self.sedges for r in range(len(self.regseq)))              
                sereq = Set(dimen=3, initialize=sereq_init)
                # avdeltaravmuer       
                def regseqavdeltaravmuer(dummy, sf, st, r):
                    return sum(qv.avdeltaravmuer[(sf,st,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravmuer[(sf,st,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravmuer = Constraint(sereq, rule=regseqavdeltaravmuer)
                # avdeltaravsigmar       
                def regseqavdeltaravsigmar(dummy, tr, r):
                    return sum(qv.avdeltaravsigmar[(tr,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravsigmar[(tr,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravsigmar = Constraint(trreq, rule=regseqavdeltaravsigmar)
                # avdeltaravatr       
                def regseqavdeltaravatr(dummy, tr, r):
                    return sum(qv.avdeltaravatr[(tr,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravatr[(tr,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravatr = Constraint(trreq, rule=regseqavdeltaravatr)
                # avdeltaravaer       
                def vereq_init(dummy):
                    return ((ve[0],ve[1],r) for ve in self.vedges for r in range(len(self.regseq)))              
                vereq = Set(dimen=3, initialize=vereq_init)
                def regseqavdeltaravaer(dummy, vf, vt, r):
                    return sum(qv.avdeltaravaer[(vf,vt,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravaer[(vf,vt,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravaer = Constraint(vereq, rule=regseqavdeltaravaer)
                # avdeltaravdmr       
                def vareq_init(dummy):
                    return ((va[0],va[1],r) for va in self.varcs for r in range(len(self.regseq)))              
                vareq = Set(dimen=3, initialize=vareq_init)
                def regseqavdeltaravdmr(dummy, vf, vt, r):
                    return sum(qv.avdeltaravdmr[(vf,vt,re)] for re in self.regseq[r]['V']) == sum(qv.avdeltaravdmr[(vf,vt,re)] for re in self.regseq[r]['W'])
                qc.regseqavdeltaravdmr = Constraint(vareq, rule=regseqavdeltaravdmr)


        return qc


    def saveres(self, model, vdimdom):
        """Save results from model to net"""
        self.objval = model.obj.expr()        
        for var in vdimdom:
            auxdict = getattr(self, vdimdom[var]['dim'])
            for it in auxdict:
                setattr(auxdict[it], var, getattr(model,var)[it].value)
        
    def printres(self):
        """Print results"""
        if self.options['antype'] in ['tr', 'mpc']: # transient state
            vdimdom = self.vdimdomtr
        elif self.options['antype']  == 'st': # steady state
            vdimdom = self.vdimdomst
        elif self.options['antype']  == 'cst': # constant steady state
            vdimdom = self.vdimdomcst
        elif self.options['antype']  == 'un': # untimed
            vdimdom = self.vdimdomun
        else:
            raise ValueError('Unknown analysis type')
        for var in sorted(vdimdom):
            auxdict = getattr(self, vdimdom[var]['dim'])
            for it in sorted(auxdict):
                print(var,'[',it,']=', getattr(auxdict[it], var), sep='')
        print('Objective:', self.objval)

    def writexls(self, xlsfile):
        """Write results to spreadsheet file xlsfile"""
        wb = self.genxlsdata()
        wb.save(xlsfile)
        
    def genxlsdata(self, wb=None, namesh=None, writeinfo=True, initau=None):
        """Generate data to be stored in a spreadsheet"""
        extvals = ['wl', 'wu', 'W', 'L', 'U']  # Extra values than can be written
        bstyle = xlwt.easyxf('font: bold on')
        wb = xlwt.Workbook() if wb is None else wb
        if self.options['antype'] == 'mpc': # MPC
            ws = wb.add_sheet('MPC' if namesh == None else namesh)
            vdimdom = self.vdimdomtr
        elif self.options['antype'] == 'tr': # transient state
            ws = wb.add_sheet('Transient')
            vdimdom = self.vdimdomtr
        elif self.options['antype']  == 'st': # steady state
            ws = wb.add_sheet('Steady state')
            vdimdom = self.vdimdomst
        elif self.options['antype']  == 'cst': # constant steady state
            ws = wb.add_sheet('Constant steady state')
            vdimdom = self.vdimdomcst
        elif self.options['antype']  == 'un': # untimed
            ws = wb.add_sheet('Untimed')
            vdimdom = self.vdimdomun
        else:
            raise ValueError('Unknown analysis type')
        if self.options['writevars'] == 'all':
            wrvars = {key: 'all' for key in vdimdom}
            for key in extvals:
                wrvars[key] = 'all'
        else:
            wrvars = self.options['writevars']
        """Write variables"""
        ws.write(0, 0, 'Objective:', bstyle)
        ws.write(0, 1, self.objval, bstyle)
        if initau == None:
            if self.options['antype'] in ['tr', 'mpc']:
                ws.write(1, 0, 'theta:', bstyle)
                ws.write(1, 1, self.theta, bstyle)
        else:
            ws.write(1, 0, 'time interval:', bstyle)
            ws.write(1, 1, '['+str(initau)+', '+str(initau+self.theta)+']', bstyle)
        row = 3
        for var in sorted(wrvars):
            if var not in extvals  and var in vdimdom:
                auxdict = getattr(self, vdimdom[var]['dim'])
                for it in sorted(auxdict):
                    if wrvars[var]=='all' or it in wrvars[var]:
                        ws.write(row, 0, str(var)+'['+str(it)+']', bstyle)
                        ws.write(row, 1, getattr(auxdict[it], var))
                        row = row + 1
        if hasattr(self, 'wl') and 'wl' in wrvars:   
            ws.write(row, 0, 'wl', bstyle)
            ws.write(row, 1, self.wl)
            row = row + 1
        if hasattr(self, 'wu') and 'wu' in wrvars:   
            ws.write(row, 0, 'wu', bstyle)
            ws.write(row, 1, self.wu)
            row = row + 1
        if hasattr(self, 'W') and 'W' in wrvars:   
            ws.write(row, 0, 'W', bstyle)
            ws.write(row, 1, self.W)
            row = row + 1
        if 'writeLUnegsa' in self.options and not self.options['writeLUnegsa']:
            auxrows = self.E + self.Ec
            eecrows = sorted([er for er in auxrows if (len(er)==1 and list(er.values()) != [-1]) or len(er)>1], key=lambda d: sorted(d.items())) # Filter components of one element with weight -1
        else:
            eecrows = sorted(self.E + self.Ec, key=lambda d: sorted(d.items()))
        if self.L and 'L' in wrvars and self.U and 'U' in wrvars:   
            for eecrow in eecrows: # For each row of E+Ec
                ws.write(row, 0, 'L['+str(eecrow)+']', bstyle)
                if eecrow in self.E:
                    ws.write(row, 1, self.L[self.E.index(eecrow)])
                else:
                    ws.write(row, 1, self.Fc[self.Ec.index(eecrow)])
                row += 1
                ws.write(row, 0, 'U['+str(eecrow)+']', bstyle)
                if eecrow in self.E:
                    ws.write(row, 1, self.U[self.E.index(eecrow)])
                else:
                    ws.write(row, 1, self.Fc[self.Ec.index(eecrow)])                            
                row += 1
        elif self.L and 'L' in wrvars:   
            for eecrow in eecrows: # For each row of E+Ec
                ws.write(row, 0, 'L['+str(eecrow)+']', bstyle)
                if eecrow in self.E:
                    ws.write(row, 1, self.L[self.E.index(eecrow)])
                else:
                    ws.write(row, 1, self.Fc[self.Ec.index(eecrow)])                            
                row += 1
        elif self.U and 'U' in wrvars: 
            for eecrow in eecrows: # For each row of E+Ec
                ws.write(row, 0, 'U['+str(eecrow)+']', bstyle)
                if eecrow in self.E:
                    ws.write(row, 1, self.U[self.E.index(eecrow)])
                else:
                    ws.write(row, 1, self.Fc[self.Ec.index(eecrow)])                            
                row += 1
                
        """Write performance"""
        if writeinfo:
            wi = wb.add_sheet('Info')
            row = 0
            wi.write(row, 0, 'Problem', bstyle)
            row += 1
            for key,val in sorted(self.info['result']['Problem'][0].items()):
                wi.write(row, 1, key)
                if isinstance(val, dict):
                    val = str(val)
                wi.write(row, 2, val)
                row += 1
            wi.write(row, 0, 'Solver', bstyle)
            row += 1
            for key,val in sorted(self.info['result']['Solver'][0].items()):
                wi.write(row, 1, key)
                if isinstance(val, dict):
                    val = str(val)
                wi.write(row, 2, val)
                row += 1
    
            wi.write(row, 0, 'Performance (seconds)', bstyle)
            row += 1
            for key, val in sorted(self.info['perf'].items()):
                wi.write(row, 1, key)
                wi.write(row, 2, val)
                row += 1

        return wb

    def plotres(self, periods = 'all'):
        print('No time evolution to plot')
