# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['ultrasnip']
install_requires = \
['Qt.py>=1.2,<2.0']

entry_points = \
{'console_scripts': ['ultrasnip = ultrasnip:main']}

setup_kwargs = {
    'name': 'ultrasnip',
    'version': '0.1.1',
    'description': 'A desktop snipping tool written in Qt for Python.',
    'long_description': None,
    'author': 'Dan Bradham',
    'author_email': 'danielbradham@gmail.com',
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*',
}


setup(**setup_kwargs)
