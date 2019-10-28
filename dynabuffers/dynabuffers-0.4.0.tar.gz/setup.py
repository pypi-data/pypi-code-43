# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dynabuffers',
 'dynabuffers.antlr',
 'dynabuffers.ast',
 'dynabuffers.ast.datatype']

package_data = \
{'': ['*'],
 'dynabuffers': ['api/*'],
 'dynabuffers.ast': ['annotation/*', 'structural/*']}

install_requires = \
['antlr4-python3-runtime>=4.7.2,<5.0.0']

entry_points = \
{'console_scripts': ['release = poetry_scripts:release',
                     'test_ci = poetry_scripts:test_ci']}

setup_kwargs = {
    'name': 'dynabuffers',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'leftshift one open source group',
    'author_email': 'devs@leftshift.one',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
