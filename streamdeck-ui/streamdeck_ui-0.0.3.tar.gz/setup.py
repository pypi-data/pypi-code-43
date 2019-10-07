# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['streamdeck_ui']

package_data = \
{'': ['*'], 'streamdeck_ui': ['fonts/roboto/*']}

install_requires = \
['hidapi>=0.7.99,<0.8.0',
 'pillow>=6.1,<7.0',
 'pynput>=1.4,<2.0',
 'pyside2>=5.13,<6.0',
 'streamdeck>=0.5.0,<0.6.0']

entry_points = \
{'console_scripts': ['streamdeck = streamdeck_ui.gui:start']}

setup_kwargs = {
    'name': 'streamdeck-ui',
    'version': '0.0.3',
    'description': 'A service, Web Interface, and UI for interacting with your computer using a Stream Deck',
    'long_description': '[![streamdeck_ui - Linux compatible UI for the Elgato Stream Deck](https://raw.githubusercontent.com/timothycrosley/streamdeck-ui/master/art/logo_large.png)](https://timothycrosley.github.io/streamdeck-ui/)\n_________________\n\n[![PyPI version](https://badge.fury.io/py/streamdeck_ui.svg)](http://badge.fury.io/py/streamdeck_ui)\n[![Build Status](https://travis-ci.org/timothycrosley/streamdeck_ui.svg?branch=master)](https://travis-ci.org/timothycrosley/streamdeck_ui)\n[![codecov](https://codecov.io/gh/timothycrosley/streamdeck_ui/branch/master/graph/badge.svg)](https://codecov.io/gh/timothycrosley/streamdeck_ui)\n[![Join the chat at https://gitter.im/timothycrosley/streamdeck_ui](https://badges.gitter.im/timothycrosley/streamdeck_ui.svg)](https://gitter.im/timothycrosley/streamdeck_ui?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/streamdeck_ui/)\n[![Downloads](https://pepy.tech/badge/streamdeck_ui)](https://pepy.tech/project/streamdeck_ui)\n_________________\n\n[Read Latest Documentation](https://timothycrosley.github.io/streamdeck_ui/) - [Browse GitHub Code Repository](https://github.com/timothycrosley/streamdeck_ui/)\n_________________\n\n**streamdeck_ui** A service, Web Interface, and UI for interacting with your computer using a Stream Deck\n',
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
