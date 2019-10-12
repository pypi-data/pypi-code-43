# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['z4_solver']
install_requires = \
['z3-solver>=4.8,<5.0']

setup_kwargs = {
    'name': 'z4-solver',
    'version': '2019.10.12.2',
    'description': 'z3++',
    'long_description': "z4\n============\n\n[z3](z3) with some improvements:\n* Change the right shift operation on `BitVec`'s to be logical instead of arithmetic\n* Add the `ByteVec` class\n\n[z3]: https://github.com/Z3Prover/z3\n",
    'author': 'Asger Hautop Drewsen',
    'author_email': 'asgerdrewsen@gmail.com',
    'url': 'https://github.com/Tyilo/z4',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
