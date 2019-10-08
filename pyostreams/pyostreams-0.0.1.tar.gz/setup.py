#!/usr/bin/env python
from setuptools import setup, Extension



hasher = Extension('pyostreams',
					sources=[],
                    libraries=['ciostreams'])


setup(name='pyostreams',
      version = '0.0.1',
      description = 'Python interface tociostreams .',
      author = 'Angelo Frangione',
      author_email = 'angelo.frangione@openio.io',
      license = 'GPL-v2.0',
      py_modules=['pyostreams'],
      install_requires = ['eventlet'],
      ext_modules = [hasher]
      )
