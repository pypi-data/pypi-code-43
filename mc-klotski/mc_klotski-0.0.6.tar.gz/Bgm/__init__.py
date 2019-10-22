__all__=['Bgm']

import sys
import os
sys.path.append('..')



def Get(name):
    return os.path.dirname(os.path.realpath(__file__))+"/"+name

