# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['doka',
 'doka.commands',
 'doka.kernel',
 'doka.kernel.actions',
 'doka.kernel.definition',
 'doka.kernel.repository',
 'doka.kernel.services',
 'doka.kernel.storage',
 'doka.plugins',
 'doka.plugins.nginx']

package_data = \
{'': ['*'],
 'doka': ['tests/*'],
 'doka.plugins.nginx': ['conf/*', 'templates/*']}

install_requires = \
['fire>=0.1.3,<0.2.0',
 'marshmallow>=2.19,<3.0',
 'python-dotenv>=0.10.3,<0.11.0',
 'pyyaml>=5.1,<6.0',
 'requests>=2.22,<3.0',
 'termcolor>=1.1,<2.0']

entry_points = \
{'console_scripts': ['doka = doka:main']}

setup_kwargs = {
    'name': 'doka',
    'version': '0.4.9',
    'description': '',
    'long_description': None,
    'author': 'axxil',
    'author_email': 'axxil@yandex.ru',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
