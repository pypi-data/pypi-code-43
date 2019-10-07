from __future__ import division, print_function
from fnyzer import FlexN
from fnyzer import netel # Net elements
import pyomo.environ as pyomo
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
import time
import itertools
from numpy import log
import random
import warnings

class GFlexN(FlexN):
    """Guarded Flexible Net"""
 
    """Variable names, dimension and domains for analysis without average values, e.g., untimed"""
    vdimdomun= {'m0'    : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # initial marking
                'm'     : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # final marking
                'mup'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # final mup
                'mue'   : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals},   # final mue
                'dlu'   : {'dim': 'sarcxguards', 'dom': pyomo.Reals}, # d lambda_U (before guards)
                'dl'    : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals},   # d lambda
#                'delta' : {'dim': 'sarcxguards', 'dom': pyomo.Binary},        # matrix delta. deltar is used instead of delta
                'deltadlu':{'dim':'sarcxguards', 'dom': pyomo.NonNegativeReals},  # delta*dlambda_U (elementwise multiplication)             
                'l'     : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # lambda
                'l0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # lambda0
                'a0'    : {'dim': 'trans', 'dom': pyomo.NonNegativeReals},    # initial actions
                'sigma' : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # sigma
                'at'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # at
                'ae'    : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals},   # ae
                'dm'    : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals},   # d m
                'deltar': {'dim': 'regs', 'dom': pyomo.Binary}   # delta_r
               }

    """Variable names, dimension and domains for steady state analysis"""
    vdimdomst= {'m0'    : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # initial marking
                'avm'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # average marking
                'avmup' : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # average mup
                'avmue' : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals},   # average mue
                'avdlu' : {'dim': 'sarcxguards', 'dom': pyomo.Reals}, # average d lambda_U (before guards)
                'avdl'  : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals},   # average d lambda
#                'avdelta':{'dim': 'sarcxguards', 'dom': pyomo.NonNegativeReals}, # average matrix delta. avdeltar is used instead of avdelta
                'avdlg' : {'dim': 'sarcxguards', 'dom': pyomo.NonNegativeReals}, # average d lambda_G
                'avl'   : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # average lambda
                'l0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # lambda0
#                'avdsigmatau'  : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals},   # average d sigma, it is equal to avdl, it is omitted to reduce the number of variables
                'avsigmatau':{'dim':'trans','dom': pyomo.NonNegativeReals},   # average sigma
                'avattau':{'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # average at
                'avaetau':{'dim': 'vedges', 'dom': pyomo.NonNegativeReals},   # average ae
                'avdmtau':{'dim': 'varcs',  'dom': pyomo.NonNegativeReals},   # average d m
                'a0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # initial actions
                'sigma' : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # sigma
                'at'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # at
                'ae'    : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals},   # ae
                'dm'    : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals},   # d m
                'avmr'  : {'dim': 'placexregs', 'dom': pyomo.NonNegativeReals},   # average marking at regions
                'avmupr' :{'dim': 'placexregs', 'dom': pyomo.NonNegativeReals},   # average mup at regions
                'avmuer' :{'dim': 'sedgexregs', 'dom': pyomo.NonNegativeReals},   # average mue at regions
                'avdlur' :{'dim': 'sarcxguardxregs', 'dom': pyomo.Reals}, # average d lambda_U at regions
                'avlr'  : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},   # average lambda at regions
                'avdlr' : {'dim': 'sarcxregs',  'dom': pyomo.NonNegativeReals},   # average d lambda at regions
                'avsigmataur':{'dim':'tranxregs','dom': pyomo.NonNegativeReals},  # average sigma at regions
                'avattaur':{'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},  # average at at regions
                'avaetaur':{'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals},  # average ae at regions
                'avdmtaur':{'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals},  # average d m at regions
                'sigmar' : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},  # sigma at regions
                'atr'    : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},  # at at regions
                'aer'    : {'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals},  # ae at regions
                'dmr'    : {'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals},  # d m at regions
                'avdeltar':{'dim': 'regs', 'dom': pyomo.NonNegativeReals},         # average delta_r
                'alphar':  {'dim': 'regs', 'dom': pyomo.Binary}, # alpha_r
                'gammar':  {'dim': 'regs', 'dom': pyomo.Binary}, # gamma_r
                'beta' : {'dim': 'regxqs', 'dom': pyomo.Binary}, # beta variables for linearization
                'betaavdlg': {'dim': 'sarcxguardxqs', 'dom': pyomo.NonNegativeReals}, # beta avdlg
                'avdeltaavdlg': {'dim': 'sarcxguards', 'dom': pyomo.NonNegativeReals}, # avdelta avdlg
                'betaavmr': {'dim': 'placexregxqs', 'dom': pyomo.NonNegativeReals}, # beta avmr
                'avdeltaravmr': {'dim': 'placexregs', 'dom': pyomo.NonNegativeReals},  # avdeltar avmr
                'betaavmupr': {'dim': 'placexregxqs', 'dom': pyomo.NonNegativeReals}, # beta avmupr
                'avdeltaravmupr':{'dim': 'placexregs', 'dom': pyomo.NonNegativeReals}, # avdeltar avmupr
                'betaavmuer': {'dim': 'sedgexregxqs', 'dom': pyomo.NonNegativeReals}, # beta avmuer
                'avdeltaravmuer':{'dim': 'sedgexregs', 'dom': pyomo.NonNegativeReals}, # avdeltar avmuer
#                'betaavdlur': {'dim': 'sarcxguardxregxqs', 'dom': pyomo.Reals}, # beta avdlur
#                'avdeltaravdlur':{'dim': 'sarcxguardxregs', 'dom': pyomo.NonNegativeReals}, # avdeltar avdlur
#                'betaavdlr': {'dim': 'sarcxregxqs', 'dom': pyomo.NonNegativeReals}, # beta avdlr
#                'avdeltaravdlr' : {'dim': 'sarcxregs',  'dom': pyomo.NonNegativeReals},# avdeltar avdlr
#                'betaavlr': {'dim': 'tranxregxqs', 'dom': pyomo.NonNegativeReals}, # beta avlr
#                'avdeltaravlr'  : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},# avdeltar avlr
                'betaavsigmataur': {'dim': 'tranxregxqs', 'dom': pyomo.NonNegativeReals}, # beta avsigmataur
                'avdeltaravsigmataur':{'dim':'tranxregs','dom': pyomo.NonNegativeReals}, # avdeltar avsigmataur
                'betaavattaur': {'dim': 'tranxregxqs', 'dom': pyomo.NonNegativeReals}, # beta avattaur
                'avdeltaravattaur':{'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals}, # avdeltar avattaur
                'betaavaetaur': {'dim': 'vedgexregxqs', 'dom': pyomo.NonNegativeReals}, # beta avaetaur
                'avdeltaravaetaur':{'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals}, # avdeltar avaetaur
                'betaavdmtaur': {'dim': 'varcxregxqs', 'dom': pyomo.NonNegativeReals}, # beta avaetaur
                'avdeltaravdmtaur':{'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals}  # avdeltaravdmtaur
                }

    """Variable names, dimension and domains for constant steady state analysis"""
    vdimdomcst={'m0'    : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # initial marking
                'avm'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # average marking
                'avmup' : {'dim': 'places', 'dom': pyomo.NonNegativeReals},   # average mup
                'avmue' : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals},   # average mue
                'avdlu' : {'dim': 'sarcxguards', 'dom': pyomo.Reals}, # average d lambda_U (before guards)
                'avdl'  : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals},   # average d lambda
                'avdlg' : {'dim': 'sarcxguards', 'dom': pyomo.NonNegativeReals}, # average d lambda_G
                'avl'   : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # average lambda
                'l0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # lambda0
#                'avdsigmatau'  : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals},   # average d sigma, it is equal to avdl, it is omitted to reduce the number of variables
                'avsigmatau':{'dim':'trans','dom': pyomo.NonNegativeReals},   # average sigma
                'avattau':{'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # average at
                'avaetau':{'dim': 'vedges', 'dom': pyomo.NonNegativeReals},   # average ae
                'avdmtau':{'dim': 'varcs',  'dom': pyomo.NonNegativeReals},   # average d m
                'a0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # initial actions
                'sigma' : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # sigma
                'at'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals},   # at
                'ae'    : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals},   # ae
                'dm'    : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals},   # d m
                'avmr'  : {'dim': 'placexregs', 'dom': pyomo.NonNegativeReals},   # average marking at regions
                'avmupr' :{'dim': 'placexregs', 'dom': pyomo.NonNegativeReals},   # average mup at regions
                'avmuer' :{'dim': 'sedgexregs', 'dom': pyomo.NonNegativeReals},   # average mue at regions
                'avdlur' :{'dim': 'sarcxguardxregs', 'dom': pyomo.Reals}, # average d lambda_U at regions
                'avlr'  : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},   # average lambda at regions
                'avdlr' : {'dim': 'sarcxregs',  'dom': pyomo.NonNegativeReals},   # average d lambda at regions
                'avsigmataur':{'dim':'tranxregs','dom': pyomo.NonNegativeReals},  # average sigma at regions
                'avattaur':{'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},  # average at at regions
                'avaetaur':{'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals},  # average ae at regions
                'avdmtaur':{'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals},  # average d m at regions
                'sigmar' : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},  # sigma at regions
                'atr'    : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals},  # at at regions
                'aer'    : {'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals},  # ae at regions
                'dmr'    : {'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals},  # d m at regions
                'alphar':  {'dim': 'regs', 'dom': pyomo.Binary}, # alpha_r
                'alphaavdlg': {'dim': 'sarcxguards', 'dom': pyomo.NonNegativeReals}, # alpha avdlg
                'alpharavmr': {'dim': 'placexregs', 'dom': pyomo.NonNegativeReals},  # alphar avmr
                'alpharavmupr':{'dim': 'placexregs', 'dom': pyomo.NonNegativeReals}, # alphar avmupr
                'alpharavmuer':{'dim': 'sedgexregs', 'dom': pyomo.NonNegativeReals}, # alphar avmuer
                'alpharavsigmataur':{'dim':'tranxregs','dom': pyomo.NonNegativeReals}, # alphar avsigmataur
                'alpharavattaur':{'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals}, # alphar avattaur
                'alpharavaetaur':{'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals}, # alphar avaetaur
                'alpharavdmtaur':{'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals}  # alpharavdmtaur
                }

    """Variable names, dimension and domains for transient state analysis"""
    vdimdomtr= {'m0'    : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'ini'},   # initial marking
                'm'     : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # final marking
                'mup'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # final mup
                'mue'   : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # final mue
                'dlu'   : {'dim': 'sarcxguards', 'dom': pyomo.Reals, 'Qtype': 'fin'}, # d lambda_U (before guards)
                'dl'    : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # d lambda
#                'delta' : {'dim': 'sarcxguards', 'dom': pyomo.Binary},        # matrix delta. deltar is used instead of delta
                'deltadlu':{'dim':'sarcxguards', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},  # delta*dlambda_U (elementwise multiplication)             
                'l'     : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # lambda
                'l0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # lambda0
                'a0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'ini'},   # initial actions
                'sigma' : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'add'},   # sigma
                'at'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # at
                'ae'    : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals, 'Qtype': 'add'},   # ae
                'dm'    : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'add'},   # d m
                'avm'   : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average marking
                'avmup' : {'dim': 'places', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average mup
                'avmue' : {'dim': 'sedges', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average mue
                'avdlu' : {'dim': 'sarcxguards', 'dom': pyomo.Reals, 'Qtype': 'av'}, # average d lambda_U (before guards)
                'avdl'  : {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average d lambda
#                'avdelta':{'dim': 'sarcxguards', 'dom': pyomo.NonNegativeReals}, # average matrix delta. avdeltar is used instead of avdelta
                'avdlg' : {'dim': 'sarcxguards', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'}, # average d lambda_G
                'avl'   : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average lambda
                'l0'    : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # lambda0
                'dsigma': {'dim': 'sarcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'add'},   # d sigma
                'avsigma':{'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average sigma
                'avdsigma':{'dim': 'sarcs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average d sigma
                'avat'  : {'dim': 'trans',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average at
                'avae'  : {'dim': 'vedges', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average ae
                'avdm'  : {'dim': 'varcs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average d m
                'deltar': {'dim': 'regs', 'dom': pyomo.Binary, 'Qtype': 'fin'},   # delta_r             
                'avmr'  : {'dim': 'placexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average marking at regions
                'avmupr' :{'dim': 'placexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average mup at regions
                'avmuer' :{'dim': 'sedgexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average mue at regions
                'avdlur' :{'dim': 'sarcxguardxregs', 'dom': pyomo.Reals, 'Qtype': 'av'}, # average d lambda_U at regions
                'avlr'  : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average lambda at regions
                'avdlr' : {'dim': 'sarcxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average d lambda at regions
                'avdsigmar':{'dim':'sarcxregs','dom': pyomo.NonNegativeReals, 'Qtype': 'av'},  # average dsigma at regions
                'avsigmar':{'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},   # average sigma at regions
                'avatr':{'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},  # average at at regions
                'avaer':{'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},  # average ae at regions
                'avdmr':{'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'av'},  # average d m at regions
                'avdeltar':{'dim': 'regs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'av'}, # average delta_r
                'alphar':{'dim': 'regs', 'dom': pyomo.Binary, 'Qtype': 'fin'}, # alpha_r
                'gammar':{'dim': 'regs', 'dom': pyomo.Binary, 'Qtype': 'fin'}, # gamma_r
                'alpharavaer':{'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},  # alphar average ae at regions
                'alpharavdmr':{'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},  # alphar average d m at regions
                'alpharavdsigmar':{'dim':'sarcxregs','dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},  # alphar average dsigma at regions
                'alpharavsigmar':{'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},   # alphar average sigma at regions
                'beta' : {'dim': 'regxqs', 'dom': pyomo.Binary, 'Qtype': 'fin'}, # beta variables for linearization
                'betaavdlg': {'dim': 'sarcxguardxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avdlg
                'avdeltaavdlg': {'dim': 'sarcxguards', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # avdelta avdlg
                'betaavmr': {'dim': 'placexregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avmr
                'avdeltaravmr': {'dim': 'placexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},  # avdeltar avmr
                'betaavmupr': {'dim': 'placexregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avmupr
                'avdeltaravmupr':{'dim': 'placexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # avdeltar avmupr
                'betaavmuer': {'dim': 'sedgexregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avmuer
                'avdeltaravmuer':{'dim': 'sedgexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # avdeltar avmuer
#                'betaavdlur': {'dim': 'sarcxguardxregxqs', 'dom': pyomo.Reals, 'Qtype': 'fin'}, # beta avdlur
#                'avdeltaravdlur':{'dim': 'sarcxguardxregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # avdeltar avdlur
#                'betaavdlr': {'dim': 'sarcxregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avdlr
#                'avdeltaravdlr' : {'dim': 'sarcxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},# avdeltar avdlr
#                'betaavlr': {'dim': 'tranxregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avlr
#                'avdeltaravlr'  : {'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'},# avdeltar avlr
                'betaavsigmar': {'dim': 'tranxregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avsigmar
                'avdeltaravsigmar':{'dim':'tranxregs','dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # avdeltar avsigmar
                'betaavatr': {'dim': 'tranxregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avatr
                'avdeltaravatr':{'dim': 'tranxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # avdeltar avatr
                'betaavaer': {'dim': 'vedgexregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avaetaur
                'avdeltaravaer':{'dim': 'vedgexregs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # avdeltar avaer
                'betaavdmr': {'dim': 'varcxregxqs', 'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}, # beta avaetaur
                'avdeltaravdmr':{'dim': 'varcxregs',  'dom': pyomo.NonNegativeReals, 'Qtype': 'fin'}  # avdeltaravdmr
                }


    def __init__(self, netdata):
        """Specific attributes of the guarded net object"""
#        self.wu =  # Upper bound to linearize products of variables involving dl (it will be computed if not specified in the net)
#        self.wl =  # Lower bound to linearize products of variables involving dl  (it will be computed if not specified in the net)
#        self.W =   # Upper bound to linearize implication in guarded nets (it will be computed if not specified in the net)
        """Regions and partitions"""
        self.CDg = {} # Matrices C and D for guarded intensity handlers
        self.regs = {} # Dictionary of regions
        self.parts = {} # Dictionary of partitions
        self.regsin = {} # Sets of regions contained in other sets of regions
        self.regseq = {} # Sets of regions equal to other sets of regions
        self.sarcxguards = {} # Dictionary of sarcxguards
        self.placexregs = {} # Dictionary of placexregs
        self.tranxregs = {} # Dictionary of tranxregs
        self.varcxregs = {} # Dictionary of varcxregs
        self.vedgexregs = {} # Dictionary of vedgexregs
        self.sarcxregs = {} # Dictionary of sarcxregs
        self.sedgexregs = {} # Dictionary of sedgexregs
        self.sarcxguardxregs = {} # Dictionary of sarcxguardxregs
        self.regxqs = {} # Dictionary of sregxqs with qs ranging from 1 to q-1
        self.sarcxguardxqs = {} # Dictionary of sarcxguardxqs with qs ranging from 1 to q-1
        self.placexregxqs = {} # Dictionary of placexsregxqs with qs ranging from 1 to q-1
        self.tranxregxqs = {} # Dictionary of tranxsregxqs with qs ranging from 1 to q-1
        self.sedgexregxqs = {} # Dictionary of sedgexregxqs with qs ranging from 1 to q-1
        self.vedgexregxqs = {} # Dictionary of vedgexregxqs with qs ranging from 1 to q-1
        self.sarcxregxqs = {} # Dictionary of sarcxregxqs with qs ranging from 1 to q-1
        self.varcxregxqs = {} # Dictionary of varcxregxqs with qs ranging from 1 to q-1
        self.sarcxguardxregxqs = {} # Dictionary of sarcxguardxregxqs with qs ranging from 1 to q-1

        """Initialize common elements of unguarded nets plus guarded
        shandlers
        """
        FlexN.__init__(self, netdata)
        """Add particular net elements of guarded nets"""
        """note: sarcxguards are created by addshandler"""
        regs=netdata['regs'] if 'regs' in netdata else []
        parts=netdata['parts'] if 'parts' in netdata else []
        if regs:
            for re in regs:
                self.addreg(re, regs[re])
        if parts:
            for pa in parts:
                self.addpart(pa, parts[pa])
        for pl, re in itertools.product(self.places, self.regs):
            self.addplacexreg((pl,re))
        for tr, re in itertools.product(self.trans, self.regs):
            self.addtranxreg((tr,re))
        for va, re in itertools.product(self.varcs, self.regs):
            self.addvarcxreg((va[0],va[1],re))
        for ve, re in itertools.product(self.vedges, self.regs):
            self.addvedgexreg((ve[0],ve[1],re))
        for sa, re in itertools.product(self.sarcs, self.regs):
            self.addsarcxreg((sa[0],sa[1],re))
        for se, re in itertools.product(self.sedges, self.regs):
            self.addsedgexreg((se[0],se[1],re))
        for sag, re in itertools.product(self.sarcxguards, self.regs):
            self.addsarcxguardxreg((sag[0],sag[1],sag[2],re))
        self.compds() # ds intervals [0,d1,..,dq-1,dq] to linearize products
        rangds = range(1,len(self.ds)-1)
        for re, d in itertools.product(self.regs, rangds):
            self.addregxq((re,d))
        for sag, d in itertools.product(self.sarcxguards, rangds):
            self.addsarcxguardxq((sag[0],sag[1],sag[2],d))
        for pl,re,d in itertools.product(self.places, self.regs, rangds):
            self.addplacexregxq((pl,re,d))
        for tr,re,d in itertools.product(self.trans, self.regs, rangds):
            self.addtranxregxq((tr,re,d))
        for se,re,d in itertools.product(self.sedges, self.regs, rangds):
            self.addsedgexregxq((se[0],se[1],re,d))
        for ve,re,d in itertools.product(self.vedges, self.regs, rangds):
            self.addvedgexregxq((ve[0],ve[1],re,d))
        for sa,re,d in itertools.product(self.sarcs, self.regs, rangds):
            self.addsarcxregxq((sa[0],sa[1],re,d))
        for va,re,d in itertools.product(self.varcs, self.regs, rangds):
            self.addvarcxregxq((va[0],va[1],re,d))
        for sag,re,d in itertools.product(self.sarcxguards, self.regs, rangds):
            self.addsarcxguardxregxq((sag[0],sag[1],sag[2],re,d))
        if self.sarcxguards == {}:
            raise ValueError("Building a guarded net without guarded intensity arcs. Use an unguarded net instead.")

                
    def compds(self):
        """Compute intervals [0,d1,..,dq-1,dq] to linearize products"""
        lamb = len(self.regs) # lambda of the exponential distribution
        q = self.options['dsspe']['q']
        if self.options['dsspe']['type'] == 'exp' and -log(1-(q-1)/q)/lamb >=1:
            print("Too many intervals for truncated exponential approximated " 
                "as exponential. Moving to uniform.")
            self.options['dsspe']['type'] = 'uni'
        if self.options['dsspe']['type'] == 'uni' or \
           (self.options['dsspe']['type'] == 'exp' and lamb == 2): 
            # An exponential with lamb=2 becomes a uniform
            self.ds = [0]+[j/q for j in range(1,q)]+[1]
        elif self.options['dsspe']['type'] == 'exp':
            self.ds = [0]+[-log(1-j/q)/lamb for j in range(1,q)]+[1]
        elif self.options['dsspe']['type'] == 'rand':
            if 'shf' in self.options['dsspe']:
                shf = self.options['dsspe']['shf']
            else:
                shf = 10.0  # Default shf
            mshift = 1/(shf*q) # Maximum shift
            self.ds = [0]+[j/q-mshift*random.random() for j in range(1,q)]+[1]
        elif self.options['dsspe']['type'] == 'shift':
            if 'shf' in self.options['dsspe']:
                shf = self.options['dsspe']['shf']
            else:
                shf = 50.0  # Default shf
            shift = 1/(shf*q)
            self.ds = [0]+[j/q-shift for j in range(1,q)]+[1]
        else:
            raise ValueError("The only allowed types of dsspe are: "
                "exp, uni, rand and shift")
                
    def addreg(self, rename, SQrows, **kwargs):
        """Create a region with name rename, polytope given by poly
           and optional attributes.
           SQrows is a list of dictionaries, each dictionary corresponding to a row
           of matrices SQ. The keys of the dictionaries are: SQ (matrix SQ at the 
           left of the expression), op (operator) and tind (constant value at the 
           right of the expression). op can only be either <= or >="""
        self.regs[rename] = netel.Reg(rename)
        self.regs[rename].SQrows = SQrows
        for key in kwargs:
            setattr(self.regs[rename], key, kwargs[key])
                
    def addpart(self, paname, regs, **kwargs):
        """Create a partition with name paname composed of list of regions regs
           and optional attributes"""
        self.parts[paname] = netel.Part(paname)
        self.parts[paname].regs = regs
        for key in kwargs:
            setattr(self.parts[paname], key, kwargs[key])

    def addsarcxguard(self, sagname, **kwargs): 
        """Create a sarcxguard (sarc,reg)  with name saname, region reg
           and optional attributes"""
        self.sarcxguards[sagname] = netel.Sarcxguard(sagname)
        for key in kwargs:
            setattr(self.sarcxguards[sagname], key, kwargs[key])

    def addplacexreg(self, plrename, **kwargs): 
        """Create a placexreg (pl,re)"""
        self.placexregs[plrename] = netel.Placexreg(plrename)
        for key in kwargs:
            setattr(self.placexregs[plrename], key, kwargs[key])

    def addtranxreg(self, trrename, **kwargs): 
        """Create a tranxreg (tr,re)"""
        self.tranxregs[trrename] = netel.Tranxreg(trrename)
        for key in kwargs:
            setattr(self.tranxregs[trrename], key, kwargs[key])

    def addvarcxreg(self, varename, **kwargs): 
        """Create a varcxreg (va,re)"""
        self.varcxregs[varename] = netel.Varcxreg(varename)
        for key in kwargs:
            setattr(self.varcxregs[varename], key, kwargs[key])

    def addvedgexreg(self, verename, **kwargs): 
        """Create a vedgexreg (ve,re)"""
        self.vedgexregs[verename] = netel.Vedgexreg(verename)
        for key in kwargs:
            setattr(self.vedgexregs[verename], key, kwargs[key])

    def addsarcxreg(self, sarename, **kwargs): 
        """Create a sarcxreg (sa,re)"""
        self.sarcxregs[sarename] = netel.Sarcxreg(sarename)
        for key in kwargs:
            setattr(self.sarcxregs[sarename], key, kwargs[key])

    def addsedgexreg(self, serename, **kwargs): 
        """Create a sedgexreg (se,re)"""
        self.sedgexregs[serename] = netel.Sedgexreg(serename)
        for key in kwargs:
            setattr(self.sedgexregs[serename], key, kwargs[key])

    def addsarcxguardxreg(self, sagrename, **kwargs): 
        """Create a sarcxguardxreg (sa, g, re)"""
        self.sarcxguardxregs[sagrename] = netel.Sarcxguardxreg(sagrename)
        for key in kwargs:
            setattr(self.sarcxguardxregs[sagrename], key, kwargs[key])

    def addregxq(self, regdname, **kwargs): 
        """Create a regxq (re, d)"""
        self.regxqs[regdname] = netel.Regxq(regdname)
        for key in kwargs:
            setattr(self.regxqs[regdname], key, kwargs[key])

    def addsarcxguardxq(self, sagdname, **kwargs): 
        """Create a sarcxguardxq (sa, g, d)"""
        self.sarcxguardxqs[sagdname] = netel.Sarcxguardxq(sagdname)
        for key in kwargs:
            setattr(self.sarcxguardxqs[sagdname], key, kwargs[key])

    def addplacexregxq(self, plredname, **kwargs): 
        """Create a placexregxq (pl, re, d)"""
        self.placexregxqs[plredname] = netel.Placexregxq(plredname)
        for key in kwargs:
            setattr(self.placexregxqs[plredname], key, kwargs[key])

    def addtranxregxq(self, trredname, **kwargs): 
        """Create a tranxregxq (tr, re, d)"""
        self.tranxregxqs[trredname] = netel.Tranxregxq(trredname)
        for key in kwargs:
            setattr(self.tranxregxqs[trredname], key, kwargs[key])

    def addsedgexregxq(self, seredname, **kwargs): 
        """Create a sedgexregxq (se, re, d)"""
        self.sedgexregxqs[seredname] = netel.Sedgexregxq(seredname)
        for key in kwargs:
            setattr(self.sedgexregxqs[seredname], key, kwargs[key])

    def addvedgexregxq(self, veredname, **kwargs): 
        """Create a vedgexregxq (ve, re, d)"""
        self.vedgexregxqs[veredname] = netel.Vedgexregxq(veredname)
        for key in kwargs:
            setattr(self.vedgexregxqs[veredname], key, kwargs[key])

    def addsarcxregxq(self, saredname, **kwargs): 
        """Create a sarcxregxq (sa, re, d)"""
        self.sarcxregxqs[saredname] = netel.Sarcxregxq(saredname)
        for key in kwargs:
            setattr(self.sarcxregxqs[saredname], key, kwargs[key])

    def addvarcxregxq(self, varedname, **kwargs): 
        """Create a varcxregxq (va, re, d)"""
        self.varcxregxqs[varedname] = netel.Varcxregxq(varedname)
        for key in kwargs:
            setattr(self.varcxregxqs[varedname], key, kwargs[key])

    def addsarcxguardxregxq(self, sagredname, **kwargs): 
        """Create a sarcxguardxregxq (sag, g, re, d)"""
        self.sarcxguardxregxqs[sagredname] = netel.Sarcxguardxregxq(sagredname)
        for key in kwargs:
            setattr(self.sarcxguardxregxqs[sagredname], key, kwargs[key])

    def optimun(self):
        """Optimize objective function objf for untimed constraints UGSENG"""
        ttic, tic = time.time(), time.clock()
        if not hasattr(self, 'wl'):
            self.computetindwl()
        if not hasattr(self, 'wu'):
            self.computetindwu()
        if not hasattr(self, 'W'):
            self.computetindW()
        self.info['perf']['Python processor time[wl,wu,W]'], self.info['perf']['Wall time[wl,wu,W]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        listcs = ['forceactf', 'forceexef', 'JpmmleqKpm', 'mbounds',
                  'meqmupYmmue', 'CdluleqDmue', 'dleqdeltadlu', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                  'SrxleqQrW1deltar', 'sumdeltareq1']
        UGSENGmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomun, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(UGSENGmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(UGSENGmodel, self.vdimdomun)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return UGSENGmodel
        else:
            raise ValueError('UGSENGmodel unbounded or infeasible')

    def optimst(self):
        """Optimize objective function objf for steady state constraints SCNG"""
        # F is not computed for steady state. It is only considered if given by the user        
        ttic, tic = time.time(), time.clock()
        if not hasattr(self, 'wl'):
            self.computestwl()
        if not hasattr(self, 'wu'):
            self.computestwu()
        if not hasattr(self, 'W'):
            self.computestW()
        self.info['perf']['Python processor time[wl,wu,W]'], self.info['perf']['Wall time[wl,wu,W]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        listcs = [
                  'forceactav', 'forceexeav', 'JpmavmleqKpm', 'avmbounds',
                  'avmeqavmupYmavmue', 'CavdluleqDavmue', 'avdleqavdeltaavdlg', 'avleql0Zlavdl', 'Jll0leqKl',
                  'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau', 'Jmm0leqKm', 'Jaa0leqKa', 
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
        SCNGmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomst, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(SCNGmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(SCNGmodel, self.vdimdomst)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return SCNGmodel
        else:
            raise ValueError('SCNGmodel unbounded or infeasible')

    def optimcst(self):
        """Optimize objective function objf for constant steady state (state at only one region) constraints SCNG"""
        # F is not computed for steady state. It is only considered if given by the user        
        ttic, tic = time.time(), time.clock()
        if not hasattr(self, 'wl'):
            self.computestwl()
        if not hasattr(self, 'wu'):
            self.computestwu()
        if not hasattr(self, 'W'):
            self.computestW()
        self.info['perf']['Python processor time[wl,wu,W]'], self.info['perf']['Wall time[wl,wu,W]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        listcs = [
                  'forceactav', 'forceexeav', 'JpmavmleqKpm', 'avmbounds',
                  'avmeqavmupYmavmue', 'CavdluleqDavmue', 'avdleqalphaavdlg', 'avleql0Zlavdl', 'Jll0leqKl',
                  'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau', 'Jmm0leqKm', 'Jaa0leqKa', 
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
        cSCNGmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomcst, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
        results = opt.solve(cSCNGmodel)
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(cSCNGmodel, self.vdimdomcst)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return cSCNGmodel
        else:
            raise ValueError('cSCNGmodel unbounded or infeasible')

    def optimtr(self):
        """Optimize objective function objf for transient state constraints TCNG"""
        ttic, tic = time.time(), time.clock()
        self.computetdepF()
        self.computeLU()
        self.info['perf']['Python processor time[L,U]'], self.info['perf']['Wall time[L,U]'] = time.clock()-tic, time.time()-ttic
        ttic, tic = time.time(), time.clock()
        if not hasattr(self, 'wl'):
            self.computetrwl()
        if not hasattr(self, 'wu'):
            self.computetrwu()
        if not hasattr(self, 'W'):
            self.computetrW()
        self.info['perf']['Python processor time[wl,wu,W]'], self.info['perf']['Wall time[wl,wu,W]'] = time.clock()-tic, time.time()-ttic
        tic = time.clock()
        listcs = [
                  'forceactf', 'forceactav', 'forceexef', 'forceexeav', 'JpmmleqKpm', 'mbounds', 'avmbounds', 
                  'meqmupYmmue', 'CdluleqDmue', 'dleqdeltadlu', 'leql0Zldl', 'Jll0leqKl',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
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
        TCNGmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomtr, obj=self.obj, extracons=self.extracons if hasattr(self,'extracons') else {})
        self.info['perf']['Python processor time[buildmodel]'] = time.clock()-tic
        ttic, tic = time.time(), time.clock()
        opt = SolverFactory(self.solver)
#        opt.options['NumericFocus'] = 3  # Gurobi parameter
        results = opt.solve(TCNGmodel, tee = False) # Use tee = True to display solver info
        self.info['perf']['Python processor time[optimize]'], self.info['perf']['Wall time[optimize]'] = time.clock()-tic, time.time()-ttic
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            tic = time.clock()
            self.info['result'] = results.json_repn()
            self.saveres(TCNGmodel, self.vdimdomtr)
            self.info['perf']['Python processor time[saveresult]'] = time.clock()-tic
            return TCNGmodel
        else:
            raise ValueError('TCNGmodel unbounded or infeasible')

    def computetindwl(self):
        """Compute time independent wl, i.e., lower bound for dlu, in the untimed setting. 
           wl is set to '-inf' if the problem is unbounded"""
        listcs = ['meqmupYmmue', 'CdluleqDmue', 'mbounds', 
                  'sigmaa0eqatYsae', 'AdmleqBae', 
                  'meqm0Zmdm', 'Jmm0leqKm']
        wlmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomun)
        auxwl = -1 # Force wl to be at most -1
        opt = SolverFactory(self.solver)    
        for sag in self.sarcxguards:
            if auxwl > -float('inf'):
                wlmodel.obj = pyomo.Objective(expr=wlmodel.dlu[sag], sense=pyomo.minimize)
                results = opt.solve(wlmodel)
                # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    auxwl = min(auxwl, wlmodel.obj.expr())                
                else:
                    auxwl = -float('inf')
                    warnings.warn("Warning: wl set to -inf")
                wlmodel.del_component('obj')
        self.wl = self.options['scalebs']*auxwl

    def computetindwu(self):
        """Compute time independent wu, i.e., upper bound for dlu, in the untimed setting. 
           wu is set to 'inf' if the problem is unbounded"""
        listcs = ['meqmupYmmue', 'CdluleqDmue', 'mbounds', 
                  'sigmaa0eqatYsae', 'AdmleqBae', 
                  'meqm0Zmdm', 'Jmm0leqKm']
        wumodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomun)
        auxwu = 1 # Force wu to be at least 1
        opt = SolverFactory(self.solver)    
        for sag in self.sarcxguards:
            if auxwu < float('inf'):
                wumodel.obj = pyomo.Objective(expr=wumodel.dlu[sag], sense=pyomo.maximize)
                results = opt.solve(wumodel)
                # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    auxwu = max(auxwu, wumodel.obj.expr())                
                else:
                    auxwu = float('inf')
                    warnings.warn("Warning: wu set to inf")
                wumodel.del_component('obj')
        self.wu = self.options['scalebs']*auxwu

    def computetrwl(self):
        """Compute auxiliary bound wl for transient state.
           wl is set to '-inf' if the problem is unbounded"""
        listcs = ['meqmupYmmue', 'CdluleqDmue', 'mbounds', 
                  'sigmaa0eqatYsae', 'AdmleqBae', 
                  'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                  'EcdsigmaeqthetaFc', 
                  'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 'Jll0leqKl']
        wlmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomtr)
        auxwl = -1 # Force wl to be at most -1
        opt = SolverFactory(self.solver)    
        for sag in self.sarcxguards:
            if auxwl > -float('inf'):
                wlmodel.obj = pyomo.Objective(expr=wlmodel.dlu[sag], sense=pyomo.minimize)
                results = opt.solve(wlmodel)
                # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
                    auxwl = min(auxwl, wlmodel.obj.expr())                
                else:
                    auxwl = -float('inf')
                    warnings.warn("Warning: wl set to -inf")
                wlmodel.del_component('obj')
        self.wl = self.options['scalebs']*auxwl

    def computetrwu(self):
        """Compute auxiliary bound wu for transient state.
           wu is set to 'inf' if the problem is unbounded"""
        listcs = [
                  'meqmupYmmue', 'CdluleqDmue', 'mbounds',
                  'sigmaa0eqatYsae', 'AdmleqBae', 
                  'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                  'EcdsigmaeqthetaFc', 
                  'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 'Jll0leqKl'
                  ]
        wumodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomtr)
        auxwu = 1 # Force wu to be at least 1
        opt = SolverFactory(self.solver)    
        for sag in self.sarcxguards:
            if auxwu < float('inf'):
                wumodel.obj = pyomo.Objective(
                    expr=wumodel.dlu[sag]
                         + sum(wumodel.m[pl] for pl in self.places)
                         + sum(wumodel.dsigma[sa] for sa in self.sarcs)
                         + sum(wumodel.sigma[tr] for tr in self.trans)
                         + sum(wumodel.dm[va] for va in self.varcs),
                    sense=pyomo.maximize)
                results = opt.solve(wumodel)
                # http://www.pyomo.org/blog/2015/1/8/accessing-solver
                if (results.solver.status == SolverStatus.ok
                    and results.solver.termination_condition == 
                        TerminationCondition.optimal):
                    auxwu = max(auxwu, wumodel.obj.expr())                
                else:
                    auxwu = float('inf')
                    warnings.warn("Warning: wu set to inf. "
                        "Have you included intensity arcs in E?")
                wumodel.del_component('obj')
        self.wu = self.options['scalebs']*auxwu
            
    def computestwl(self):
        """Compute auxiliary bound wl for steady state.
           wl is set to '-inf' if the problem is unbounded"""
        self.computetindwl()

    def computestwu(self):
        """Compute auxiliary bound wu for steady state.
           wu is set to 'inf' if the problem is unbounded"""
        self.computetindwu()
        wutind = self.wu 
        listcs = ['avmeqavmupYmavmue', 'CavdluleqDavmue', 'avleql0Zlavdl', 'Jll0leqKl', 'avmbounds',
                  'Zmavdmtaueq0',
                  'avdleleqwutind',
                  'avsigmataueqavl', 'avsigmataueqavattauYsigmaavaetau', 'AavdmtauleqBavaetau', 'Jmm0leqKm', 'Jaa0leqKa',
                  'sigmaa0eqatYsae', 'AdmleqBae', 'avmeqm0Zmdm'
                  ]
        wumodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomst)
        wumodel.obj = pyomo.Objective(expr=sum(wumodel.avm[pl] for pl in self.places)+
                                           sum(wumodel.avl[tr] for tr in self.trans)+
                                           sum(wumodel.avdmtau[va] for va in self.varcs), 
                                          sense=pyomo.maximize)
        opt = SolverFactory(self.solver)    
        results = opt.solve(wumodel)
        # http://www.pyomo.org/blog/2015/1/8/accessing-solver
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            self.wu = wutind+self.options['scalebs']*(wumodel.obj.expr())
        else:
            self.wu = float('inf')
            warnings.warn("Warning: wu set to inf")

    def computetindW(self):
        """Compute time independent W. W is set to 'inf' if the problem is unbounded"""
        listcs = ['meqmupYmmue', 'mbounds', 
                  'sigmaa0eqatYsae', 'AdmleqBae', 
                  'meqm0Zmdm', 'Jmm0leqKm']
        Wmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomun)
        opt = SolverFactory(self.solver)
        obj = 0
        for re in self.regs:
            for sqr in self.regs[re].SQrows:
                abssqr = sqr.replace('-','+').replace('<=','+').replace('>=','+')
                obj = obj+eval(abssqr, {var.name:getattr(Wmodel,var.name) for var in Wmodel.component_objects(pyomo.Var)})
        Wmodel.obj = pyomo.Objective(expr=obj, sense=pyomo.maximize)
        results = opt.solve(Wmodel)
        # http://www.pyomo.org/blog/2015/1/8/accessing-solver
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            self.W = self.options['scalebs']*Wmodel.obj.expr()
        else:
            self.W = float('inf')
            warnings.warn("Warning: W set to inf")


    def computetrW(self):
        """Compute auxiliary bound W for transient state. W is set to 'inf' if the problem is unbounded"""
        listcs = ['meqmupYmmue', 'mbounds',
                  'sigmaa0eqatYsae', 'AdmleqBae', 
                  'meqm0Zmdm', 'Jmm0leqKm', 'Jaa0leqKa',
                  'EcdsigmaeqthetaFc', 
                  'EdsigmaleqthetaF', 'sigmaeql0thetaZldsigma', 'Jll0leqKl']
        Wmodel = self.buildmodel(listcs=listcs, vdimdom=self.vdimdomtr)
        opt = SolverFactory(self.solver)    
        obj = 0
        for re in self.regs:
            for sqr in self.regs[re].SQrows:
                abssqr = sqr.replace('-','+').replace('<=','+').replace('>=','+')
                obj = obj+eval(abssqr, {var.name:getattr(Wmodel,var.name) for var in Wmodel.component_objects(pyomo.Var)})
        Wmodel.obj = pyomo.Objective(expr=obj, sense=pyomo.maximize)
        results = opt.solve(Wmodel)
        # http://www.pyomo.org/blog/2015/1/8/accessing-solver
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            self.W = self.options['scalebs']*Wmodel.obj.expr()
        else:
            self.W = float('inf')
            warnings.warn("Warning: W set to inf")

    def computestW(self):
        """Compute auxiliary bound W for steady state. W is set to 'inf' if the problem is unbounded"""
        self.computetindW()

