# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['z4_solver']
install_requires = \
['z3-solver>=4.8,<5.0']

setup_kwargs = {
    'name': 'z4-solver',
    'version': '2019.10.12.1',
    'description': 'z3++',
    'long_description': None,
    'author': 'Asger Hautop Drewsen',
    'author_email': 'asgerdrewsen@gmail.com',
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
