# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mercylog_bashlog', 'mercylog_bashlog.config', 'mercylog_bashlog.lib']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0']

setup_kwargs = {
    'name': 'mercylog-bashlog',
    'version': '0.2.0',
    'description': 'Datalog(Bashlog) Inspired Logic Programming in Python',
    'long_description': None,
    'author': 'Rajiv Abraham',
    'author_email': 'rajiv.abraham@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
