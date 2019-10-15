name = 'photofind'

import sys

if sys.version_info[0] < 3:
    from photofind import *
else:
    from photofind.photofind import *
