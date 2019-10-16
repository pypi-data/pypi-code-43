from ..db import filters
from . import keys as K

def filter_device(devices, field, filter):
    if hasattr(filter, "check"):
        checker = filter.check
    else:
        if hasattr(filter, "__call__"):
            checker = filter 
        else:        
            try:
                s, data = filter
            except (ValueError, TypeError):
                raise ValueError('filter must be a 2 tuple, a function or a Filter object got a %s'%type(filter))
                
            try:
                FilterClass = filters.filter_loockup[s]
            except KeyError:
                raise ValueError('Unknown filter %r'%s)
            else:
                checker = FilterClass(data).check    
    
    if isinstance(field, (int,str)):
        if field == "*":
            try:
                first_key = next(iter(devices))
            except StopIteration: # empty dictionary 
                return {}
            else:
                fields = [k for k,d in devices[first_key].items() if isinstance(d, dict)]  
                return _filter_fields(devices, fields, checker)
        else:
            return _filter_one_field(devices, field, checker)
    else:
        return _filter_fields(devices, field, checker)             

def _filter_one_field(devices, field, checker):
    return {k:d  for k,d in devices.items() if checker(d[field][K.VALUE])}

def _filter_fields(devices, fields, checker):
    return {k:d  for k,d in devices.items() if any(  checker(d[field][K.VALUE]) for field in fields )  }


    
