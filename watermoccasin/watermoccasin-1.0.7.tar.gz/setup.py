# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['watermoccasin']
install_requires = \
['algoliasearch>=1.17.0,<2.0.0',
 'certifi>=2019.6.16,<2020.0.0',
 'chardet>=3.0.4,<4.0.0',
 'future>=0.17.1,<0.18.0',
 'humanfriendly>=4.18,<5.0',
 'idna>=2.8,<3.0',
 'mutagen>=1.42.0,<2.0.0',
 'npr>=2.3.0,<3.0.0',
 'pydub>=0.23.1,<0.24.0',
 'requests>=2.22.0,<3.0.0',
 'urllib3>=1.25.3,<2.0.0']

entry_points = \
{'console_scripts': ['watermoccasin = watermoccasin:main']}

setup_kwargs = {
    'name': 'watermoccasin',
    'version': '1.0.7',
    'description': 'Convert a NPR ONE news feed for offline listening with options for speed up and timed playlist',
    'long_description': None,
    'author': 'Alex Reich',
    'author_email': 'watermoccasin@alexreich.com',
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
