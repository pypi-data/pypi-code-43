# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['janusgraphy']

package_data = \
{'': ['*']}

install_requires = \
['gremlinpython==3.2.9']

setup_kwargs = {
    'name': 'janusgraphy',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Victor Marcelino',
    'author_email': 'victor.fmarcelino@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
