'''
Python decorator for annotation

History:
06-01-2014 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'


def annotate(gen):
    ''' enumerate-like generator that skips ahead one; it returns -1 for
     the last element.

    Most usefully when needing to determine if the element is the last or not

    Example: use when generating SQL statements and you need to detect the
    last column to output a trailing ")"
    '''
    gen = iter(gen)
    prev_i, prev_val = 0, gen.next()
    for i, val in enumerate(gen, start=1):
        yield prev_i, prev_val
        prev_i, prev_val = i, val
    yield '-1', prev_val
