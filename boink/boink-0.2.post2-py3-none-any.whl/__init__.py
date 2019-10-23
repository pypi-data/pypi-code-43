import os
import cppyy
from .initializor import initialize

__version__ = '0.2.2'


initialize('boink', 'libboinkCppyy.so', 'boink.map')
del initialize



from boink import boink as libboink
from boink.pythonizors.declarations import *
from cppyy import nullptr
