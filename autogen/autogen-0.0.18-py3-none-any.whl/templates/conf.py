#!/usr/bin/env python

""" this is a generic conf.py that uses sensible defaults for most projects

add different or additional options to moreconf.py which is imported at the bottom of this file
"""
import sys
from os.path import join, basename
from datetime import datetime

try:
    import win32api
except:
    # windows only
    pass
from pipreqs import pipreqs
import importlib
from glob import glob
import os

#####################
# Project information
#####################

# author from username
try:
    # windows full name
    author = win32api.GetUserNameEx(3)
except:
    # gitlab CI full name of user that started the job
    author = os.environ.get("GITLAB_USER_NAME", "")

# project name from root folder
copyright = ", ".join([str(datetime.now().year), author])
root = os.path.abspath(join(__file__, os.pardir, os.pardir))
project = basename(root)

# version from first <version.py>.__version__
try:
    versionfiles = glob(f"{root}/**/version.py", recursive=True)
    sys.path.insert(0, os.path.abspath(os.path.join(versionfiles[0], os.pardir)))
    version = importlib.__import__("version").__version__
except:
    version = "latest"

########
# source
########

# mock all imports that are not installed so packages can be imported without errors
# e.g. a package that runs in a container may not have dependencies installed locally
imports = pipreqs.get_all_imports(root)
autodoc_mock_imports = [f for f in imports if importlib.util.find_spec(f) is None]

# concatenate docstrings for class and __init__
autoclass_content = 'both'

########
# layout
########

# same as python. better than the default theme.
html_theme = 'sphinx_rtd_theme'

# includes the todos in the docs
todo_include_todos = True

# use these for changing default layout e.g. adding comments using disqus
# templates_path = ['_templates']
# html_static_path = ['_static']

############
# extensions
############

extensions = [
    'sphinx.ext.autodoc',       # source code docstrings
    'sphinx.ext.intersphinx',   # links to other package docs
    'sphinx.ext.todo',          # enable todo_boxes
    'sphinx.ext.coverage',      # report docstring coverage
    'sphinx.ext.viewcode',      # links to source code
    'sphinx.ext.githubpages',   # minor changes to enable githubpages
    'nbsphinx'                  # insert views of jupyter notebooks in the docs
]
# maps links to docs for other packages
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# more config options can be added in moreconf.py
try:
    from .moreconf import *
except ModuleNotFoundError:
    pass