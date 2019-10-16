from . import keys as K
from ..io import ioconfig

#### ################################
#
# Function to load the devices yaml files. 
# So far all data information are found inside the xls sheet however to work 
# correctly more information about data fields are inside yaml file found in 
# the config directory. 
# The yaml files define the correspondance between xls column names and the more 
# python compatible name of data fields as well as the type of data found in each 
# columns.  
# 
#### ################################

###
# define some parser for the field types
FTYPE = 'ftype'
STR_CHOICE = 'str_choice'
INT = 'int'
STR = 'str'

_ftype_loockup = {}
def add_ftype(cls):
    _ftype_loockup[cls.ftype] = cls
def get_ftype(ftype):
    return _ftype_loockup[ftype]

class FType:
    ftype = ''
    def init_field(self, name, d):
        # just a copy
        field = dict(d)
        field[K.PARSER] = self.parse_value  
        field.setdefault(K.CHOICES, None)
        field[K.NAME] = name
        return field
        
    def parse_value(self, field, value):
        return value

##
# a str_choice is a choice of string. 
# the set of choices is expended when new data arrive inside the 'choices' keyword
# of the field property 
class StrChoice(FType):
    ftype = STR_CHOICE
    def init_field(self, name, d):        
        field = FType.init_field(self, name, d)
        field[K.CHOICES] = set()
        field[K.PARSER] = self.parse_value
        return field
    def parse_value(self, field, value):
        value = str(value)
        field[K.CHOICES].add(value)
        return value 
add_ftype(StrChoice)

##
# juste parse as str    
class Str(FType):
    ftype = STR
    def init_field(self, name,  d):
        field = FType.init_field(self, name, d)
        field[K.PARSER] = self.parse_value
        return field
    def parse_value(self, field, value):
        return str(value)
add_ftype(Str)
        
##
# 
class Int(FType):
    ftype = INT
    def init_field(self, name, d):
        field = FType.init_field(self, name, d)
        field[K.MIN] = 0
        field[K.MAX] = 0
        field[K.PARSER] = self.parse_value
        return field
    
    def parse_value(self, field, value):
        value = int(value)
        field[K.MIN] = min(field[K.MIN] , value)
        field[K.MAX] = max(field[K.MAX] , value)    
        return value
add_ftype(Int)

def load_device_conf(file_name):            
    conf_fields = ioconfig.load_yaml(file_name)
    fields = {}
    
    for k,d in conf_fields.items():
        ftype = d.get(FTYPE, 'str')
        d[FTYPE] = ftype
        ftype_cls = get_ftype(ftype)
        ftype_obj = ftype_cls()
        field = ftype_obj.init_field(k, d)
        fields[k] = field
    return fields
        
    