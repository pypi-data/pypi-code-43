'''
Python Extensions related to collections

Note, this is named collection to avoid conflict with python's built-in collections module

History:
04-05-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'

# python import
from collections import Iterable

# pylib import
# from dds_pylib.decorators.deprecated import deprecated


def multidim_list(dims):
    ''' Create a list, possibly of multiple dimensions

    @param dims tuple of the dimension definition. A list would also work
        Ex.
            (3, )  - one dimension list of 3 elements
            (3, 4) - two dimension list
            (n, y, ...z) -
    '''
    if dims:
        return [multidim_list(dims[1:]) for _ in xrange(dims[0])]


def flatten(i):
    ''' flatten an arbitrarily nested iterable
    '''
    for el in i:
        if isinstance(el, Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el


# @deprecated
def create_multidim_list(dims):
    ''' wrapper for better named multidim_list()

    @param - see multidim_list()
    '''
    return multidim_list(dims=dims)


if __name__ == '__main__':
    def test_flatten(l):
        f = list(flatten(l))
        print 'flatten: len={l} {coll}'.format(l=len(f), coll=f)

    # uncomment to see deprecation warning
    print 'n: 1 create_multidim_list {r}'.format(r=create_multidim_list((1,)))
    print ''

    def test(dim=None, l=None):
        if dim:
            l = multidim_list(dim)
        print 'multidim_list: {d}  {r}'.format(d=dim, r=l)
        print ""
        test_flatten(l=l)
        print ""

    test(dim=(1,))
    test(dim=(3, 4))
    test(dim=(4, 4, 2))

    # create a nested tuples and numbers
    from pprint import pprint
    l = (
        [
            (chr(i), chr(i - 32))
            for i in xrange(ord('a'), ord('z') + 1)
        ] + range(0, 9)
    )
    pprint(l)
    test(l=l)
