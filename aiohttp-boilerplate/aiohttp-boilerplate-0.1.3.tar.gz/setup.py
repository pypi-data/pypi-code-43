# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aiohttp_boilerplate',
 'aiohttp_boilerplate.auth',
 'aiohttp_boilerplate.bootstrap',
 'aiohttp_boilerplate.config',
 'aiohttp_boilerplate.dbpool',
 'aiohttp_boilerplate.log',
 'aiohttp_boilerplate.middleware',
 'aiohttp_boilerplate.models',
 'aiohttp_boilerplate.schemas',
 'aiohttp_boilerplate.sql',
 'aiohttp_boilerplate.test_utils',
 'aiohttp_boilerplate.views']

package_data = \
{'': ['*']}

install_requires = \
['Cython==0.29.12',
 'aiodns==2.0.0',
 'aiohttp==3.5.4',
 'async-timeout==3.0.1',
 'asyncpg==0.18.3',
 'attrs==19.1.0',
 'cchardet==2.1.4',
 'cffi==1.12.3',
 'chardet==3.0.4',
 'idna==2.8',
 'marshmallow==2.19.5',
 'multidict==4.5.2',
 'pycares==3.0.0',
 'pycparser==2.19',
 'pyjwt==1.7.1',
 'ujson==1.35',
 'uvloop==0.12.2',
 'yarl==1.3.0']

setup_kwargs = {
    'name': 'aiohttp-boilerplate',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Vladyslav Tarasenko',
    'author_email': 'vladka@webdevelop.pro',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
