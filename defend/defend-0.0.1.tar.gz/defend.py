import os, time, functools

def debug(*targs, expect=None, istype=None, time_limit=None, verbose=False, active=False):
    cmark = u'\u2713'
    clres = '\033[0m'
    clred = '\033[31m'
    
    try: 
        if os.environ["DEBUG"] == '*': active = True
    except: pass

    def decorator(func):
        @functools.wraps(func)
        
        def test_expect(x):
            """ test if output value equals expected value """
            if expect:
                if x != expect: raise Exception(f'{clred}failed expectation: {x!r} does not match {expect!r}{clres}')
                if verbose: print(f'{cmark} {x!r} equals {expect!r}')
        
        def test_istype(x):
            """ test if output value is expected type """
            if istype:
                if type(x) != istype: raise Exception(f'{clred}failed assertion: {x!r} is not type {istype.__name__!r}{clres}')
                if verbose: print(f'{cmark} {x!r} is type {istype.__name__!r}')
        
        def test_limit(e):
            """ test if func elapsed time is under time limit """
            if time_limit:
                if float(e) > time_limit: raise Exception(f'{clred}failed limit: {func.__name__!r} took {e} limit is {time_limit}{clres}')
        
        def run_func(func, *args, **kwargs):
            t = time.time()
            x = func(*args, **kwargs)
            e = str(time.time() - t)[:12]

            test_expect(x)
            test_istype(x)
            test_limit(e)
            
            if verbose: print(f'elapsed: {e}\n')

        def wrapper(*args, **kwargs):
            if not active: return func(*args, **kwargs)
            
            afunc = f'{func.__name__}({", ".join([repr(a) for a in args])})'
            tfunc = f'{func.__name__}({", ".join([repr(a) for a in targs])})'
            
            if targs: 
                if verbose: print(f'{afunc} -> {tfunc}')
                run_func(func, *targs, **kwargs)
            else: 
                if verbose: print(f'{afunc}')
                run_func(func, *args, **kwargs)
            
            return
        return wrapper
    return decorator
