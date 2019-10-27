import __builtin__
import functools


def curry(x, argc=None):
    if argc is None:
        argc = x.func_code.co_argcount
    def p(*a):
        if len(a) == argc:
            return x(*a)
        def q(*b):
            return x(*(a + b))
        return curry(q, argc - len(a))
    return p


def pipe(*fs):
    def f(x):
        pipeline = reduce(lambda v, f: f(v), init=x)
        return pipeline(fs)
    return f


def reduce(fn, init=None):
    def f(xs):
        if init is not None:
            return functools.reduce(fn, xs, init)
        return functools.reduce(fn, xs)
    return f


@curry
def head(xs):
    return xs[0]


@curry
def tap(xs):
    print(xs)
    return xs


@curry
def map(fn, xs):
    try:
        _ = iter(xs)
    except TypeError:
        xs = []
    return __builtin__.map(fn, xs)


@curry
def prop(prop, props={}):
    return props.get(prop)


@curry
def equals(a, b):
    return a == b


@curry
def gt(a, b):
    return a > b


@curry
def notEquals(a, b):
    return complement(equals(a, b))
    

@curry
def complement(x):
    return not x


@curry
def ifElse(condition, onTrue, onFalse, xs):
    return onTrue(xs) if condition(xs) else onFalse(xs)


@curry
def any(f, xs):
    return __builtin__.any(f(x) for x in xs)


@curry
def all(f, xs):
    return __builtin__.all(f(x) for x in xs)


@curry
def fork(accumulator, condition, xs):
    """Process a collection into two collections.
    
    Args:
        accumulator (list): You're splitting a list into two, so your initial
            containers should be something like a 2 dimensional array.
        condition (function): Truth-y goes into 1st container and false-y
            goes into 2nd container.
        xs (list): original list
    
    Returns:
        (collection): collections within a collection
    """
    @curry
    def forker(condition, acc, x):
        print(x)
        if condition(x):
            acc[0].append(x)  
        else:
            acc[1].append(x)                
        return acc
    return reduce(forker(condition), accumulator)(xs)


@curry
def compliance(condition, xs):
    return fork(([],[]), condition, xs)


@curry
def elem(x, xs):
    return x in xs


@curry
def has(prop, props):
    try:
        _ = iter(props)
    except TypeError:
        props = {}
    return prop in props


@curry
def both(a, b, xs):
    return a(xs) and b(xs)
