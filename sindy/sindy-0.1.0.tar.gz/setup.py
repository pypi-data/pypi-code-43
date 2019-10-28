# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['sindy']
install_requires = \
['sparsereg>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'sindy',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Markus Quade',
    'author_email': 'info@markusqua.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
