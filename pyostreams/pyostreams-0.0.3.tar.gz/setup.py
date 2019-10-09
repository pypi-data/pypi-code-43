#!/usr/bin/env python
from setuptools import setup, Extension



liboio = Extension('oio-streams',
					sources=[],
                    libraries=['oio-streams'])


setup(name='pyostreams',
      version = '0.0.3',
      description = 'Python interface to ciostreams .',
      author = 'Angelo Frangione',
      author_email = 'angelo.frangione@openio.io',
      license = 'GPL-v2.0',
      py_modules=['pyostreams'],
      install_requires = ['eventlet'],
      ext_modules = [liboio]
      )
