# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ghstar']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['ghstar = ghstar.ghstar:main']}

setup_kwargs = {
    'name': 'ghstar',
    'version': '0.2.0',
    'description': 'Star GitHub repos from the command line',
    'long_description': "# ghstar\n\nStar GitHub repos from the command line.\n\n```sh\n# set the environment variables GH_UNAME and GH_TOKEN\n# to your GitHub username and token/password\n\n$ ghstar gokulsoumya/ghstar\nStarred gokulsoumya/ghstar\n```\n\n(Because the command line is awesome, browsers are a hassle, and I'm lazy.)\n\n## Installation\n\n`ghstar` is written in Python3, available on PyPI and installable via pip:\n\n```\npip install ghstar\n```\n\n## Usage\n\nYou must first set the environment variables `GH_UNAME` and `GH_TOKEN` to\nyour GitHub username and token/password. It is recommended to use a\n[token](https://github.com/settings/tokens/new) with `public_repo` scope\ninstead of your password though either one works.\n\n```\n$ ghstar --help\n\nusage: ghstar [-h] [-i] [-n SEARCH_COUNT] repo\n\nStar GitHub repos from the command line.\n\npositional arguments:\n  repo                  name of repo to star\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -i, --interactive     search for a repo and star interactively\n  -n SEARCH_COUNT, --search-count SEARCH_COUNT\n                        number of search results to show when run\n                        interactively\n\nexamples:\n  ghstar gokulsoumya/ghstar\n  ghstar jlevy/the-art-of-command-line\n```\n\n## Contributing\n\nIf you have a feature request or if you've found a nasty lil bug, definitely\nopen an [issue](https://github.com/gokulsoumya/ghstar/issues). And PRs are,\nas always, welcome.\n",
    'author': 'Gokul',
    'author_email': 'gokulps15@gmail.com',
    'url': 'https://www.github.com/gokulsoumya/ghstar',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
