# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['requests_asserts']
install_requires = \
['requests>=2.22,<3.0', 'responses>=0.10.6,<0.11.0']

setup_kwargs = {
    'name': 'requests-asserts',
    'version': '0.1.0',
    'description': 'The library to help test your HTTP requests using unittests',
    'long_description': None,
    'author': 'Adrian Dankiv',
    'author_email': 'adr-007@ukr.net',
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
