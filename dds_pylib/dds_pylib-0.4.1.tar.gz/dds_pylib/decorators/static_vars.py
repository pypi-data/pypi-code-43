'''
Python decorators for static variables

Usage:
@static_vars(counter=0)
def foo():
    foo.counter += 1
    print "Counter is %d" % foo.counter

History:
09-20-2018 - 1.0.0 - Stephen Funkhouser
    - Created
'''
__version__ = '1.0.0'

def static_vars(**kwargs):
    ''' static variable decorator
    '''
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate
