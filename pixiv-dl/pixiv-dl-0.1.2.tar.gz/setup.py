# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pixiv_dl']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=0.15.2,<0.16.0', 'pixivpy>=3.5.0,<4.0.0', 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['pixiv-dl = pixiv_dl.downloader:main']}

setup_kwargs = {
    'name': 'pixiv-dl',
    'version': '0.1.2',
    'description': 'A tool to download from pixiv',
    'long_description': "pixiv-dl\n========\n\nA simple tool to automatically download stuff from pixiv.\n\nUsage\n-----\n\n.. code-block::\n\n    usage: pixiv-dl [-h] [-u USERNAME] [-p PASSWORD] [-o OUTPUT] [--allow-r18]\n                    [--min-lewd-level MIN_LEWD_LEVEL]\n                    [--max-lewd-level MAX_LEWD_LEVEL] [--filter-tag FILTER_TAG]\n                    [--require-tag REQUIRE_TAG] [--min-bookmarks MIN_BOOKMARKS]\n                    [--max-bookmarks MAX_BOOKMARKS] [--max-pages MAX_PAGES]\n                    {bookmarks,following,mirror,tag} ...\n\n    A pixiv downloader tool. This can download your bookmarks, your following\n    feed, whole user accounts, etc.\n\n    positional arguments:\n      {bookmarks,following,mirror,tag}\n        bookmarks           Download bookmarks\n        following           Download all following\n        mirror              Mirror a user\n        tag                 Download works with a tag\n\n    optional arguments:\n      -h, --help            show this help message and exit\n      -u USERNAME, --username USERNAME\n                            Your pixiv username\n      -p PASSWORD, --password PASSWORD\n                            Your pixiv password\n      -o OUTPUT, --output OUTPUT\n                            The output directory for the command to run\n      --allow-r18           If R-18 works should also be downloaded\n      --min-lewd-level MIN_LEWD_LEVEL\n                            The minimum 'lewd level'\n      --max-lewd-level MAX_LEWD_LEVEL\n                            The maximum 'lewd level'\n      --filter-tag FILTER_TAG\n                            Ignore any illustrations with this tag\n      --require-tag REQUIRE_TAG\n                            Require illustrations to have this tag\n      --min-bookmarks MIN_BOOKMARKS\n                            Minimum number of bookmarks\n      --max-bookmarks MAX_BOOKMARKS\n                            Maximum number of bookmarks\n      --max-pages MAX_PAGES\n                            Maximum number of pages\n\n",
    'author': 'Laura F Dickinson',
    'author_email': 'l@veriny.tf',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Fuyukai/pixiv-dl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
