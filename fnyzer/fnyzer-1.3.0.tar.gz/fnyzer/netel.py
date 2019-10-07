# Classes for the net elements
from copy import deepcopy

class Place:
    """Class for the places of the flexible net"""
    def __init__(self, name):
        self.name = name # Name of the place
        self.invh = [] # Input event handlers
        self.outvh = [] # Output event handlers
        self.consh = [] # Connected intensity handlers
        
class Transition:
    """Class for the transitions of the flexible net"""
    def __init__(self, name):
        self.name = name # Name of the transition
        self.convh = [] # Connected event handlers
        self.outsh = [] # Output intensity handlers
        self.insh = [] # Input intensity handlers        
        
class Vhandler:
    """Class for the event handlers of the flexible net"""
    def __init__(self, name, vhdata):
        self.name = name # Name of the event handler
        self.nickae = deepcopy(vhdata[0]) # Dictionary linking nicknames to arcs and edges
        self.ABk = deepcopy(vhdata[1:]) # Expressions associated to matrices Ak and Bk
        self.arcs = [] # List of nicknames of arcs
        self.edges = [] # List of nicknames of of edges
        self.cont = [] # Connected transitions
        self.inp = [] # Input places
        self.outp = [] # Output places

class Varc:
    """Class for the event arcs of the flexible net"""
    def __init__(self, name):
        self.name = name # Name of the event arc

class Vedge:
    """Class for the event edges of the flexible net"""
    def __init__(self, name):
        self.name = name # Name of the event edge
        
class Shandler:
    """Class for the intensity handlers of the flexible net"""
    def __init__(self, name, shdata):
        self.name = name # Name of the event handler
        self.nickae = deepcopy(shdata[0]) # Dictionary linking nicknames to arcs and edges
        self.CDk = deepcopy(shdata[1:]) # Expressions associated to matrices Ck and Dk
        self.arcs = [] # List of nicknames of arcs
        self.edges = [] # List of nicknames of of edges
        self.conp = [] # Connected places
        self.int = [] # Input transitions
        self.outt = [] # Output transitions

class Sarc:
    """Class for the intensity arcs of the flexible net"""
    def __init__(self, name):
        self.name = name # Name of the intensity arc
        self.phi = [] # Regions associated (only used by guarded intensity arcs)

class Sedge:
    """Class for the intensity edges of the flexible net"""
    def __init__(self, name):
        self.name = name # Name of the intensity edge
        
class Sarcxguard:
    """Class for the pairs (intensity arc, guard) of the guarded flexible net
       where guard is a region which is a guard of the intensity arc"""
    def __init__(self, name):
        self.name = name # Name of the pair
        
class Reg:
    """Class for the regions of the guarded flexible net"""
    def __init__(self, name):
        self.name = name # Name of the region
        
class Part:
    """Class for the partitions of the guarded flexible net"""
    def __init__(self, name):
        self.name = name # Name of the partition

class Placexreg:
    """Class for the pairs (place, region) of the guarded flexible net"""
    def __init__(self, name):
        self.name = name # Name of the pair

class Tranxreg:
    """Class for the pairs (transition, region) of the guarded flexible net"""
    def __init__(self, name):
        self.name = name # Name of the pair

class Varcxreg:
    """Class for the pairs (event arc, region) of the guarded flexible net"""
    def __init__(self, name):
        self.name = name 

class Vedgexreg:
    """Class for the pairs (event edge, region) of the guarded flexible net"""
    def __init__(self, name):
        self.name = name 

class Sarcxreg:
    """Class for the pairs (intensity arc, region) of the guarded flexible net"""
    def __init__(self, name):
        self.name = name 

class Sedgexreg:
    """Class for the pairs (intensity edge, region) of the guarded flexible net"""
    def __init__(self, name):
        self.name = name 

class Sarcxguardxreg:
    """Class for the trios (intensity arc, guard, region) of the guarded flexible net
       where guard is a region which is a guard of the intensity arc"""
    def __init__(self, name):
        self.name = name 

class Sarcxguardxq:
    """Class for the trios (intensity arc, guard, d) of the guarded flexible net
       where guard is a region which is a guard of the intensity arc and d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 

class Regxq:
    """Class for the pairs (region, d) of the guarded flexible net where d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 

class Placexregxq:
    """Class for the trio (place, region, d) of the guarded flexible net where d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 

class Tranxregxq:
    """Class for the trio (tran, region, d) of the guarded flexible net where d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 

class Sedgexregxq:
    """Class for the trio (sedge, region, d) of the guarded flexible net where d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 

class Vedgexregxq:
    """Class for the trio (vedge, region, d) of the guarded flexible net where d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 

class Sarcxregxq:
    """Class for the trio (sarc, region, d) of the guarded flexible net where d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 

class Varcxregxq:
    """Class for the trio (varc, region, d) of the guarded flexible net where d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 

class Sarcxguardxregxq:
    """Class for the tuple (sag, g, re, d) of the guarded flexible net where d is in [1,q-1]"""
    def __init__(self, name):
        self.name = name 
