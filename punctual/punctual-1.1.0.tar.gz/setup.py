# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['punctual']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'colorama>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['pcl = punctual:cli.cli']}

setup_kwargs = {
    'name': 'punctual',
    'version': '1.1.0',
    'description': 'Clean and simple dotfile management with a lot of flexibility',
    'long_description': 'punctual\n========\n\n``punctual`` is an uncomplicated dotfile manager that works on common Linux fundamentals and simplistic JSON configuration files.\n\n\nInstallation\n------------\n\n\nFrom `PyPi <https://pypi.org/project/punctual/>`_, with pip::\n\n  pip install punctual\n\nWith this you will have an executable named ``pcl``.\n\n\nUsage\n-----\n\nMain::\n\n  $ pcl --help\n  Usage: pcl [OPTIONS] COMMAND [ARGS]...\n\n  Options:\n    --help  Show this message and exit.\n\n  Commands:\n    delete\n    install\n    list\n\nInstall::\n\n  $ pcl install --help\n  Usage: pcl install [OPTIONS] PACKAGE_NAME\n\n  Options:\n    --force  Remove any existing files\n    --help   Show this message and exit.\n\n\nDocumentation\n-------------\n\n`Available on ReadTheDocs! <https://punctual.readthedocs.io/>`_\n',
    'author': 'Mark Rawls',
    'author_email': 'markrawls96@gmail.com',
    'url': 'https://github.com/markrawls/punctual',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
