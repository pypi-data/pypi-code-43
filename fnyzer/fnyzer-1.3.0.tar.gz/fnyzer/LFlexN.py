from __future__ import division, print_function
from fnyzer import FlexN
from fnyzer import GFlexN
import pyomo.environ as pyomo
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
import time
import warnings
from copy import deepcopy
import matplotlib.pyplot as plt      
import xlwt
import pickle

class LFlexN:
    """List of Flexible Nets for analysis with intermediate states"""
    qpre = 'q' # Period prefix for variables and constraints
    Qpre = 'Q' # Macro period prefix (a macroperiod covers all consecutive periods with same net)

    """Variable names, dimension and domains for the nets composing LFlexN"""
    vdimdomun = deepcopy(FlexN.vdimdomun)
    vdimdomtr = deepcopy(FlexN.vdimdomtr)
    vdimdomst = deepcopy(FlexN.vdimdomst)
    vdimdomgun = deepcopy(GFlexN.vdimdomun)
    vdimdomgtr = deepcopy(GFlexN.vdimdomtr)
    vdimdomgst = deepcopy(GFlexN.vdimdomst)
    vdimdomgcst = deepcopy(GFlexN.vdimdomcst)

    def __init__(self, netdata):
        """Set default options for non specified options"""
        if 'options' not in netdata:
            netdata['options'] = {}
        self.options = deepcopy(netdata['options'])
        for opt in FlexN.defoptions:
            if opt not in self.options:
                self.options[opt] = FlexN.defoptions[opt]
        if self.options['writexls'] and 'xlsfile' not in self.options:
            self.options['xlsfile']  = netdata['name'] + ".xls"
        if self.options['savenet'] and 'netfile' not in self.options:
            self.options['netfile']  = netdata['name'] + ".pkl"
        """Set general attributes"""
        self.info = {'perf': {}, 'result': {}} # Dictionary to store info about the results and performance of the program
        for key in netdata: # solver, options, extracons and obj are specified in LFlexN, the values of those attributes of each particular net are discarded 
            if key not in ['options']:
                setattr(self, key, netdata[key])
        """Build list of nets"""
        self.qnets = [] # One net per period
        self.Qnets = [] # One net per macroperiod
        qfirst = 0 # Number of first period of macroperiod
        for mapper in self.mappers: # Iterate over macro periods
            mapper['net']['solver'] = self.solver  # Set solver and options for each qnet
            mapper['net']['options'] = deepcopy(self.options)
            qlast = qfirst+len(mapper['thetas'])-1
            mapper['qfirst'], mapper['qlast'] = qfirst, qlast
            qfirst = qlast + 1
            self.Qnets.append(GFlexN(mapper['net']) if 'regs' in mapper['net'] else FlexN(mapper['net']))
            self.Qnets[-1].theta = sum(mapper['thetas'])
            if 'outinm' in mapper: # Not first net, update link marking of previous net to current one
                self.qnets[-1].outinm = mapper['outinm']
                self.qnets[-1].outina = mapper['outina']
            for theta in mapper['thetas']:
                self.qnets.append(GFlexN(mapper['net']) if 'regs' in mapper['net'] else FlexN(mapper['net']))
                self.qnets[-1].theta = theta
                self.qnets[-1].outinm = 'eq' # 'eq' means previous final marking equal to next initial marking
                self.qnets[-1].outina = 'eq' # 'eq' means previous final aT equal to next a0
        delattr(self.qnets[-1], 'outinm')
        delattr(self.qnets[-1], 'outina')
        """Initial and final time of each qnet and Qnet"""
        self.qnets[0].tau0 = 0
        self.qnets[0].tauf = self.qnets[0].theta
        for idx, qnet in enumerate(self.qnets[1:], 1):
            qnet.tau0 = self.qnets[idx-1].tauf
            qnet.tauf = qnet.tau0+qnet.theta
        self.Qnets[0].tau0 = 0
        self.Qnets[0].tauf = sum(self.mappers[0]['thetas'])
        for IDX, Qnet in enumerate(self.Qnets[1:], 1):
            Qnet.tau0 = self.Qnets[IDX-1].tauf
            Qnet.tauf = Qnet.tau0+sum(self.mappers[IDX]['thetas'])
            
        if len(self.qnets) < 2:
            raise ValueError('List of nets must have at least two elements. Use FlexNtr for single nets.')


    def buildmodel(self, listcsfol, glistcsfol, vdimdom, horizon=-1, compQ=False, obj={}, extracons=[]):
        """Build mathematical model from a list of constraints listcsfol, 
           a list of extra constraints extracons and a dictionary with an objective function obj.
           listcsfol is a dictionary with three keys 'first', 'last', 'other'
           storing the list of constraints for the first, the last and other(neither first nor last) period of unguarded nets.
           glistcsfol is similar to listcfol but applies to guarded nets
           vdimdom is a list of at least horizon elements containing dictionaries with dimension and domain of variables
           horizon is the number of periods to be considered
           Varables for macro periods are included if compQ"""
        if horizon == -1:
            horizon = len(self.qnets)
        model = pyomo.ConcreteModel()
        class Cqv: # Class with attributes linked to variables of current period
            pass
        """Iterate over periods"""
        for idx in range(horizon): # idx is the index of the net of the current period (period indices start at 0) 
            preq = LFlexN.qpre+str(idx)+'_' # prefix for variables
            qnet = self.qnets[idx]  # net of current period
            """Create variables"""
            qv = Cqv()
            for var in vdimdom[idx]:
                auxdict = getattr(qnet, vdimdom[idx][var]['dim'])
                setattr(model, preq+var, pyomo.Var(auxdict.keys(), within=vdimdom[idx][var]['dom']))
                setattr(qv, var, getattr(model, preq+var))# Create object qv linking attributes to variables of current period
            """Create constraints"""
            if idx == 0: # Constraints for first period
                qc = qnet.createcons(qv=qv, listcs=glistcsfol['first'] if hasattr(qnet,'regs') else listcsfol['first'])
            elif idx == horizon-1: # Constraints for last period
                qc = qnet.createcons(qv=qv, listcs=glistcsfol['last'] if hasattr(qnet,'regs') else listcsfol['last'])
            else: # Constraints for intermediate periods
                qc = qnet.createcons(qv=qv, listcs=glistcsfol['other'] if hasattr(qnet,'regs') else listcsfol['other'])
            """Add constraints of current period to the model"""
            for con in vars(qc).keys(): # Copy constraints of current period to model
                setattr(model, preq+con, getattr(qc, con))
        """Link final markings and actions of one period to initial markings and actions of next period"""
        for idx in range(horizon-1):
            qnet = self.qnets[idx]  # net of current period
            preq = LFlexN.qpre+str(idx)+'_' # prefix of current period
            nextpreq = LFlexN.qpre+str(idx+1)+'_' # prefix of next period
            if self.qnets[idx].outinm == 'eq':
                def OutInmeq(model, p):
                    return getattr(model, preq+'m')[p] == getattr(model, nextpreq+'m0')[p]
                setattr(model, preq+'outinmeq', pyomo.Constraint(qnet.places.keys(), rule=OutInmeq))
            else:
                def OutInm(model, r):
                    return eval(qnet.outinm[r], {'m':getattr(model,preq+'m'), 'm0':getattr(model,nextpreq+'m0')})
                setattr(model, preq+'outinm', pyomo.Constraint(range(len(qnet.outinm)), rule=OutInm))
            if self.qnets[idx].outina == 'eq':
                def OutInaeq(model, t):
                    return getattr(model, preq+'at')[t] == getattr(model, nextpreq+'a0')[t]
                setattr(model, preq+'outinaeq', pyomo.Constraint(qnet.trans.keys(), rule=OutInaeq))
            else:
                def OutIna(model, r):
                    return eval(qnet.outina[r], {'at':getattr(model,preq+'at'), 'a0':getattr(model,nextpreq+'a0')})
                setattr(model, preq+'outina', pyomo.Constraint(range(len(qnet.outina)), rule=OutIna))
        """Create variables and equalities for values of macro periods"""
        if compQ:
            for IDX, mapper in enumerate(self.mappers):
                qfirst, qlast = mapper['qfirst'], mapper['qlast']
                vdido = vdimdom[qlast]
                if  vdido == LFlexN.vdimdomtr or vdido == LFlexN.vdimdomgtr: # Compute variables of macro period only if its last period is transient
                    preQ = LFlexN.Qpre+str(IDX)+'_' # prefix for variables
                    preQC = LFlexN.Qpre+str(IDX)+'C_' # prefix for constraints
                    Qnet = self.Qnets[IDX]  # Qnet of current macro period
                    for var in vdido:
                        auxdict = getattr(Qnet, vdido[var]['dim'])
                        setattr(model, preQ+var, pyomo.Var(auxdict.keys(), within=vdido[var]['dom']))
                        if vdido[var]['Qtype'] == 'ini': # Initial value at the beginning of macro period
                            def IniQ(model, it):
                                return getattr(model, preQ+var)[eval(it)] == getattr(model, LFlexN.qpre+str(qfirst)+'_'+var)[eval(it)]
                            setattr(model, preQC+var, pyomo.Constraint([repr(it) for it in auxdict], rule=IniQ))
                        elif vdido[var]['Qtype'] == 'fin': # Final value at the end of macro period
                            def FinalQ(model, it):
                                return getattr(model, preQ+var)[eval(it)] == getattr(model, LFlexN.qpre+str(qlast)+'_'+var)[eval(it)]
                            setattr(model, preQC+var, pyomo.Constraint([repr(it) for it in auxdict], rule=FinalQ))
                        elif vdido[var]['Qtype'] == 'add': # Sum over macro period
                            def SumQ(model, it):
                                thesum = sum(getattr(model,LFlexN.qpre+str(i)+'_'+var)[eval(it)] for i in range(qfirst, qlast+1))
                                return getattr(model, preQ+var)[eval(it)] == thesum
                            setattr(model, preQC+var, pyomo.Constraint([repr(it) for it in auxdict], rule=SumQ))
                        elif vdido[var]['Qtype'] == 'av': # Average over macro period
                            def AverQ(model, it):
                                theav = sum(mapper['thetas'][i-qfirst]*getattr(model,LFlexN.qpre+str(i)+'_'+var)[eval(it)] for i in range(qfirst, qlast+1))/sum(mapper['thetas'])
                                return getattr(model, preQ+var)[eval(it)] == theav
                            setattr(model, preQC+var, pyomo.Constraint([repr(it) for it in auxdict], rule=AverQ))
                else:
                    print('Variables of macro-period', IDX, 'not computed (last period is not transient)')                            
        """Create extra constraints"""    
        if extracons:
            model.ConExtra = self.qnets[0].createextrac(model, extracons) # Extra constraints
        """Create objective function"""    
        if obj:
            model.obj = self.qnets[0].createobj(model, obj)
        return model

    def computetdepF(self):
        """Compute time dependent F for all qnets.
        Compute components of F that are initialized to -inf.
        Assumptions:
         - The corresponding components of E have one and only one nonnull component
         - The guards of each nonnull components form a partition"""
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
        listcsfol = {'first': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                               'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                               'EcdsigmaeqthetaFc', 
                               'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                               'Jll0leqKl'],
                     'other': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                               'meqm0Zmdm',
                               'EcdsigmaeqthetaFc', 
                               'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                               'Jll0leqKl'],
                     'last': ['meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'mbounds', # Constraints for unguarded intensity arcs
                              'sigmaa0eqatYsae', 'AdmleqBae', 
                              'meqm0Zmdm',
                              'EcdsigmaeqthetaFc',
                              'EudsigmaleqthetaFu',                      
                              'EladsigmaleqthetaFla',
                              'Emadsigmaeq0', 
                              'sigmaeql0thetaZldsigma', 'Jll0leqKl',
                              'forceactf']}
        glistcsfol = deepcopy(listcsfol)
        glistcsfol['last'] = ['meqmupYmmue', 'CdluleqDmue', 'leql0Zldl', 'mbounds',  # Constraints for guarded intensity arcs
                              'dleeqdluer', 
                              'sigmaa0eqatYsae', 'AdmleqBae', 
                              'meqm0Zmdm',
                              'EcdsigmaeqthetaFc',
                              'EudsigmaleqthetaFu',                      
                              'EladsigmaleqthetaFla',
                              'Emadsigmaeq0', 
                              'sigmaeql0thetaZldsigma', 'Jll0leqKl',
                              'SrxleqQr',
                              'forceactf']
        self.qnets[0].computetdepF() # Compute F for first net
        vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets))]
        numqnets = len(self.qnets) if self.options['antype'] in ['tr','mpc'] else len(self.qnets)-1
        for j in range(1, numqnets): # Compute F for rest of nets
            qnet = self.qnets[j]
            pref = LFlexN.qpre+str(j)+'_'
            if qnet.E:
                qnet.rowsu = [index for index, value in enumerate(qnet.F) if value > float('-inf')]  # rows of matrix E^u
                qnet.rowsa = list(set(range(len(qnet.F))) - set(qnet.rowsu))  # rows of matrix E^a
                Ha = deepcopy(qnet.F)
                it = 0
                dif = qnet.options['epsiloncompF']+1
                while it<qnet.options['maxitcompF'] and dif>qnet.options['epsiloncompF']:
                    it = it + 1
                    Fpri = deepcopy(qnet.F)
                    for k in qnet.rowsa:
                        guards = qnet.sarcs[list(qnet.E[k].keys())[0]].phi
                        if guards: # intensity arcs of row k are guarded
                            currentmax = qnet.F[k]
                            for reg in guards:
                                qnet.curreg = reg
                                Fmodel = self.buildmodel(listcsfol, glistcsfol, vdimdom, horizon=j+1)
                                Fmodel.name = 'Fmodel_Timed_States'
                                opt = SolverFactory(self.solver)
                                Fmodel.obj = pyomo.Objective(expr=sum(qnet.E[k][sa]*getattr(Fmodel, pref+'dl')[sa] for sa in qnet.E[k]), 
                                                              sense=pyomo.maximize)
                                results = opt.solve(Fmodel)
                                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                    currentmax = max([currentmax, Fmodel.obj.expr()])
                                else:
                                    pass # The problem will be infeasible for 
                                         # unreachable regions,so, no warning here
                                         # and the pyomo warning can be ignored.
                                         # Remark: termination_conditions of gurobi
                                         # and cplex can be inconsistent (for the
                                         # same problem one can be unbounded and
                                         # the other infeasible).
                            Ha[k] = currentmax                            
                            del qnet.curreg
                        else: # intensity arcs of row k are not guarded
                            Fmodel = self.buildmodel(listcsfol, glistcsfol, vdimdom, horizon=j+1)
                            Fmodel.name = 'Fmodel_Timed_States'
                            opt = SolverFactory(self.solver)
                            Fmodel.obj = pyomo.Objective(expr=sum(qnet.E[k][sa]*getattr(Fmodel, pref+'dl')[sa] for sa in qnet.E[k]), 
                                                      sense=pyomo.maximize)
                            results = opt.solve(Fmodel)
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                Ha[k] = max([qnet.F[k], Fmodel.obj.expr()])
                            else:
                                warnings.warn("Infeasible or unbounded problem "
                                    "while computing F["+str(qnet.E[k])+"]")
                    qnet.F = Ha                                
                    dif = max([compdif(f,fp) for f,fp in zip(qnet.F, Fpri)])
                if it >= qnet.options['maxitcompF']:
                    warnings.warn("Maximum number of iterations reached while computing F (F might not be upperbound for E")


    def computetrwl(self):
        """Compute auxiliary bound wl for transient state.
           wl is set to '-inf' if the problem is unbounded"""
        if len(self.mappers) == 1: # If all qnets are the same
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wl'): # If the net is guarded
                tmptheta = self.qnets[0].theta
                self.qnets[0].theta = self.Qnets[0].tauf
                self.qnets[0].computetrwl()
                self.qnets[0].theta = tmptheta
                for qnet in self.qnets:
                    qnet.wl = self.qnets[0].wl
        else:
            glistcsfol = {'first': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'other': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'last':  ['meqmupYmmue', 'CdluleqDmue', 'mbounds',
                                    'sigmaa0eqatYsae', 'AdmleqBae', 
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma',
                                    'Jll0leqKl']}
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wl'):
                self.qnets[0].computetrwl() # Compute wl for first net
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') and not hasattr(self.qnets[i], 'wl') else LFlexN.vdimdomtr for i in range(len(self.qnets))]
            for j in range(1, len(self.qnets)): 
                qnet = self.qnets[j]
                pref = LFlexN.qpre+str(j)+'_'
                if hasattr(qnet,'regs') and not hasattr(qnet, 'wl'):  # Compute wl for periods with guarded nets
                    wlmodel = self.buildmodel(glistcsfol, glistcsfol, vdimdom, horizon=j+1)
                    opt = SolverFactory(self.solver)    
                    auxwl = -1 # Force wl to be at most -1
                    for sag in qnet.sarcxguards:
                        if auxwl > -float('inf'):
                            wlmodel.obj = pyomo.Objective(expr=getattr(wlmodel, pref+'dlu')[sag], sense=pyomo.minimize)
                            results = opt.solve(wlmodel)
                            # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                auxwl = min(auxwl, wlmodel.obj.expr())                
                            else:
                                auxwl = -float('inf')
                                warnings.warn("Warning: wl set to -inf")
                            wlmodel.del_component('obj')
                    qnet.wl = qnet.options['scalebs']*auxwl
                    
    def computetrwu(self):
        """Compute auxiliary bound wu for transient state.
           wu is set to 'inf' if the problem is unbounded"""
        if len(self.mappers) == 1: # If all qnets are the same
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wu'): # If the net is guarded
                tmptheta = self.qnets[0].theta
                self.qnets[0].theta = self.Qnets[0].tauf
                self.qnets[0].computetrwu()
                self.qnets[0].theta = tmptheta
                for qnet in self.qnets:
                    qnet.wu = self.qnets[0].wu
        else:
            glistcsfol = {'first': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'other': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'last':  ['meqmupYmmue', 'CdluleqDmue', 'mbounds',
                                    'sigmaa0eqatYsae', 'AdmleqBae', 
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma',
                                    'Jll0leqKl']}
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wu'):
                self.qnets[0].computetrwu() # Compute wu for first net
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') and not hasattr(self.qnets[i], 'wu') else LFlexN.vdimdomtr for i in range(len(self.qnets))]
            for j in range(1, len(self.qnets)): 
                qnet = self.qnets[j]
                pref = LFlexN.qpre+str(j)+'_'
                if hasattr(qnet,'regs') and not hasattr(qnet, 'wu'):  # Compute wu for periods with guarded nets
                    wumodel = self.buildmodel(glistcsfol, glistcsfol, vdimdom, horizon=j+1)
                    opt = SolverFactory(self.solver)    
                    auxwu = 1 # Force wu to be at least 1
                    for sag in qnet.sarcxguards:
                        if auxwu < float('inf'):
                            wumodel.obj = pyomo.Objective(expr=getattr(wumodel, pref+'dlu')[sag]+
                                                   sum(getattr(wumodel, pref+'m')[pl] for pl in qnet.places)+
                                                   sum(getattr(wumodel, pref+'dsigma')[sa] for sa in qnet.sarcs)+
                                                   sum(getattr(wumodel, pref+'sigma')[tr] for tr in qnet.trans)+
                                                   sum(getattr(wumodel, pref+'dm')[va] for va in qnet.varcs), sense=pyomo.maximize)
                            results = opt.solve(wumodel)
                            # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                auxwu = max(auxwu, wumodel.obj.expr())                
                            else:
                                auxwu = float('inf')
                                warnings.warn("Warning: wu set to inf "
                                    "Have you included intensity arcs in E?")
                            wumodel.del_component('obj')
                    qnet.wu = qnet.options['scalebs']*auxwu

    def computetindwl(self):
        """Compute auxiliary bound wl considering the last period as untimed. 
           wl is set to '-inf' if the problem is unbounded"""
        if len(self.mappers) == 1: # If all qnets are the same
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wl'):
                self.qnets[0].computetindwl()
                for qnet in self.qnets:
                    qnet.wl = self.qnets[0].wl
        else:
            glistcsfolA = {'first': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'other': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'last':  ['meqmupYmmue', 'CdluleqDmue', 'mbounds',
                                    'sigmaa0eqatYsae', 'AdmleqBae', 
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma',
                                    'Jll0leqKl']}
            glistcsfolB = deepcopy(glistcsfolA)
            glistcsfolB['last'] =  ['meqmupYmmue', 'CdluleqDmue', 'mbounds',
                                    'sigmaa0eqatYsae', 'AdmleqBae', 
                                    'meqm0Zmdm']
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wl'):
                self.qnets[0].computetrwl() # Compute wl for first net
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') and not hasattr(self.qnets[i], 'wl') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgun if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomun)
            for j in range(1, len(self.qnets)): 
                qnet = self.qnets[j]
                pref = LFlexN.qpre+str(j)+'_'
                if hasattr(qnet,'regs') and not hasattr(qnet, 'wl'):  # Compute wl for periods with guarded nets
                    opt = SolverFactory(self.solver)
                    if j< len(self.qnets)-1:
                        wlmodel = self.buildmodel(glistcsfolA, glistcsfolA, vdimdom, horizon=j+1)
                    else:
                        wlmodel = self.buildmodel(glistcsfolB, glistcsfolB, vdimdom, horizon=j+1)
                    auxwl = -1 # Force wl to be at most -1
                    opt = SolverFactory(self.solver)    
                    for sag in qnet.sarcxguards:
                        if auxwl > -float('inf'):
                            wlmodel.obj = pyomo.Objective(expr=getattr(wlmodel, pref+'dlu')[sag], sense=pyomo.minimize)
                            results = opt.solve(wlmodel)
                            # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                auxwl = min(auxwl, wlmodel.obj.expr())                
                            else:
                                auxwl = -float('inf')
                                warnings.warn("Warning: wl set to -inf")
                            wlmodel.del_component('obj')
                    qnet.wl = qnet.options['scalebs']*auxwl

    def computetindwu(self):
        """Compute auxiliary bound wu considering the last period as untimed. 
           wu is set to 'inf' if the problem is unbounded"""
        if len(self.mappers) == 1: # If all qnets are the same
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wu'):
                self.qnets[0].computetindwu()
                for qnet in self.qnets:
                    qnet.wu = self.qnets[0].wu
        else:
            glistcsfolA = {'first': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'other': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'last':  ['meqmupYmmue', 'CdluleqDmue', 'mbounds',
                                    'sigmaa0eqatYsae', 'AdmleqBae', 
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma',
                                    'Jll0leqKl']}
            glistcsfolB = deepcopy(glistcsfolA)
            glistcsfolB['last'] =  ['meqmupYmmue', 'CdluleqDmue', 'mbounds',
                                    'sigmaa0eqatYsae', 'AdmleqBae', 
                                    'meqm0Zmdm']
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wu'):
                self.qnets[0].computetrwu() # Compute wu for first net
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') and not hasattr(self.qnets[i], 'wu') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgun if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomun)
            for j in range(1, len(self.qnets)): 
                qnet = self.qnets[j]
                pref = LFlexN.qpre+str(j)+'_'
                if hasattr(qnet,'regs') and not hasattr(qnet, 'wu'):  # Compute wu for periods with guarded nets
                    opt = SolverFactory(self.solver)
                    if j< len(self.qnets)-1:
                        wumodel = self.buildmodel(glistcsfolA, glistcsfolA, vdimdom, horizon=j+1)
                        auxwu = 1 # Force wu to be at least 1
                        opt = SolverFactory(self.solver)    
                        for sag in qnet.sarcxguards:
                            if auxwu < float('inf'):
                                wumodel.obj = pyomo.Objective(expr=getattr(wumodel, pref+'dlu')[sag]+
                                                       sum(getattr(wumodel, pref+'m')[pl] for pl in qnet.places)+
                                                       sum(getattr(wumodel, pref+'dsigma')[sa] for sa in qnet.sarcs)+
                                                       sum(getattr(wumodel, pref+'sigma')[tr] for tr in qnet.trans)+
                                                       sum(getattr(wumodel, pref+'dm')[va] for va in qnet.varcs), sense=pyomo.maximize)
                                results = opt.solve(wumodel)
                                # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                    auxwu = max(auxwu, wumodel.obj.expr())                
                                else:
                                    auxwu = float('inf')
                                    warnings.warn("Warning: wu set to inf")
                                wumodel.del_component('obj')
                        qnet.wu = qnet.options['scalebs']*auxwu
                    else:
                        wumodel = self.buildmodel(glistcsfolB, glistcsfolB, vdimdom, horizon=j+1)
                        auxwu = 1 # Force wu to be at least 1
                        opt = SolverFactory(self.solver)    
                        for sag in qnet.sarcxguards:
                            if auxwu < float('inf'):
                                wumodel.obj = pyomo.Objective(expr=getattr(wumodel, pref+'dlu')[sag], sense=pyomo.maximize)
                                results = opt.solve(wumodel)
                                # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                    auxwu = max(auxwu, wumodel.obj.expr())                
                                else:
                                    auxwu = float('inf')
                                    warnings.warn("Warning: wu set to inf")
                                wumodel.del_component('obj')
                        qnet.wu = qnet.options['scalebs']*auxwu


    def computestwl(self):
        """Compute auxiliary bound wl considering the last period as steady state. 
           wl is set to '-inf' if the problem is unbounded"""
        self.computetindwl()

    def computestwu(self):
        """Compute auxiliary bound wu considering the last period as steady state. 
           wu is set to 'inf' if the problem is unbounded"""
        self.computetindwu() # Required for constraint 'avdleleqwutind'
        wutind = self.qnets[-1].wu # To be used in the last period
        glistcsfolA = {'first': ['sigmaa0eqatYsae', 'AdmleqBae', 'avmbounds',
                                'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                                'EcdsigmaeqthetaFc', 
                                'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                'Jll0leqKl'],
                      'other': ['sigmaa0eqatYsae', 'AdmleqBae', 'avmbounds',
                                'meqm0Zmdm',
                                'EcdsigmaeqthetaFc', 
                                'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                'Jll0leqKl'],
                      'last':  ['meqmupYmmue', 'CdluleqDmue', 'avmbounds',
                                'sigmaa0eqatYsae', 'AdmleqBae', 
                                'meqm0Zmdm',
                                'EcdsigmaeqthetaFc', 
                                'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma',
                                'Jll0leqKl']}
        glistcsfolB = deepcopy(glistcsfolA)
        glistcsfolB['last'] =  ['avmeqavmupYmavmue', 'CavdluleqDavmue', 'avleql0Zlavdl', 'Jll0leqKl', 'avmbounds',
                                'avdleleqwutind',
                                'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau',
                                'sigmaa0eqatYsae', 'AdmleqBae', 'avmeqm0Zmdm']
        if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'wu'):
            self.qnets[0].computetrwu() # Compute wu for first net
        vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') and not hasattr(self.qnets[i], 'wu') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
        vdimdom.append(LFlexN.vdimdomgst if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomst)
        for j in range(1, len(self.qnets)): 
            qnet = self.qnets[j]
            pref = LFlexN.qpre+str(j)+'_'
            if hasattr(qnet,'regs') and not hasattr(qnet, 'wu'):  # Compute wu for periods with guarded nets
                opt = SolverFactory(self.solver)
                if j< len(self.qnets)-1:
                    wumodel = self.buildmodel(glistcsfolA, glistcsfolA, vdimdom, horizon=j+1)
                    auxwu = 1 # Force wu to be at least 1
                    opt = SolverFactory(self.solver)    
                    for sag in qnet.sarcxguards:
                        if auxwu < float('inf'):
                            wumodel.obj = pyomo.Objective(expr=getattr(wumodel, pref+'dlu')[sag]+
                                                   sum(getattr(wumodel, pref+'m')[pl] for pl in qnet.places)+
                                                   sum(getattr(wumodel, pref+'dsigma')[sa] for sa in qnet.sarcs)+
                                                   sum(getattr(wumodel, pref+'sigma')[tr] for tr in qnet.trans)+
                                                   sum(getattr(wumodel, pref+'dm')[va] for va in qnet.varcs), sense=pyomo.maximize)
                            results = opt.solve(wumodel)
                            # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                            if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                                auxwu = max(auxwu, wumodel.obj.expr())                
                            else:
                                auxwu = float('inf')
                                warnings.warn("Warning: wu set to inf")
                            wumodel.del_component('obj')
                    qnet.wu = qnet.options['scalebs']*auxwu
                else:
                    wumodel = self.buildmodel(glistcsfolB, glistcsfolB, vdimdom, horizon=j+1)
                    opt = SolverFactory(self.solver)    
                    wumodel.obj = pyomo.Objective(expr=sum(getattr(wumodel, pref+'avm')[pl] for pl in qnet.places)+
                                                   sum(getattr(wumodel, pref+'avl')[tr] for tr in qnet.trans)+
                                                   sum(getattr(wumodel, pref+'avdmtau')[va] for va in qnet.varcs), 
                                                   sense=pyomo.maximize)
                    results = opt.solve(wumodel)
                    # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        qnet.wu = wutind+qnet.options['scalebs']*(wumodel.obj.expr())
                    else:
                        qnet.wu = float('inf')
                        warnings.warn("Warning: wu set to inf")
                    

    def computetrW(self, upto = -1):
        """Compute auxiliary bound W for transient state.
           W is set to 'inf' if the problem is unbounded"""
        if upto == -1: # Default is compute W for all qnets 
            upto = len(self.qnets)
        glistcsfol = {'first': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                                'EcdsigmaeqthetaFc', 
                                'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                'Jll0leqKl'],
                      'other': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                'meqm0Zmdm',
                                'EcdsigmaeqthetaFc', 
                                'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                'Jll0leqKl'],
                      'last':  ['meqmupYmmue', 
                                'sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                'meqm0Zmdm',
                                'EcdsigmaeqthetaFc', 
                                'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma',
                                'Jll0leqKl']}
        if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'W'):
            self.qnets[0].computetrW() # Compute W for first net
        vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') and not hasattr(self.qnets[i], 'W') else LFlexN.vdimdomtr for i in range(upto)]
        for j in range(1, upto): 
            qnet = self.qnets[j]
            pref = LFlexN.qpre+str(j)+'_'
            if hasattr(qnet,'regs') and not hasattr(qnet, 'W'):  # Compute W for periods with guarded nets
                Wmodel = self.buildmodel(glistcsfol, glistcsfol, vdimdom, horizon=j+1)
                opt = SolverFactory(self.solver)
                obj = 0
                for re in qnet.regs:
                    for sqr in qnet.regs[re].SQrows:
                        abssqr = sqr.replace('-','+').replace('<=','+').replace('>=','+')
                        dicvars = {var.name.lstrip(pref):getattr(Wmodel,var.name) for var in Wmodel.component_objects(pyomo.Var) if var.name.startswith(pref)}
                        obj = obj+eval(abssqr, dicvars)
                Wmodel.obj = pyomo.Objective(expr=obj, sense=pyomo.maximize)
                results = opt.solve(Wmodel)
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    qnet.W = qnet.options['scalebs']*Wmodel.obj.expr()
                else:
                    qnet.W = float('inf')
                    warnings.warn("Warning: W set to inf")

    def computetindW(self):
        """Compute auxiliary bound W considering last period as untimed.
           W is set to 'inf' if the problem is unbounded"""
        if len(self.mappers) == 1: # If all qnets are the same
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'W'): # If the net is guarded
                self.qnets[0].computetindW()
                for qnet in self.qnets:
                    qnet.W = self.qnets[0].W
        else:
            glistcsfolA = {'first': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'other': ['sigmaa0eqatYsae', 'AdmleqBae', 'mbounds',
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 
                                    'Jll0leqKl'],
                          'last':  ['meqmupYmmue', 'mbounds',
                                    'sigmaa0eqatYsae', 'AdmleqBae', 
                                    'meqm0Zmdm',
                                    'EcdsigmaeqthetaFc', 
                                    'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma',
                                    'Jll0leqKl']}
            glistcsfolB = deepcopy(glistcsfolA)
            glistcsfolB['last'] =  ['meqmupYmmue', 'mbounds',
                                    'sigmaa0eqatYsae', 'AdmleqBae', 
                                    'meqm0Zmdm']
            if hasattr(self.qnets[0],'regs') and not hasattr(self.qnets[0], 'W'):
                self.qnets[0].computetrW() # Compute W for first net
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') and not hasattr(self.qnets[i], 'W') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgun if hasattr(self.qnets[-1],'regs') and not hasattr(self.qnets[-1], 'W') else LFlexN.vdimdomun)
            for j in range(1, len(self.qnets)): 
                qnet = self.qnets[j]
                pref = LFlexN.qpre+str(j)+'_'
                opt = SolverFactory(self.solver)
                if hasattr(qnet,'regs') and not hasattr(qnet, 'W'):  # Compute W for periods with guarded nets
                    if j< len(self.qnets)-1:
                        Wmodel = self.buildmodel(glistcsfolA, glistcsfolA, vdimdom, horizon=j+1)
                    else:
                        Wmodel = self.buildmodel(glistcsfolB, glistcsfolB, vdimdom, horizon=j+1)
                    obj = 0
                    for re in qnet.regs:
                        for sqr in qnet.regs[re].SQrows:
                            abssqr = sqr.replace('-','+').replace('<=','+').replace('>=','+')
                            dicvars = {var.name.lstrip(pref):getattr(Wmodel,var.name) for var in Wmodel.component_objects(pyomo.Var) if var.name.startswith(pref)}
                            obj = obj+eval(abssqr, dicvars)
                    Wmodel.obj = pyomo.Objective(expr=obj, sense=pyomo.maximize)
                    results = opt.solve(Wmodel)
                    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                        qnet.W = qnet.options['scalebs']*Wmodel.obj.expr()
                    else:
                        qnet.W = float('inf')
                        warnings.warn("Warning: W set to inf")

    def computestW(self):
        """Compute auxiliary bound W considering last period as steady state.
           W is set to 'inf' if the problem is unbounded"""
        self.computetindW()

    def computeLU(self):
        """Compute matrices L and U from E and F"""
        connets = self.qnets if self.options['antype'] in ['tr','mpc'] else self.qnets[0:-1]
        for qnet in connets:
            qnet.computeLU()

    def optimst(self):
        """Optimize objective function objf for transient constraints TCN and last period as steady state"""
        ttic, tic = time.time(), time.clock()
        self.computetdepF()
        self.computeLU()
        self.info['perf']['Python processor time[L,U]'], self.info['perf']['Wall time[L,U]'] = time.clock()-tic, time.time()-ttic
        ttic, tic = time.time(), time.clock()
        self.computestwl()
        self.computestwu()
        self.computestW()
        self.info['perf']['Python processor time[wl,wu,W]'], self.info['perf']['Wall time[wl,wu,W]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        other =  ['forceactf', 'forceactav', 'forceexef', 'forceexeav', 'mbounds', 'avmbounds',
                  'meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'avmeqavmupYmavmue', 'CavdlleqDavmue', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma']
        first =  ['Jaa0leqKa', 'Jmm0leqKm'] + other
        last =   ['forceactav', 'forceexeav', 'JpmavmleqKpm', 'avmbounds',
                  'avmeqavmupYmavmue', 'CavdlleqDavmue', 'avleql0Zlavdl', 'Jll0leqKl',
                  'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau',
                  'Zmavdmtaueq0',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'avmeqm0Zmdm',
                  'EcavdleqFc', 'EavdlleqF']
        listcsfol = {'first': first, 'other': other, 'last': last}
        gother = [
                  'forceactf', 'forceactav', 'forceexef', 'forceexeav', 'mbounds', 'avmbounds',
                  'meqmupYmmue', 'CdluleqDmue', 'dleqdeltadlu', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'avmeqavmupYmavmue', 'CavdluleqDavmue', 'avdleqavdeltaavdlg', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma',
                  'SrxleqQrW1deltar', 'SravxrleqQrW1alphar',
                  'avmreqavmuprYmavmuer', 'CavdlurleqDavmuer', 'avlreql0Zlavdlr',
                  'avsigmara0eqavatrYsigmaavaer', 'AavdmrleqBavaer', 'avmreqm0Zmavdmr',
                  'epsavdeltarleq21alphar', 'epsavdeltargeq2alphar',
                  'alpharavaerleqae', 'alpharavdmrleqdm', 'alpharavdsigmarleqdsigma', 'alpharavsigmarleqsigma',
                  'avdlgereqalpharavdlurer', 'avdlreeqalpharavdlurer',
                  'sumdeltareq1', 'sumavdeltareq1', 'avxeqsumavdeltaravxr',
                  'sumavdeltarVleqsumavdeltasW',
                  'sumavdeltarVpeqsumavdeltasWp', 'sumavdeltaravxrVpeqsumavdeltasavxsWp'
                  ]
        gfirst = ['Jaa0leqKa', 'Jmm0leqKm'] + gother        
        glast =  [
                  'forceactav', 'forceexeav', 'JpmavmleqKpm', 'avmbounds',
                  'avmeqavmupYmavmue', 'CavdluleqDavmue', 'avdleqavdeltaavdlg', 'avleql0Zlavdl', 'Jll0leqKl',
                  'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau',
                  'Zmavdmtaueq0',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'avmeqm0Zmdm',
                  'EcavdleqFc', 'EavdlleqF',
                  'SravzrleqQrW1alphar',
                  'avmreqavmuprYmavmuer', 'CavdlurleqDavmuer', 'avlreql0Zlavdlr',
                  'avsigmataureqavattaurYsigmaavaetaur', 'AavdmtaurleqBavaetaur',
                  'sigmara0eqatrYsigmaaer', 'AdmrleqBaer', 'avmreqm0Zmdmr',
                  'epsavdeltarleq21alphar', 'epsavdeltargeq2alphar',                  
                  'avdlgereqalpharavdlurer', 'avdlreeqalpharavdlurer',
                  'sumavdeltareq1', 'avzeqsumavdeltaravzr',
                  'sumavdeltarVleqsumavdeltasW',
                  'sumavdeltarVpeqsumavdeltasWp', 'sumavdeltaravzrVpeqsumavdeltasavzsWp'
                  ]
        glistcsfol = {'first': gfirst, 'other': gother, 'last': glast}
        vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
        vdimdom.append(LFlexN.vdimdomgst if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomst)
        LTCNmodel = self.buildmodel(listcsfol, glistcsfol, vdimdom, compQ = True, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(LTCNmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(LTCNmodel, vdimdom)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return LTCNmodel
        else:
            raise ValueError('LTCNmodel unbounded or infeasible')

    def optimcst(self):
        """Optimize objective function objf for transient constraints TCN and last period as constant steady state"""
        ttic, tic = time.time(), time.clock()
        self.computetdepF()
        self.computeLU()
        self.info['perf']['Python processor time[L,U]'], self.info['perf']['Wall time[L,U]'] = time.clock()-tic, time.time()-ttic
        ttic, tic = time.time(), time.clock()
        self.computestwl()
        self.computestwu()
        self.computestW()
        self.info['perf']['Python processor time[wl,wu,W]'], self.info['perf']['Wall time[wl,wu,W]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        # Constraints for unguarded nets
        other =  ['forceactf', 'forceactav', 'forceexef', 'forceexeav', 'mbounds', 'avmbounds',
                  'meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'avmeqavmupYmavmue', 'CavdlleqDavmue', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma']
        first =  ['Jaa0leqKa', 'Jmm0leqKm'] + other
        last =   ['forceactav', 'forceexeav', 'JpmavmleqKpm', 'avmbounds',
                  'avmeqavmupYmavmue', 'CavdlleqDavmue', 'avleql0Zlavdl', 'Jll0leqKl',
                  'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau',
                  'Zmavdmtaueq0',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'avmeqm0Zmdm',
                  'EcavdleqFc', 'EavdlleqF']
        listcsfol = {'first': first, 'other': other, 'last': last}
        # Constraints for guarded nets        
        gother = [
                  'forceactf', 'forceactav', 'forceexef', 'forceexeav', 'mbounds', 'avmbounds',
                  'meqmupYmmue', 'CdluleqDmue', 'dleqdeltadlu', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'avmeqavmupYmavmue', 'CavdluleqDavmue', 'avdleqavdeltaavdlg', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma',
                  'SrxleqQrW1deltar', 'SravxrleqQrW1alphar',
                  'avmreqavmuprYmavmuer', 'CavdlurleqDavmuer', 'avlreql0Zlavdlr',
                  'avsigmara0eqavatrYsigmaavaer', 'AavdmrleqBavaer', 'avmreqm0Zmavdmr',
                  'epsavdeltarleq21alphar', 'epsavdeltargeq2alphar',
                  'alpharavaerleqae', 'alpharavdmrleqdm', 'alpharavdsigmarleqdsigma', 'alpharavsigmarleqsigma',
                  'avdlgereqalpharavdlurer', 'avdlreeqalpharavdlurer',
                  'sumdeltareq1', 'sumavdeltareq1', 'avxeqsumavdeltaravxr',
                  'sumavdeltarVleqsumavdeltasW',
                  'sumavdeltarVpeqsumavdeltasWp', 'sumavdeltaravxrVpeqsumavdeltasavxsWp'
                  ]
        gfirst = ['Jaa0leqKa', 'Jmm0leqKm'] + gother        
        glast =  [
                  'forceactav', 'forceexeav', 'JpmavmleqKpm', 'avmbounds',
                  'avmeqavmupYmavmue', 'CavdluleqDavmue', 'avdleqalphaavdlg', 'avleql0Zlavdl', 'Jll0leqKl',
                  'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau',
                  'Zmavdmtaueq0',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'avmeqm0Zmdm',
                  'EcavdleqFc', 'EavdlleqF',
                  'SravzrleqQrW1alphar',
                  'avmreqavmuprYmavmuer', 'CavdlurleqDavmuer', 'avlreql0Zlavdlr',
                  'avsigmataureqavattaurYsigmaavaetaur', 'AavdmtaurleqBavaetaur',
                  'sigmara0eqatrYsigmaaer', 'AdmrleqBaer', 'avmreqm0Zmdmr',
                  'avdlgereqalpharavdlurer', 'avdlreeqalpharavdlurer',
                  'sumalphareq1', 'avzeqsumalpharavzr',
                  'sumalpharVleqsumalphasW',
                  'sumalpharVpeqsumalphasWp', 'sumalpharavzrVpeqsumalphasavzsWp'
                  ]
        glistcsfol = {'first': gfirst, 'other': gother, 'last': glast}
        vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
        vdimdom.append(LFlexN.vdimdomgcst if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomst)
        LTCNmodel = self.buildmodel(listcsfol, glistcsfol, vdimdom, compQ = True, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(LTCNmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(LTCNmodel, vdimdom)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return LTCNmodel
        else:
            raise ValueError('LTCNmodel unbounded or infeasible')

    def optimun(self):
        """Optimize objective function objf for transient constraints TCN and last period as untimed"""
        ttic, tic = time.time(), time.clock()
        self.computetdepF()
        self.computeLU()
        self.info['perf']['Python processor time[L,U]'], self.info['perf']['Wall time[L,U]'] = time.clock()-tic, time.time()-ttic
        ttic, tic = time.time(), time.clock()
        self.computetindwl()
        self.computetindwu()
        self.computetindW()
        self.info['perf']['Python processor time[wl,wu,W]'], self.info['perf']['Wall time[wl,wu,W]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        other =  ['forceactf', 'forceactav', 'forceexef', 'forceexeav', 'mbounds', 'avmbounds',
                  'meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'avmeqavmupYmavmue', 'CavdlleqDavmue', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma']
        first =  ['Jaa0leqKa', 'Jmm0leqKm'] + other
        last =   ['forceactf', 'forceexef', 'JpmmleqKpm', 'mbounds',
                  'meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm']
        listcsfol = {'first': first, 'other': other, 'last': last}
        gother = [
                  'forceactf', 'forceactav', 'forceexef', 'forceexeav', 'mbounds', 'avmbounds',
                  'meqmupYmmue', 'CdluleqDmue', 'dleqdeltadlu', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'avmeqavmupYmavmue', 'CavdluleqDavmue', 'avdleqavdeltaavdlg', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma',
                  'SrxleqQrW1deltar', 'SravxrleqQrW1alphar',
                  'avmreqavmuprYmavmuer', 'CavdlurleqDavmuer', 'avlreql0Zlavdlr',
                  'avsigmara0eqavatrYsigmaavaer', 'AavdmrleqBavaer', 'avmreqm0Zmavdmr',
                  'epsavdeltarleq21alphar', 'epsavdeltargeq2alphar',
                  'alpharavaerleqae', 'alpharavdmrleqdm', 'alpharavdsigmarleqdsigma', 'alpharavsigmarleqsigma',
                  'avdlgereqalpharavdlurer', 'avdlreeqalpharavdlurer',
                  'sumdeltareq1', 'sumavdeltareq1', 'avxeqsumavdeltaravxr',
                  'sumavdeltarVleqsumavdeltasW',
                  'sumavdeltarVpeqsumavdeltasWp', 'sumavdeltaravxrVpeqsumavdeltasavxsWp'
                  ]
        gfirst = ['Jaa0leqKa', 'Jmm0leqKm'] + gother        
        glast =  ['forceactf', 'forceexef', 'JpmmleqKpm', 'mbounds',
                  'meqmupYmmue', 'CdluleqDmue', 'dleqdeltadlu', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'SrxleqQrW1deltar', 'sumdeltareq1']
        glistcsfol = {'first': gfirst, 'other': gother, 'last': glast}
        vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
        vdimdom.append(LFlexN.vdimdomgun if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomun)
        LTCNmodel = self.buildmodel(listcsfol, glistcsfol, vdimdom, compQ = True, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(LTCNmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(LTCNmodel, vdimdom)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return LTCNmodel
        else:
            raise ValueError('LTCNmodel unbounded or infeasible')

    def optimtr(self):
        """Optimize objective function objf for transient constraints TCN"""
        ttic, tic = time.time(), time.clock()
        self.computetdepF()
        self.computeLU()
        self.info['perf']['Python processor time[L,U]'], self.info['perf']['Wall time[L,U]'] = time.clock()-tic, time.time()-ttic
        ttic, tic = time.time(), time.clock()
        self.computetrwl()
        self.computetrwu()
        self.computetrW()
        self.info['perf']['Python processor time[wl,wu,W]'], self.info['perf']['Wall time[wl,wu,W]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        other =  ['forceactf', 'forceactav', 'forceexef', 'forceexeav', 'mbounds', 'avmbounds',
                  'meqmupYmmue', 'CdlleqDmue', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'avmeqavmupYmavmue', 'CavdlleqDavmue', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma']
        first = ['Jaa0leqKa', 'Jmm0leqKm'] + other
        last =  ['JpmmleqKpm'] + other
        listcsfol = {'first': first, 'other': other, 'last': last}
        gother = [
                  'forceactf', 'forceactav', 'forceexef', 'forceexeav', 'mbounds', 'avmbounds',
                  'meqmupYmmue', 'CdluleqDmue', 'dleqdeltadlu', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm',
                  'avmeqavmupYmavmue', 'CavdluleqDavmue', 'avdleqavdeltaavdlg', 'avleql0Zlavdl',
                  'dsigmaeqavdltheta', 'sigmaeql0thetaZldsigma',
                  'avsigmaeq05l0thetaZlavdsigma',
                  'avsigmaa0eqavatYsavae', 'AavdmleqBavae', 'avmeqm0Zmavdm',
                  'avaeleqae', 'avdmleqdm', 'avdsigmaleqdsigma', 'avsigmaleqsigma',
                  'EcdsigmaeqthetaFc', 'Ecavdsigmaeq05Ecdsigma',
                  'EdsigmaleqthetaF',
                  'thetaEavdsigmaleqquad2', 'quad2leqthetaEavdsigma',
                  'SrxleqQrW1deltar', 'SravxrleqQrW1alphar',
                  'avmreqavmuprYmavmuer', 'CavdlurleqDavmuer', 'avlreql0Zlavdlr',
                  'avsigmara0eqavatrYsigmaavaer', 'AavdmrleqBavaer', 'avmreqm0Zmavdmr',
                  'epsavdeltarleq21alphar', 'epsavdeltargeq2alphar',
                  'alpharavaerleqae', 'alpharavdmrleqdm', 'alpharavdsigmarleqdsigma', 'alpharavsigmarleqsigma',
                  'avdlgereqalpharavdlurer', 'avdlreeqalpharavdlurer',
                  'sumdeltareq1', 'sumavdeltareq1', 'avxeqsumavdeltaravxr',
                  'sumavdeltarVleqsumavdeltasW',
                  'sumavdeltarVpeqsumavdeltasWp', 'sumavdeltaravxrVpeqsumavdeltasavxsWp'
                  ]
        gfirst = ['Jaa0leqKa', 'Jmm0leqKm'] + gother
        glast =  ['JpmmleqKpm'] + gother
        glistcsfol = {'first': gfirst, 'other': gother, 'last': glast}
        vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets))]
        LTCNmodel = self.buildmodel(listcsfol, glistcsfol, vdimdom, compQ = True, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(LTCNmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(LTCNmodel, vdimdom)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return LTCNmodel
        else:
            print('Solver status:', results.solver.status, '. Termination condition:', results.solver.termination_condition)###
            raise ValueError('LTCNmodel unbounded or infeasible')

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
        """Plot variables"""
        if 'plotres' in self.options and self.options['plotres']:
            self.plotres()
        """Return model"""
        return model

        
    def saveres(self, model, vdimdom):
        """Save results from model to net"""
        self.objval = model.obj.expr()
        """Variables of periods"""
        for idx, qnet in enumerate(self.qnets):
            preq = LFlexN.qpre+str(idx)+'_'
            for var in vdimdom[idx]:
                auxdict = getattr(qnet, vdimdom[idx][var]['dim'])
                for it in auxdict:
                    setattr(auxdict[it], var, getattr(model,preq+var)[it].value)
        """Variables of macro periods"""
        for IDX, Qnet in enumerate(self.Qnets):
            preQ = LFlexN.Qpre+str(IDX)+'_'
            vdido = vdimdom[self.mappers[IDX]['qlast']]
            if  vdido == LFlexN.vdimdomtr or vdido == LFlexN.vdimdomgtr:            
                for var in vdido:
                    auxdict = getattr(Qnet, vdido[var]['dim'])
                    for it in auxdict:
                        setattr(auxdict[it], var, getattr(model,preQ+var)[it].value)
        
    def printres(self):
        """Print results"""
        """Periods"""
        if self.options['antype'] in ['tr', 'mpc']:
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets))]
        elif self.options['antype'] == 'st':
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgst if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomst)
        elif self.options['antype'] == 'cst':
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgcst if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomst)
        elif self.options['antype'] == 'un':
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgun if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomun)
        else:
            raise ValueError('Unknown analysis type')
        for idx, qnet in enumerate(self.qnets):
            if  vdimdom[idx] == LFlexN.vdimdomtr or vdimdom[idx] == LFlexN.vdimdomgtr:
                tauf = qnet.tauf
            elif vdimdom[idx] == LFlexN.vdimdomst or vdimdom[idx] == LFlexN.vdimdomgst:
                tauf = 'steady state'
            elif vdimdom[idx] == LFlexN.vdimdomgcst:
                tauf = 'constant steady state'
            else:
                tauf = 'untimed'
            print('-------- Period: ', idx, 'from', qnet.tau0, 'to', tauf)
            for var in sorted(vdimdom[idx]):
                auxdict = getattr(qnet, vdimdom[idx][var]['dim'])
                for it in sorted(auxdict):
                    print(var,'[',it,']=', getattr(auxdict[it], var), sep='')
        """Macro periods"""
        for IDX, Qnet in enumerate(self.Qnets):
            vdido = vdimdom[self.mappers[IDX]['qlast']]
            if  vdido == LFlexN.vdimdomtr or vdido == LFlexN.vdimdomgtr:            
                print('-------- Macro period: ', IDX, 'from', Qnet.tau0, 'to', qnet.tauf)
                for var in sorted(vdido):
                    auxdict = getattr(Qnet, vdido[var]['dim'])
                    for it in sorted(auxdict):
                        print(var,'[',it,']=', getattr(auxdict[it], var), sep='')
        print('Objective:', self.objval)
        
    def plotres(self, plotvars = None, periods = 'all', marginper = 0.05):
        """Plot the variables in dictionary plvs, e.g., plvs = {'evm':['p1','p2'], 'm':['p1','p2'], 'sigma': ['t1']}
           where plvs =self.options['plotvars'] if plotvars == None else plotvars
           Each key of plotvars is a variable name or 'evm' or 'eva'. Variable names
           are plotted as steps (stair-like plot). 'evm' and 'eva' plot the marking and
           actions evolution, ie, lines connecting initial and final markings(actions) are plotted.
           if periods == 'all' the values of all qnets are plot
           otherwise the values of qnets in the interval periods[0]:periods[1] are plot (this might be useful for untimed and steady state analysis)
           marginper is the figure percentage to be left blank above and below plotted lines
        """
        nets = self.qnets if periods == 'all' else self.qnets[periods[0]:periods[1]]
        boty, topy = float('inf'), -float('inf') # bottom and top to fix y axis
        plvs = deepcopy(self.options['plotvars']) if plotvars == None else deepcopy(plotvars)
        """Print marking and actions evolution"""
        if 'evm' in plvs: # plot marking evolution, ie, lines connecting the initial and final marking of periods
            tpsm = []  # Time points for markings
            for qnet in nets:            
                tpsm = tpsm + [qnet.tau0, qnet.tauf]
            for pl in plvs['evm']:            
                evm = []  # evolution of the marking                
                for qnet in nets:
                    if pl in qnet.places:
                        if hasattr(qnet.places[pl],'m'):
                            evm = evm + [qnet.places[pl].m0, qnet.places[pl].m]
                        else:
                            evm = evm + [qnet.places[pl].m0, qnet.places[pl].avm] # Steady state marking of last qnet
                    else:
                        evm = evm + [-1, -1]
                boty, topy = min([boty]+evm), max([topy]+evm)
                plt.plot(tpsm, evm, '.-', label='evm['+pl+']')
            plvs.pop('evm')
        if 'eva' in plvs: # plot actions evolution, ie, lines connecting the initial and final actions of periods
            tpsa = []  # Time points for markings
            for qnet in nets:            
                tpsa = tpsa + [qnet.tau0, qnet.tauf]
            for tr in plvs['eva']:            
                eva = []  # evolution of the actions
                for qnet in nets:
                    if tr in qnet.trans:
                        eva = eva + [qnet.trans[tr].a0, qnet.trans[tr].at]
                    else:
                        eva = eva + [-1, -1]
                boty, topy = min([boty]+eva), max([topy]+eva)
                plt.plot(tpsa, eva, '.-', label='eva['+tr+']')
            plvs.pop('eva')
        """Print rest of variables""" 
        tps = [qnet.tau0 for qnet in nets]
        tps.append(nets[-1].tauf)
        for va in plvs:
            for it in plvs[va]:            
                ev = []  # evolution of the variable
                for qnet in nets:
                    vdido = LFlexN.vdimdomgtr if hasattr(qnet,'regs') else LFlexN.vdimdomtr
                    if va in vdido and it in getattr(qnet,vdido[va]['dim']):
                        ev.append(getattr(getattr(qnet,vdido[va]['dim'])[it],va))
                    else:
                        ev.append(-1)
                ev.append(ev[-1])
                boty, topy = min([boty]+ev), max([topy]+ev)
                plt.step(tps, ev, marker = '.', where='post', label=va+'['+str(it)+']')
        plt.legend(loc='best')
        margin = marginper*(topy-boty) # marginper% of margin at top and bottom
        plt.axis([0, nets[-1].tauf, boty - margin, topy + margin])
        plt.xlabel('time')
        plt.show(block=True)

    def writexls(self, xlsfile):
        """Write results to spreadsheet file xlsfile"""
        wb = self.genxlsdata()
        wb.save(xlsfile)
        
    def genxlsdata(self, wb=None, namesh=None, writeinfo=True, initau=None, maxcols=250):
        """Generate data to be stored in a spreadsheet"""
        # maxcols: Maximum number of columns to write before wrapping
        MaxPerxlwt = 252 # The maximum number of columns allowed by xlwt is 256
        if maxcols > MaxPerxlwt:
            maxcols = MaxPerxlwt
            print("Warning: The maximum number of columns allowed by xlwt is 256. Setting maxcols to", MaxPerxlwt)
            
        def compnprvars(wrvars, extvals, vdimdom, qfirst):
            """Compute number of variables, i.e., columns, to write"""
            nprvars = 0
            for var in wrvars:
                if var not in extvals and var in vdimdom[qfirst]:
                    auxdict = getattr(self.qnets[qfirst], vdimdom[qfirst][var]['dim'])
                    for it in auxdict:
                        if wrvars[var]=='all' or it in wrvars[var]:
                            nprvars += 1
            if hasattr(self.qnets[qfirst], 'wl') and 'wl' in wrvars:
                nprvars += 1
            if hasattr(self.qnets[qfirst], 'wu') and 'wu' in wrvars:
                nprvars += 1
            if hasattr(self.qnets[qfirst], 'W') and 'W' in wrvars:
                nprvars += 1
            if 'writeLUnegsa' in self.options and not self.options['writeLUnegsa']:
                auxrows = self.qnets[qfirst].E + self.qnets[qfirst].Ec
                eecrows = [er for er in auxrows if (len(er)==1 and er.values() != [-1]) or len(er)>1]
            else:
                eecrows = self.qnets[qfirst].E + self.qnets[qfirst].Ec
            if self.qnets[qfirst].L and 'L' in wrvars:   
                nprvars += len(eecrows)
            if self.qnets[qfirst].U and 'U' in wrvars: 
                nprvars += len(eecrows)
            return nprvars + 8  # Add rows for objective function, periods, etc

        def wrap(row, col, nprvars):
            """Overcome the limitation to 256 columns of xlwt by wrapping lines"""
            # nprvars: Number of rows between wrapped lines
            quot, rem = divmod(col, maxcols)
            return (row + quot*nprvars, rem + 1)
            
        extvals = ['wl', 'wu', 'W', 'L', 'U']  # Extra values than can be written
        """Dimension and domain of variables over periods"""
        if self.options['antype'] in ['tr', 'mpc']:
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets))]
        elif self.options['antype'] == 'st':
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgst if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomst)
        elif self.options['antype'] == 'cst':
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgcst if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomst)
        elif self.options['antype'] == 'un':
            vdimdom = [LFlexN.vdimdomgtr if hasattr(self.qnets[i],'regs') else LFlexN.vdimdomtr for i in range(len(self.qnets)-1)]
            vdimdom.append(LFlexN.vdimdomgun if hasattr(self.qnets[-1],'regs') else LFlexN.vdimdomun)
        else:
            raise ValueError('Unknown analysis type')
        """Create sheets"""
        bstyle = xlwt.easyxf('font: bold on')
        wb = xlwt.Workbook() if wb is None else wb
        ws = {}  # Dictionary to store the sheets
        """Iterate over macro periods"""
        for IDX, mapper in enumerate(self.mappers):
            qfirst, qlast = mapper['qfirst'], mapper['qlast']
            if self.options['writevars'] == 'all':
                wrvars = {key: 'all' for key in vdimdom[qfirst]}
                for key in extvals:
                    wrvars[key] = 'all'
            else:
                wrvars = self.options['writevars']
            nprvars = compnprvars(wrvars, extvals, vdimdom, qfirst)
            cursh = 'Q'+str(IDX)+' transient' if namesh == None else namesh
            ws[cursh] = wb.add_sheet(cursh)
            row = 0
            if IDX == 0:
                for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                    ws[cursh].write(row+ssr*nprvars, 0, 'Objective:', bstyle)
                if isinstance(self.objval, list): # List of values from MPC
                    for step in range(qfirst, qlast+1):
                        posr, posc = wrap(row, step-qfirst, nprvars)
                        ws[cursh].write(posr, posc, self.objval[step])
                else:
                    ws[cursh].write(row, 1, self.objval, bstyle)
                row += 2
            """Iterate over periods"""
            lvdido = vdimdom[qlast]
            if lvdido == LFlexN.vdimdomtr or lvdido == LFlexN.vdimdomgtr:
                lastper = 'tr'  # Last period of macroperiod is transient
                lasttrper = qlast # Last transient period of the macroperiod
            elif lvdido == LFlexN.vdimdomst or lvdido == LFlexN.vdimdomgst:
                lastper = 'st'  # Last period of macroperiod is steady state
                lasttrper = qlast-1
            elif lvdido == LFlexN.vdimdomgcst:
                lastper = 'cst'  # Last period of macroperiod is constant steady state
                lasttrper = qlast-1
            elif lvdido == LFlexN.vdimdomun or lvdido == LFlexN.vdimdomgun:
                lastper = 'un'  # Last period of macroperiod is untimed
                lasttrper = qlast-1
            """Write period index"""
            for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                ws[cursh].write(row+ssr*nprvars, 0, 'Period:', bstyle)
            for per in range(qfirst, lasttrper+1):
                posr, posc = wrap(row, per-qfirst, nprvars)
                ws[cursh].write(posr, posc, per, bstyle)
            if lastper == 'tr':
                posr, posc = wrap(row, lasttrper+1-qfirst, nprvars)
                ws[cursh].write(posr, posc, 'Overall', xlwt.easyxf('font: bold on; align: horiz right'))
            row += 1
            """Write final time of each period index"""
            if initau == None:
                for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                    ws[cursh].write(row+ssr*nprvars, 0, 'tauf:', bstyle)
            else:
                for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                    strtauf = 'tauf: '+str(initau)+'+'
                    ws[cursh].write(row+ssr*nprvars, 0, strtauf, bstyle)
            for per in range(qfirst, lasttrper+1):
                posr, posc = wrap(row, per-qfirst, nprvars)
                ws[cursh].write(posr, posc, self.qnets[per].tauf, bstyle)
            if lastper == 'tr':
                posr, posc = wrap(row, lasttrper+1-qfirst, nprvars)
                ws[cursh].write(posr, posc, '['+str(self.Qnets[IDX].tau0)+', '+str(self.Qnets[IDX].tauf)+']', xlwt.easyxf('font: bold on; align: horiz right'))
            row += 1
            """Write variable values of each period index"""
            for var in sorted(wrvars):
                if var not in extvals and var in vdimdom[qfirst]:
                    auxdict = getattr(self.qnets[qfirst], vdimdom[qfirst][var]['dim'])
                    for it in sorted(auxdict):
                        if wrvars[var]=='all' or it in wrvars[var]:
                            for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                                ws[cursh].write(row+ssr*nprvars, 0, str(var)+'['+str(it)+']', bstyle)
                            for per in range(qfirst, lasttrper+1):
                                sdict = getattr(self.qnets[per], vdimdom[qfirst][var]['dim'])
                                posr, posc = wrap(row, per-qfirst, nprvars)
                                ws[cursh].write(posr, posc, getattr(sdict[it], var))
                            if lastper == 'tr': # Write aggregate variables of macroperiod
                                Sdict = getattr(self.Qnets[IDX], vdimdom[qfirst][var]['dim'])
                                posr, posc = wrap(row, lasttrper+1-qfirst, nprvars)
                                ws[cursh].write(posr, posc, getattr(Sdict[it], var))
                            row += 1
            """Write wl, wu, W, L, U"""               
            if hasattr(self.qnets[qfirst], 'wl') and 'wl' in wrvars:
                for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                    ws[cursh].write(row+ssr*nprvars, 0, 'wl', bstyle)
                for per in range(qfirst, lasttrper+1):
                    posr, posc = wrap(row, per-qfirst, nprvars)
                    ws[cursh].write(posr, posc, self.qnets[per].wl)
                row += 1
            if hasattr(self.qnets[qfirst], 'wu') and 'wu' in wrvars:
                for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                    ws[cursh].write(row+ssr*nprvars, 0, 'wu', bstyle)
                for per in range(qfirst, lasttrper+1):
                    posr, posc = wrap(row, per-qfirst, nprvars)
                    ws[cursh].write(posr, posc, self.qnets[per].wu)
                row += 1
            if hasattr(self.qnets[qfirst], 'W') and 'W' in wrvars:
                for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                    ws[cursh].write(row+ssr*nprvars, 0, 'W', bstyle)
                for per in range(qfirst, lasttrper+1):
                    posr, posc = wrap(row, per-qfirst, nprvars)
                    ws[cursh].write(posr, posc, self.qnets[per].W)
                row += 1
            if 'writeLUnegsa' in self.options and not self.options['writeLUnegsa']:
                auxrows = self.qnets[qfirst].E + self.qnets[qfirst].Ec
                eecrows = [er for er in auxrows if (len(er)==1 and er.values() != [-1]) or len(er)>1] # Filter components of one element with weight -1
            else:
                eecrows = self.qnets[qfirst].E + self.qnets[qfirst].Ec
            if self.qnets[qfirst].L and 'L' in wrvars and self.qnets[qfirst].U and 'U' in wrvars:
                for eecrow in eecrows: # For each row of E+Ec
                    for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                        ws[cursh].write(row+ssr*nprvars, 0, 'L['+str(eecrow)+']', bstyle)
                    for per in range(qfirst, lasttrper+1):
                        if eecrow in self.qnets[per].E:
                            posr, posc = wrap(row, per-qfirst, nprvars)
                            ws[cursh].write(posr, posc, self.qnets[per].L[self.qnets[per].E.index(eecrow)])
                        else:
                            posr, posc = wrap(row, per-qfirst, nprvars)
                            ws[cursh].write(posr, posc, self.qnets[per].Fc[self.qnets[per].Ec.index(eecrow)])                            
                    row += 1
                    for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                        ws[cursh].write(row+ssr*nprvars, 0, 'U['+str(eecrow)+']', bstyle)
                    for per in range(qfirst, lasttrper+1):
                        if eecrow in self.qnets[per].E:
                            posr, posc = wrap(row, per-qfirst, nprvars)
                            ws[cursh].write(posr, posc, self.qnets[per].U[self.qnets[per].E.index(eecrow)])
                        else:
                            posr, posc = wrap(row, per-qfirst, nprvars)
                            ws[cursh].write(posr, posc, self.qnets[per].Fc[self.qnets[per].Ec.index(eecrow)])                            
                    row += 1
            elif self.qnets[qfirst].L and 'L' in wrvars:   
                for eecrow in eecrows: # For each row of E+Ec
                    for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                        ws[cursh].write(row+ssr*nprvars, 0, 'L['+str(eecrow)+']', bstyle)
                    for per in range(qfirst, lasttrper+1):
                        if eecrow in self.qnets[per].E:
                            posr, posc = wrap(row, per-qfirst, nprvars)
                            ws[cursh].write(posr, posc, self.qnets[per].L[self.qnets[per].E.index(eecrow)])
                        else:
                            posr, posc = wrap(row, per-qfirst, nprvars)
                            ws[cursh].write(posr, posc, self.qnets[per].Fc[self.qnets[per].Ec.index(eecrow)])                            
                    row += 1
            elif self.qnets[qfirst].U and 'U' in wrvars: 
                for eecrow in eecrows: # For each row of E+Ec
                    for ssr in range(int((qlast+1-qfirst)/maxcols)+1):
                        ws[cursh].write(row+ssr*nprvars, 0, 'U['+str(eecrow)+']', bstyle)
                    for per in range(qfirst, lasttrper+1):
                        if eecrow in self.qnets[per].E:
                            posr, posc = wrap(row, per-qfirst, nprvars)
                            ws[cursh].write(posr, posc, self.qnets[per].U[self.qnets[per].E.index(eecrow)])
                        else:
                            posr, posc = wrap(row, per-qfirst, nprvars)
                            ws[cursh].write(posr, posc, self.qnets[per].Fc[self.qnets[per].Ec.index(eecrow)])                            
                    row += 1
            """Write final untimed or steady state period"""
            if lastper in ['un', 'st', 'cst']:
                if self.options['writevars'] == 'all':
                    wrvars = {key: 'all' for key in vdimdom[qlast]}
                    for key in extvals:
                        wrvars[key] = 'all'
                else:
                    wrvars = self.options['writevars']
                if lastper == 'un':
                    cursh = 'Q'+str(IDX)+' untimed'
                elif lastper == 'st':
                    cursh = 'Q'+str(IDX)+' steady state'
                else:
                    cursh = 'Q'+str(IDX)+' constant steady state'
                ws[cursh] = wb.add_sheet(cursh)
                row = 0
                for var in sorted(wrvars):
                    if var not in ['wl', 'wu', 'W', 'L', 'U'] and var in vdimdom[qlast]:
                        auxdict = getattr(self.qnets[qlast], vdimdom[qlast][var]['dim'])
                        for it in sorted(auxdict):
                            if wrvars[var]=='all' or it in wrvars[var]:
                                ws[cursh].write(row, 0, str(var)+'['+str(it)+']', bstyle)
                                ws[cursh].write(row, 1, getattr(auxdict[it], var))
                                row += 1
                if hasattr(self.qnets[qlast], 'wl') and 'wl' in wrvars: # Only wl, wu and W can be present in this final period
                    ws[cursh].write(row, 0, 'wl', bstyle)
                    ws[cursh].write(row, 1, self.qnets[qlast].wl)
                    row += 1
                if hasattr(self.qnets[qlast], 'wu') and 'wu' in wrvars:
                    ws[cursh].write(row, 0, 'wu', bstyle)
                    ws[cursh].write(row, 1, self.qnets[qlast].wu)
                    row += 1
                if hasattr(self.qnets[qlast], 'W') and 'W' in wrvars:
                    ws[cursh].write(row, 0, 'W', bstyle)
                    ws[cursh].write(row, 1, self.qnets[qlast].W)

        """Write performance"""
        if writeinfo:
            wi = wb.add_sheet('Info')
            row = 0
            if self.options['antype'] == 'mpc':
                wi.write(row, 0, 'Problem (1st step)', bstyle)
            else:
                wi.write(row, 0, 'Problem', bstyle)
            row += 1
            for key,val in sorted(self.info['result']['Problem'][0].items()):
                wi.write(row, 1, key)
                if isinstance(val, dict):
                    val = str(val)
                wi.write(row, 2, val)
                row += 1
            if self.options['antype'] == 'mpc':
                wi.write(row, 0, 'Solver (1st step)', bstyle)
            else:                
                wi.write(row, 0, 'Solver', bstyle)
            row += 1
            for key,val in sorted(self.info['result']['Solver'][0].items()):
                wi.write(row, 1, key)
                if isinstance(val, dict):
                    val = str(val)
                wi.write(row, 2, val)
                row += 1
    
            if self.options['antype'] == 'mpc':
                wi.write(row, 0, 'Performance (all steps) (seconds)', bstyle)
            else:
                wi.write(row, 0, 'Performance (seconds)', bstyle)
            row += 1
            for key, val in sorted(self.info['perf'].items()):
                wi.write(row, 1, key)
                wi.write(row, 2, val)
                row += 1

        return wb

