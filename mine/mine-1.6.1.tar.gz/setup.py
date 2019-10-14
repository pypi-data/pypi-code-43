# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mine', 'mine.models', 'mine.tests']

package_data = \
{'': ['*'], 'mine.tests': ['files/*']}

install_requires = \
['YORM>=1.4,<2.0',
 'crayons>=0.1.2,<0.2.0',
 'minilog>=0.3,<0.4',
 'psutil>=2.1,<3.0']

entry_points = \
{'console_scripts': ['mine = mine.cli:main']}

setup_kwargs = {
    'name': 'mine',
    'version': '1.6.1',
    'description': 'Share application state across computers using Dropbox.',
    'long_description': "# Overview\n\nThis program lets you synchronize application data using Dropbox.\n\nIt automatically starts and stops programs that would otherwise fight over data in a shared folder and ensures only one instance is running.  Many applications work fine when their data is stored in Dropbox, but some programs overwrite databases:\n\n* iTunes\n* iPhoto\n* etc.\n\nwhile others periodically write snapshot data:\n\n* Eclipse\n* Xcode\n* etc.\n\nand some just don't make sense to keep running on all your computers:\n\n* Slack\n* HipChat\n* etc.\n\n[![Build Status](https://img.shields.io/travis/jacebrowning/mine/master.svg)](https://travis-ci.org/jacebrowning/mine)\n[![Coverage Status](https://img.shields.io/coveralls/jacebrowning/mine/master.svg)](https://coveralls.io/r/jacebrowning/mine)\n[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/jacebrowning/mine.svg)](https://scrutinizer-ci.com/g/jacebrowning/mine/?branch=master)\n[![PyPI Version](https://img.shields.io/pypi/v/mine.svg)](https://pypi.org/project/mine)\n\n# Setup\n\n## Requirements\n\n* Python 3.6+\n\n## Installation\n\nInstall mine with pip:\n\n```sh\n$ pip install mine\n```\n\nor directly from the source code:\n\n```sh\n$ git clone https://github.com/jacebrowning/mine.git\n$ cd mine\n$ python setup.py install\n```\n\n## Configuration\n\nCreate a `mine.yml` in your Dropbox:\n\n```yaml\nconfig:\n  computers:\n  - name: My iMac\n    hostname: My-iMac.local\n    address: 00:11:22:33:44:55\n  - name: My MacBook Air\n    hostname: My-MacBook-Air.local\n    address: AA:BB:CC:DD:EE:FF\n  applications:\n  - name: iTunes\n    properties:\n      auto_queue: false\n      single_instance: true\n    versions:\n      mac: iTunes.app\n      windows: iTunes.exe\n      linux: null\n  - name: Slack\n    properties:\n      auto_queue: true\n      single_instance: false\n    versions:\n      mac: Slack.app\n      windows: null\n      linux: null\n```\n\nInclude the applications you would like `mine` to manage. Computers are added automatically when `mine` is run.\n\nThe `versions` dictionary identifies the name of the executable on each platform. The `properties.auto_queue` setting indicates `mine` should attempt to launch the application automatically when switching computers. The `properties.single_instance` setting indicates the application must be closed on other computers before another instance can start.\n\n# Usage\n\nTo synchronize the current computer's state:\n\n```sh\n$ mine\n```\n\nTo close applications on remote computers and start them locally:\n\n```sh\n$ mine switch\n```\n\nTo close applications running locally:\n\n```sh\n$ mine close\n```\n\nTo close applications locally and start them on another computer:\n\n```sh\n$ mine switch <name>\n```\n\nTo delete conflicted files in your Dropbox:\n\n```sh\n$ mine clean\n```\n",
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/mine',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
