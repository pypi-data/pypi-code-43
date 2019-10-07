
# This file is based on magmax readchar as provided on github under the MIT license:
# https://github.com/magmax/python-readchar/blob/master/readchar/readchar.py
# In order to eliminate dependencies and to prevent any possibilities of tempering with critical code,
# the readchar code has been integrated into this project.
# It is a general weakness of open source software and sometimes a general weakness of package management
# infrastructures that critical packages could (in theory) be modified without notice. As reading data
# from STDIN is a very security sensitive task and used in programs running as user root
# the author of Console is integrating readchar into his package to enforce that no security problems can
# occur. As this way Console does no longer depend on non-Python modules and the author of Console can
# ensure the integrity of Console this way a bit better level of security is achieved.
# In the future this code will be kept in sync with magmax implementation.

# This file is based on this gist:
# http://code.activestate.com/recipes/134892/
# So real authors are DannyYoo and company.

import sys

if sys.platform.startswith('linux'):
    from .readchar_linux import readchar
elif sys.platform == 'darwin':
    from .readchar_linux import readchar
elif sys.platform in ('win32', 'cygwin'):
    from .readchar_windows import readchar
else:
    raise NotImplementedError('The platform %s is not supported yet' % sys.platform)

"""
# Note: This code does not work well. It has therefore been replaced by Console.readKey().

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1 + c2
    c3 = getchar()
    if ord(c3) != 0x33:
        return c1 + c2 + c3
    c4 = getchar()
    return c1 + c2 + c3 + c4
"""


















