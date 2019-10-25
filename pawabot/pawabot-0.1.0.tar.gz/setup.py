# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['pawabot']

package_data = \
{'': ['*']}

install_requires = \
['ThePirateBay>=1.3,<2.0',
 'aria2p>=0.2.5,<0.3.0',
 'beautifulsoup4>=4.8,<5.0',
 'privibot>=0.1.0,<0.2.0',
 'python-telegram-bot==12.0.0b1',
 'requests>=2.22,<3.0',
 'sqlalchemy>=1.3,<2.0',
 'tomlkit>=0.5.5,<0.6.0']

entry_points = \
{'console_scripts': ['pawabot = pawabot.cli:main']}

setup_kwargs = {
    'name': 'pawabot',
    'version': '0.1.0',
    'description': 'A bot for many things: aria2 management, torrent sites crawling, media organization with filebot and plex.',
    'long_description': "# pawabot\nThe repository for my Telegram Bot.\n\nThis bot provides a command to search for torrents on the web, and let you select them for download.\nThere is a basic permission system allowing to manage multiple users for one bot.\n\nSoon you'll be able to use it as well with\n```\npip install pawabot\npawabot create-admin USERNAME ID\nBOT_TOKEN=tooookeeeen pawabot run\n```\n\n",
    'author': 'Timothée Mazzucotelli',
    'author_email': 'pawamoy@pm.me',
    'url': 'https://github.com/pawamoy/pawabot',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
