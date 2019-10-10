# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jiratag_commitizen',
 'jiratag_commitizen.commands',
 'jiratag_commitizen.cz',
 'jiratag_commitizen.cz.conventional_commits',
 'jiratag_commitizen.cz.jira']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'decli>=0.5.0,<0.6.0',
 'packaging>=19.0,<20.0',
 'questionary>=1.0,<2.0',
 'termcolor>=1.1,<2.0',
 'tomlkit>=0.5.3,<0.6.0']

entry_points = \
{'console_scripts': ['cz = jiratag_commitizen.cli:main']}

setup_kwargs = {
    'name': 'jiratag-commitizen',
    'version': '0.1.2',
    'description': 'Python commitizen client tool',
    'long_description': '====================\nJiratag Commitizen\n====================\n\nThis a simple project forked from https://Woile.github.io/commitizen/\nthat simply adds a step in the default conventional-commit pipeline to\nindicate the Jira Issue tag in order for the commit to include the link\nto the issue so that is quickly accessed from the Bitbucket commit log.\n\n-----------\n\n**Documentation**: https://Woile.github.io/commitizen/\n',
    'author': 'Santiago Fraire',
    'author_email': 'santiwilly@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cgutierrezpa/jiratag-commitizen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
