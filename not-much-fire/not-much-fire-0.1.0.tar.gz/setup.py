# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['not_much_fire']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'click>=7.0,<8.0',
 'dbus-python>=1.2,<2.0',
 'notify2>=0.3.1,<0.4.0',
 'notmuch>=0.29.1,<0.30.0']

entry_points = \
{'console_scripts': ['not-much-fire = not_much_fire.cli:main']}

setup_kwargs = {
    'name': 'not-much-fire',
    'version': '0.1.0',
    'description': 'A simple Notmuch notification tool',
    'long_description': None,
    'author': 'Thore Weilbier',
    'author_email': 'thore@weilbier.net',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
