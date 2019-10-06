# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dli_scrapping_lib', 'dli_scrapping_lib.scrap', 'dli_scrapping_lib.util']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.8,<5.0', 'pandas>=0.25.1,<0.26.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'dli-scrapping-lib',
    'version': '1.0.4',
    'description': 'Open Source Library of all the scrapping python utilities I have used over the years',
    'long_description': 'Personal Scrapping Library\n==========================\n\n.. image:: https://badge.fury.io/py/dli-scrapping-lib.svg\n    :target: https://badge.fury.io/py/dli-scrapping-lib\n\nVarious web scrapping functions I have written over the years.\n\nTo install \n\n.. code-block:: python\n\n  pip install dli-scrapping-lib\n',
    'author': 'dli',
    'author_email': 'davidli012345@gmail.com',
    'url': 'https://github.com/FriendlyUser/dli-scrapping-lib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
