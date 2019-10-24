import sys
import inspect

def get_fn_arg_names(fn):
    # This limits support to py36
    sig = inspect.signature(fn)
    return [param.name for param in sig.parameters.values() if param.kind == param.POSITIONAL_OR_KEYWORD]

def filter_dict(dict_to_filter, fn):
    filter_keys = get_fn_arg_names(fn)
    filtered_dict = {filter_key:dict_to_filter[filter_key] for filter_key in filter_keys}
    return filtered_dict

class IncrementalModuleError(Exception):
    pass

class IncrementalModuleLoader(object):
    def __init__(self):
        self.modules = dict()
        
    def update(self, **new_modules):
        """
        Add an injectable module to the list of modules, without any initialization.
        """
        self.modules.update(new_modules)
    
    def _create_module(self, mod):
        try:
            filtered_kwargs = filter_dict(self.modules, mod)
        except KeyError as e:
            raise IncrementalModuleError('Module %s is not loaded, but requested by %s.' % (str(e), mod))
        return mod(**filtered_kwargs)
    
    def load(self, _anonymous_mod=None, **new_modules):
        """
        Dynamically create the modules in arguments with the existing, already loaded
        modules.
        Params:
            _anonymous_mod: Positional argument. If the module is passed without a key,
                it will appear as an 'anonymous' module: the next modules loaded won't 
                have access to it in their dependencies.
            **new_modules: Load A SINGLE module with the current loaded modules as arguments
                and add it to the list of modules under the name specified with each key.
                For multiple modules, call this function once per module.
        Returns:
            The created module.
        """
        
        if _anonymous_mod is not None and new_modules:
            raise IncrementalModuleError('Either specify the positional module alone, or a single key=module pair.')
        elif _anonymous_mod is not None:
            # Return the anonymous module.
            return self._create_module(_anonymous_mod)
        elif new_modules:
            if len(new_modules) > 1:
                raise IncrementalModuleError('Only call load(key=module) with a single key=module pair.')
            # For loop, but we just checked there is only one key=value pair present.
            # This allows us to return the created module directly in loop.
            for mod_name, fn in new_modules.items():
                if mod_name in self.modules:
                    raise IncrementalModuleError('%s: duplicate module name' % mod_name)
                
                created_module = self._create_module(fn)
                self.modules[mod_name] = created_module
                return created_module