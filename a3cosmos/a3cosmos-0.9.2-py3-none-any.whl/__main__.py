

from __future__ import print_function # for Python<=2.X
#from __future__ import with_statement # for Python<=2.5
#from __future__ import nested_scopes # for Python<=2.1
#from pkg_resources import parse_version
from distutils.version import LooseVersion, StrictVersion
import os, sys, re
if sys.version_info.major>=3:
    import inspect
else:
    import funcsigs as inspect



# 
# import functions (keep these the same as in __init__.py)
# 
from .Software import module_find_source
from .Software import module_make_cutout




# 
# load all modules
# 
def load_all_modules():
    load_all_functions_in_one_module(module_find_source, r'^find_source', print_to_screen = False)
    load_all_functions_in_one_module(module_make_cutout, r'^make_cutout', print_to_screen = False)
    pass




# 
# test all modules
# 
def test_all_modules():
    load_all_modules()
    # 
    print('# ')
    print('# Testing find_source()')
    print('# ')
    find_source(RA = 150.1183756, Dec = 2.0027718)
    # 
    print('# ')
    print('# Testing make_cutout()')
    print('# ')
    make_cutout(RA = 150.1183756, Dec = 2.0027718, Band = 'Ks')




# 
# load and print all functions in one module
# 
def load_all_functions_in_one_module(t_module, func_name_pattern = '', print_to_screen = False):
    # get function list in the input t_module
    t_func_list = [ t_func_name \
                    for t_func_name in dir(t_module) \
                        if re.match(func_name_pattern, t_func_name, re.IGNORECASE) \
                            and hasattr(getattr(t_module, t_func_name), '__call__') ]
    # sort function names
    t_func_list.sort(key=LooseVersion)
    # prepare printing prefix
    t_print_prefix = '    '
    # get function name maximum string length
    t_func_nchar = 0
    for t_func_name in t_func_list:
        t_func_nchar = max([len(t_func_name), t_func_nchar])
    # loop function names and print function arguments
    for t_func_name in t_func_list:
        if print_to_screen == True:
            print(t_print_prefix, end='')
            print(('%%-%ds'%(t_func_nchar))%(t_func_name), end='')
        t_func_self = getattr(t_module,t_func_name)
        # 
        # The commented code below are for getting t_func_args without import inspect. The problem is len(t_func_defaults) != t_func_narg. 
        #if sys.version_info.major < 2 or (sys.version_info.major==2 and sys.version_info.minor<=5):
        #    t_func_narg = t_func_self.func_code.co_argcount
        #    t_func_args = t_func_self.func_code.co_varnames
        #    t_func_defaults = t_func_self.func_defaults
        #else:
        #    t_func_narg = t_func_self.__code__.co_argcount
        #    t_func_args = t_func_self.__code__.co_varnames
        #    t_func_defaults = t_func_self.__defaults__
        # 
        # Get t_func_args with inspect. Still has the problem that len(t_func_defaults) != t_func_narg. 
        #t_func_spec = inspect.getargspec(t_func_self) # inspect.getargspec() is deprecated since Python 3.0, use inspect.signature() or inspect.getfullargspec()
        #t_func_spec = inspect.getfullargspec(t_func_self)
        #t_func_narg = len(t_func_spec.args)
        #t_func_args = t_func_spec.args
        #t_func_defaults = t_func_spec.defaults
        # 
        # Loop function arguments and print
        #for t_func_iarg in range(t_func_narg):
        #    if t_func_iarg == 0: print('(', end='')
        #    else: print(', ', end='')
        #    print(t_func_args[t_func_iarg], end='')
        #    if t_func_defaults[t_func_iarg] != None:
        #        print(' = %s'%(t_func_defaults[t_func_iarg]), end='')
        #    print(')', end='')
        # 
        # Directly print str(inspect.signature()) is the new way
        if print_to_screen == True:
            print(' ', end='')
            print(str(inspect.signature(t_func_self)), end='')
            print('')
        # 
        # import
        #print('globals()['+t_func_name+']')
        #globals()[t_func_name] = t_func_self
        #locals()[t_func_name] = t_func_self
        module = sys.modules[__name__]
        #print(module)
        if not hasattr(module, t_func_name):
            #print('setattr(module, '+t_func_name+', t_func_self)')
            setattr(module, t_func_name, t_func_self)





# 
# list all functions
# 
def help():
    print('Hello:')
    print('    ')
    print('')
    print('Examples:')
    print('    import a3cosmos as a3c')
    print('    a3c.make_cutout(RA = 150.0, Dec = 2.0, FoV = 10, Band = \'Ks\') # This makes a UltraVISTA Ks cutout image with FoV 10 arcsec')
    print('    ')




# 
# main function
# 
if __name__ == '__main__':
    help()


