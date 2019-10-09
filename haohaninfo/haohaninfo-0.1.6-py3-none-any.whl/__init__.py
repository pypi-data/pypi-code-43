from haohaninfo import GOrder
from haohaninfo import MicroPlay

import platform
bit = platform.architecture()[0]
if(bit == '32bit'):
    from haohaninfo import version
else:
    from haohaninfo import version64
