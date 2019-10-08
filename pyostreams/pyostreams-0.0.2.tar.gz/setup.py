#!/usr/bin/env python
from setuptools import setup, Extension



pyostreams = Extension('pyostreams',
					sources=[],
                    libraries=['ciostreams'])


setup(name='pyostreams',
      version = '0.0.2',
      description = 'Python interface to ciostreams .',
      author = 'Angelo Frangione',
      author_email = 'angelo.frangione@openio.io',
      license = 'GPL-v2.0',
      py_modules=['pyostreams'],
      install_requires = ['eventlet'],
      ext_modules = [pyostreams]
      )
