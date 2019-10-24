# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['twerk', 'twerk.tests', 'twerk.views']

package_data = \
{'': ['*']}

install_requires = \
['bullet>=2.1.0,<3.0.0',
 'click>=7.0,<8.0',
 'datafiles>=0.5,<0.6',
 'ipdb>=0.12.2,<0.13.0',
 'minilog>=1.2.5,<2.0.0',
 'splinter>=0.11.0,<0.12.0',
 'webdriver_manager>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['twerk = twerk.cli:main', 'twerk-gui = twerk.gui:main']}

setup_kwargs = {
    'name': 'twerk',
    'version': '0.0.2',
    'description': 'Make Twitter work for humans by blocking fake accounts.',
    'long_description': '# Twerk\n\nThis is a Selenium-powered tool to browse Twitter and automatically block fake accounts.\n\nThis project was generated with [cookiecutter](https://github.com/audreyr/cookiecutter) using [jacebrowning/template-python](https://github.com/jacebrowning/template-python).\n\n[![Unix Build Status](https://img.shields.io/travis/jacebrowning/twerk/master.svg?label=unix)](https://travis-ci.org/jacebrowning/twerk)\n[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/twerk/master.svg?label=window)](https://ci.appveyor.com/project/jacebrowning/twerk)\n[![Coverage Status](https://img.shields.io/coveralls/jacebrowning/twerk/master.svg)](https://coveralls.io/r/jacebrowning/twerk)\n[![PyPI Version](https://img.shields.io/pypi/v/twerk.svg)](https://pypi.org/project/twerk)\n[![PyPI License](https://img.shields.io/pypi/l/twerk.svg)](https://pypi.org/project/twerk)\n\n# Setup\n\n## Requirements\n\n- Python 3.7+\n- Poetry\n\n# Usage\n\nInstall the project from source:\n\n```text\n$ git clone https://github.com/jacebrowning/twerk\n$ cd twerk\n$ poetry install\n```\n\nVerify browser automation is working:\n\n```\n$ poetry run twerk check --debug --browser=chrome\n$ poetry run twerk check --debug --browser=firefox\n```\n\n# Configuration\n\nThe `$TWITTER_USERNAME` and `$TWITTER_PASSWORD` environment variables can be set to avoid manually typing account credentials.\n\nMost commands accept a `--browser` option or you can set `$BROWSER` to avoid specifying this each time.\n\nThe `$TWITTER_SEED_USERNAME` can be set to override the default starting account when searching for fake accounts.\n\n---\n\n> **Disclaimer**: I am by no means responsible for any usage of this tool. Please consult the [full license](https://github.com/jacebrowning/twerk/blob/master/LICENSE.md) for details.\n',
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/twerk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
