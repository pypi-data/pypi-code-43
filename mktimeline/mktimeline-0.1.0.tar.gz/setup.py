# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['mktimeline',
 'mktimeline.console',
 'mktimeline.console.commands',
 'mktimeline.events',
 'mktimeline.templates',
 'mktimeline.timeline']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'cleo>=0.7.5,<0.8.0',
 'frontmatter>=3.0,<4.0',
 'jinja2>=2.10,<3.0',
 'markdown>=3.1,<4.0']

entry_points = \
{'console_scripts': ['mktimeline = mktimeline.console.application:main']}

setup_kwargs = {
    'name': 'mktimeline',
    'version': '0.1.0',
    'description': '',
    'long_description': '# mktimeline - a timeline tool\nA tool for creating interactive/visual timelines.\n',
    'author': 'John Duprey',
    'author_email': '297628+jduprey@users.noreply.github.com',
    'url': 'https://www.iduprey.com/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
