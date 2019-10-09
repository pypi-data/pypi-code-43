# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['libflavour', 'libflavour.fields', 'libflavour.test']

package_data = \
{'': ['*'], 'libflavour.test': ['data/*']}

install_requires = \
['attrs', 'python-slugify', 'strictyaml']

setup_kwargs = {
    'name': 'libflavour',
    'version': '0.0.18',
    'description': '',
    'long_description': 'libflavour\n===========\n\nPython library to validate and load flavour YAML files for projects and addons.\n',
    'author': 'Dennis Schwertel',
    'author_email': 'dennisschwertel@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.5',
}


setup(**setup_kwargs)
