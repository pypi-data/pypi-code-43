# FNFactory: returns the flexible net object corresponding to the dictionary
#             'netdata' in flexible net format
# optimize: optimizes a given flexible net object

# The above functions can be used as:
# model, net = optimize(netd) # model is the obtained programming problem
                              # net is the net object

# The results and the net object are saved in (name).xls and (name).pkl
# where (name) is the value of the key 'name' of the dictionary

# The above command is equivalent to the following two:
# net = FNFactory(netd) # Build net object
# model = net.optimize() # Optimize net and save results and net

from fnyzer import FlexN
from fnyzer import GFlexN
from fnyzer import LFlexN
from fnyzer import MFlexN

def FNFactory(netdata):
    if ('options' in netdata 
        and 'antype' in netdata['options'] 
        and netdata['options']['antype'] == 'mpc'):
        net = MFlexN(netdata)
    elif 'mappers' in netdata:
        net = LFlexN(netdata)
    else:
        if 'regs' in netdata:
            net = GFlexN(netdata)  
        else:
            net = FlexN(netdata)
    return net

def optimize(netdata):
    net = FNFactory(netdata)
    model = net.optimize()
    return model, net

