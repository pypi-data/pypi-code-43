# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['drf_viewset_profiler']

package_data = \
{'': ['*']}

install_requires = \
['Cython>=0.29.13,<0.30.0', 'line_profiler>=2.1,<3.0']

setup_kwargs = {
    'name': 'drf-viewset-profiler',
    'version': '0.1.0',
    'description': 'Lib to profile all methods from a viewset line by line',
    'long_description': None,
    'author': 'Frederico V Lima',
    'author_email': 'frederico.vieira@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fvlima/drf-viewset-profiler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
