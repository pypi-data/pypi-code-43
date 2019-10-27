# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['plantuml2freemind']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.3.0,<20.0.0']

entry_points = \
{'console_scripts': ['plantuml2freemind = plantuml2freemind.cli:main']}

setup_kwargs = {
    'name': 'plantuml2freemind',
    'version': '0.3.0',
    'description': 'Converts plantuml mindmaps to freemind .mm files',
    'long_description': None,
    'author': 'Boger',
    'author_email': 'kotvberloge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
