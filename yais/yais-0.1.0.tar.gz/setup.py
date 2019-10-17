# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['yais']
install_requires = \
['beautifulsoup4>=4.8.1,<5.0.0',
 'imagesize>=1.1.0,<2.0.0',
 'requests>=2.22.0,<3.0.0']

entry_points = \
{'console_scripts': ['yais = yais:cli']}

setup_kwargs = {
    'name': 'yais',
    'version': '0.1.0',
    'description': 'Yet Another Image Scraper',
    'long_description': '# yais\nYet Another Image Scraper\n',
    'author': 'Wu Haotian',
    'author_email': 'whtsky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/whtsky/yais',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
