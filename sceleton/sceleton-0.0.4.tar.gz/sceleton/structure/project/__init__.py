import pkg_resources
import os

ENCODING = 'utf-8'

def sceleton(file):
    content_path = os.path.join('skeleton', file)
    content = pkg_resources.resource_string(__name__, content_path)
    return content.decode('utf-8').split("\n")

def licenses(file):
    content_path = os.path.join('licenses', file)
    content = pkg_resources.resource_string(__name__, content_path)
    return content.decode('utf-8')


from . import venv
from . import setup_py
from . import readme
from . import package
from . import git
from . import classifier
from . import license