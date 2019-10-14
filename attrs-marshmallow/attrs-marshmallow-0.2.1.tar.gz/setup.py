# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['attrs_marshmallow']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0', 'marshmallow>=3.0', 'typing_inspect>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'attrs-marshmallow',
    'version': '0.2.1',
    'description': '',
    'long_description': None,
    'author': 'Igor Stuzhuk (KoHcoJlb)',
    'author_email': 'fujitsuigor@gmail.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
