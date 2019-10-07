import os, time, functools, traceback

def debug(*targs, expect=None, istype=None, time_limit=None, verbose=False, stack=False, active=False):
    cmark = u'\u2713'
    clres = '\033[0m'
    clred = '\033[31m'
    clblu = '\033[34m'
    cldgr = '\033[90m'
    clpur = '\033[35m'
    
    try: 
        if os.environ["DEBUG"] == '*': active = True
    except: pass

    def decorator(func):
        @functools.wraps(func)
        
        def test_expect(x):
            """ test if output value equals expected value """
            if expect:
                if x != expect: raise AssertionError(f'{clred}failed expectation: {x!r} does not match {expect!r}{clres}')
                if verbose: print(f'{cmark} {clblu}{x!r}{clres} equals {clblu}{expect!r}{clres}')
        
        def test_istype(x):
            """ test if output value is expected type """
            if istype:
                if type(x) != istype: raise AssertionError(f'{clred}failed assertion: {x!r} is not type {istype.__name__!r}{clres}')
                if verbose: print(f'{cmark} {clblu}{x!r}{clres} is type {clblu}{istype.__name__!r}{clres}')
        
        def test_limit(e):
            """ test if func elapsed time is under time limit """
            if time_limit:
                if float(e) > time_limit: raise Exception(f'{clred}failed limit: {func.__name__!r} took {e} limit is {time_limit}{clres}')
        
        def run_func(func, *args, **kwargs):
            if verbose: print(clpur, end='')
            t = time.time()
            x = func(*args, **kwargs)
            e = str(time.time() - t)[:12]
            if verbose: print(clres, end='')
            
            test_expect(x)
            test_istype(x)
            test_limit(e)
            
            if verbose: 
                print(f'elapsed: {clblu}{e}{clres}\n')
                print(clpur, end='')
                print( "".join([x for x in traceback.format_stack()[:-2]]) )
                print(clres, end='')
            
            return x

        def wrapper(*args, **kwargs):
            if not active: return func(*args, **kwargs)
            
            afunc = f'\n{clblu}{func.__name__}{clres}({", ".join([repr(a) for a in args])}){clres}'
            tfunc = f'{clblu}{func.__name__}{clres}({", ".join([repr(a) for a in targs])}){clres}'
            
            if targs: 
                if verbose: print(f'{afunc} -> {tfunc}')
                return run_func(func, *targs, **kwargs)
            else: 
                if verbose: print(f'{afunc}')
                return run_func(func, *args, **kwargs)
            
            return
        return wrapper
    return decorator
