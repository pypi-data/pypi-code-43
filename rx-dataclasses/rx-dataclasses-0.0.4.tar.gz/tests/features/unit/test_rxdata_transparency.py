import pytest
import inspect


def excluding_keys_prefixed(d, prefixes):
    if isinstance(prefixes, str):
        prefixes = [prefixes,]

    return dict((k,v) for (k,v) in d.items() if not any(k.startswith(prefix) for prefix in prefixes))

def excluding_class_functions(d, prefixes=None):
    d = dict((k, v) for (k, v) in d.items() if not inspect.isfunction(v))
    if prefixes is not None:
        d = excluding_keys_prefixed(d, prefixes)

    return d

def excluding_bound_methods(d, prefixes=None):
    d = dict((k, v) for (k, v) in d.items() if not inspect.ismethod(v))
    if prefixes is not None:
        d = excluding_keys_prefixed(d, prefixes)
    return d

def excluding_methods(instance, prefixes=None):
    if isinstance(instance, type):
        excluder = excluding_class_functions
    else:
        excluder = excluding_bound_methods        

    return excluder(vars(instance), prefixes=prefixes)


def code_descriptor(code, descriptors=('co_filename', 'co_firstlineno', 'co_kwonlyargcount', 'co_name', 'co_names', 'co_varnames')):
    return tuple(getattr(code, descriptor) for descriptor in descriptors)

def codemap(instance):
    if isinstance(instance, type):
        _codemap = dict((k, code_descriptor(v.__code__)) for (k, v) in vars(instance).items() if inspect.isfunction(v))
    else:
        _codemap = dict((k, code_descriptor(v.__func__.__code__)) for (k, v) in vars(instance).items() if inspect.ismethod(v))
    return _codemap

def annotations(instance):
    if not isinstance(instance, type):
        instance = type(instance)

    return vars(instance)['__annotations__']


@pytest.mark.instances
@pytest.mark.equal
@pytest.mark.except_magic
def test_instances_are_equal_except_magic(prelast, last):
    '''f"attributes and methods of {last} is equivalent to {prelast} excluding magic"'''
    assert excluding_keys_prefixed(excluding_methods(last), '__') == excluding_keys_prefixed(excluding_methods(prelast), '__')
    assert excluding_keys_prefixed(codemap(last), '__') == excluding_keys_prefixed(codemap(prelast), '__')


@pytest.mark.instances
@pytest.mark.equal
@pytest.mark.exact
def test_instance_are_exact_equal(prelast, last):
    '''f"attributes and methods of {last} is equivalent to {prelast}"'''
    assert excluding_methods(last) == excluding_methods(prelast)
    assert excluding_keys_prefixed(codemap(last), ('__setattr__', '__delattr__')) == excluding_keys_prefixed(codemap(prelast), ('__setattr__', '__delattr__'))


@pytest.mark.instances
@pytest.mark.equal
@pytest.mark.annotations
def test_annotations_are_equal(prelast, last):
    '''f"annotations of {last} is equivalent to annotations {prelast}"'''
    assert annotations(last) == annotations(prelast)

@pytest.mark.functions
@pytest.mark.kwargs
@pytest.mark.conformant
def test_functions_kwargs_is_compatible(prelast, last):
    optional_args = lambda spec: set(spec.args[len(spec.defaults or []) - len(spec.args):])
    mandatory_kw = lambda spec: set(k for k in spec.kwonlyargs if not k in (spec.kwonlydefaults or []))

    _super = inspect.getfullargspec(prelast)
    _sub = inspect.getfullargspec(last)

    if _super.varkw or _sub.varkw:
        return

    if _super.varkw or _sub.varkw:
        return

    mandatory_kw_super = mandatory_kw(_super)
    mandatory_kw_sub = mandatory_kw(_sub)

    assert (optional_args(_super).issuperset(mandatory_kw_sub) 
        or set(_super.kwonlyargs).issuperset(mandatory_kw_sub)), \
    'Non defaulted keywords of replaced function must be defined in one of [kwargs, keyword only, non defaulted keyword] of replacement'


@pytest.mark.functions
@pytest.mark.args
@pytest.mark.conformant
def test_functions_args_is_compatible(prelast, last):
    _super = inspect.getfullargspec(prelast)
    _sub = inspect.getfullargspec(last)

    if _super.varargs or _sub.varargs:
        return
    
    mandatory = lambda spec: list(spec.args[:len(spec.args) - len(spec.defaults or [])])

    assert len(mandatory(_super)) <= len(mandatory(_sub))


@pytest.mark.functions
@pytest.mark.annotations
@pytest.mark.conformant
def test_functions_annotations_is_compatible(prelast, last):
    _super = inspect.getfullargspec(prelast).annotations
    _sub = inspect.getfullargspec(last).annotations

    if not (_super and _sub):
        return
    
    for name, annotation in _super.items():
        if name in _sub:
            assert annotation.issubclass(_sub[name])
