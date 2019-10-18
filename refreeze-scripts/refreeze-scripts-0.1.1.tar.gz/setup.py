# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['refreeze_scripts']

package_data = \
{'': ['*']}

install_requires = \
['setuptools>=41.4.0,<42.0.0', 'typing-extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['refreeze-scripts = refreeze_scripts.cli:main']}

setup_kwargs = {
    'name': 'refreeze-scripts',
    'version': '0.1.1',
    'description': '',
    'long_description': '# refreeze-scripts\n\nA *refreeze-scripts* refreeze EXE files in `Scripts` directory on Windows.\n\nIt extract a script part from [simple_launcer](https://bitbucket.org/vinay.sajip/simple_launcher/src/default/); which is used in pip internally to make `console_script` executable; EXE file and make it executable via `cli.exe` in setuptools.\n',
    'author': 'lambdalisue',
    'author_email': 'lambdalisue@fixpoint.co.jp',
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
