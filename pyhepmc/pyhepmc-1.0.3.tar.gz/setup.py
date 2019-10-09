#! /usr/bin/env python

"""\
A simple wrapper on the main classes of the HepMC event simulation
representation, making it possible to create, read and manipulate HepMC events
from Python code.
"""

from __future__ import print_function
from distutils.core import setup, Extension
import os, sys

## Specify HepMC install dir
HEPMCINCPATH, HEPMCLIBPATH = None, None
if "HEPMCPATH" in os.environ:
    HEPMCINCPATH = os.path.join(os.environ["HEPMCPATH"], "include")
    HEPMCLIBPATH = os.path.join(os.environ["HEPMCPATH"], "lib")
if os.path.join("HEPMCINCPATH" in os.environ):
    HEPMCINCPATH = os.environ["HEPMCINCPATH"]
if os.path.join("HEPMCLIBPATH" in os.environ):
    HEPMCLIBPATH = os.environ["HEPMCLIBPATH"]
if HEPMCLIBPATH is None or HEPMCINCPATH is None:
    msg = """\
          WARNING: HepMC install path not specified via the HEPMCPATH
          (or HEPMCINCPATH & HEPMCLIBPATH) environment variables, e.g.
            HEPMCPATH=$HOME/local ./setup.py --prefix=$HOME/local
          Not building Python interface to C++ HepMC library
          """
    import textwrap
    print(textwrap.dedent(msg))
    # sys.exit(1)

## Pure Python package definition
kwargs = dict(name = 'pyhepmc',
              version = '1.0.3',
              py_modules = ['hepmcio'],
              scripts = ['mcgraph2', 'mcprint2', 'mc3d'],
              author = 'Andy Buckley',
              author_email = 'andy@insectnation.org',
              url = 'http://projects.hepforge.org/pyhepmc/',
              description = 'A Python interface to the HepMC high-energy physics event record API',
              long_description = __doc__,
              keywords = 'generator montecarlo simulation data hep physics particle',
              license = 'GPL')

## Extension definition
if HEPMCINCPATH:
    ext = Extension('_hepmcwrap', ['hepmc/hepmcwrap.i'],
                    swig_opts=['-c++', '-Iinclude', '-I'+HEPMCINCPATH],
                    include_dirs = [HEPMCINCPATH], library_dirs = [HEPMCLIBPATH], libraries = ['HepMC'])
    kwargs.update({"ext_package" : "hepmc",  "ext_modules" : [ext]})
    kwargs["py_modules"] += ['hepmc.__init__', 'hepmc.hepmcwrap']

## Run setup
setup(**kwargs)
