
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .advsleep import precision_sleep, interupt_sleep
from .save_load_object import save_to_file as save_object
from .save_load_object import load_from_file as load_object
from . import os
from . import traveling_salesman
from . import numerical
from . import threading
