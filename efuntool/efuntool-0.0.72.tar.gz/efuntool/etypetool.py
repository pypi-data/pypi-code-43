import re
import os
from efuntool.efuntool import dflt_kwargs
from efuntool.ebooltool import blor

def is_none(obj):
    if(type(obj)==type(None)):
        return(True)
    else:
        return(False)

def is_bool(obj):
    if(type(obj)==type(True)):
        return(True)
    else:
        return(False)

def is_bytes(obj):
    if(type(obj)==type(b'x')):
        return(True)
    else:
        return(False)

def is_str(obj):
    if(type(obj)==type('')):
        return(True)
    else:
        return(False)

def is_int(obj):
    if(type(obj)==type(0)):
        return(True)
    else:
        return(False)

def is_float(obj):
    if(type(obj)==type(0.0)):
        return(True)
    else:
        return(False)

def is_list(obj):
    if(type(obj)==type([])):
        return(True)
    else:
        return(False)

def is_tuple(obj):
    if(type(obj)==type(())):
        return(True)
    else:
        return(False)

def is_dict(obj):
    if(type(obj)==type({})):
        return(True)
    else:
        return(False)

def is_set(obj):
    if(type(obj)==type({1})):
        return(True)
    else:
        return(False)

def is_regex(obj):
    if(type(obj)==type(re.compile(""))):
        return(True)
    else:
        return(False)

def is_function(obj):
    if(is_non_buildin_function(obj)|is_buildin_function(obj)):
        return(True)
    else:
        return(False)

def is_module(obj):
    if(type(obj)==type(os)):
        return(True)
    else:
        return(False)

def is_type(obj):
    if(type(obj)==type(type)):
        return(True)
    else:
        return(False)


def is_other_type(obj):
    if(is_recursive_type(obj)|is_str(obj)|is_bool(obj)|is_none(obj)|is_number(obj)|is_function(obj)|is_type(obj)|is_module(obj)):
        return(False)
    else:
        return(True)

def parse_other(obj):
    regex = re.compile("<class '(.*)'>")
    t = type(obj)
    m = regex.search(str(t))
    rslt = m if(m==None) else m.group(1)
    return(rslt)


def is_number(obj):
    if(is_int(obj)|is_float(obj)):
        return(True)
    else:
        return(False)

def is_recursive_type(obj):
    #is_set(obj)
    #you cant add list/dict into set
    #you can also add tuple into set ,if the tuple has recusively dict/list
    if(is_list(obj)|is_tuple(obj)|is_dict(obj)):
        return(True)
    else:
        return(False)

def is_non_buildin_function(obj):
    def a_function():
        pass
    if(type(obj)==type(a_function)):
        return(True)
    else:
        return(False)

def is_buildin_function(obj):
    if(type(obj)==type(os.system)):
        return(True)
    else:
        return(False)

def is_hashable_type(obj):
    try:
        d = {obj:1}
    except:
        return(False)
    else:
        return(True)

def is_unhashable_type(obj):
    try:
        d = {obj:1}
    except:
        return(True)
    else:
        return(False)

def is_json(obj,strict=False):
    try:
        json.loads(obj,strict=strict)
    except:
        return(False)
    else:
        return(True)

def is_strize_free_jobj_leaf(obj):
    '''
         str(obj) could be parsed by ast, without strize
        >>> ast.parse(str(type))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/usr/lib/python3.6/ast.py", line 35, in parse
            return compile(source, filename, mode, PyCF_ONLY_AST)
          File "<unknown>", line 1
            <class 'type'>
            ^
        SyntaxError: invalid syntax
        >>>
        >>> ast.parse(str(False))
        <_ast.Module object at 0x7f976ac2acf8>
        >>>
    '''
    rslt = blor(
        is_none(obj),
        is_bool(obj),
        is_bytes(obj),
        is_str(obj),
        is_number(obj),
        is_regex(obj)
    )
    return(rslt)


_FUNCS = {
    "none":is_none,
    "bool":is_bool,
    "bytes":is_bytes,
    "str":is_str,
    "int":is_int,
    "float":is_float,
    "list":is_list,
    "tuple":is_tuple,
    "dict":is_dict,
    "set":is_set,
    "regex":is_regex,
    "function":is_function,
    "type":is_type,
    "module":is_module,
}


def get_type(obj,**kwargs):
    enable_parse_other = dflt_kwargs("parse_other",True,**kwargs)
    for k in _FUNCS:
        f = _FUNCS[k]
        if(f(obj)):
            return(k)
        else:
            pass
    if(enable_parse_other):
        return(parse_other(obj))
    else:
        return('other')

