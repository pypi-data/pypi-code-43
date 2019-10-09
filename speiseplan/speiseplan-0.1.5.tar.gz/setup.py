# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['speiseplan']
install_requires = \
['requests_html>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['speiseplan = speiseplan:main']}

setup_kwargs = {
    'name': 'speiseplan',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'Markus Quade',
    'author_email': 'info@markusqua.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
