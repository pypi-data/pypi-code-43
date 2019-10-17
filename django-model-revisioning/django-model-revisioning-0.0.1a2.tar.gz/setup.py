# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['model_revisioning',
 'model_revisioning.management',
 'model_revisioning.management.commands',
 'model_revisioning.templatetags']

package_data = \
{'': ['*'], 'model_revisioning': ['templates/model_revisioning/*']}

install_requires = \
['django>=2.2,<3.0']

setup_kwargs = {
    'name': 'django-model-revisioning',
    'version': '0.0.1a2',
    'description': 'Version control for django models.',
    'long_description': 'django-model-revisioning\n========================\n\nAdd history to your models - migrations compatible!\n\n.. image:: https://readthedocs.org/projects/django-model-revisioning/badge/?version=latest\n   :target: https://django-model-revisioning.readthedocs.io/\n   :alt: Documentation Status\n.. image:: https://travis-ci.org/valberg/django-model-revisioning.svg?branch=master\n   :target: https://travis-ci.org/valberg/django-model-revisioning\n   :alt: Build Status\n.. image:: https://codecov.io/gh/valberg/django-model-revisioning/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/valberg/django-model-revisioning\n   :alt: Code Coverage\n\nSupported versions\n------------------\n\n- Python 3.6, 3.7, (3.8 soon)\n- Django 2.2.x, 3.0.x\n\nCurrent state\n-------------\n\ndjango-model-revisioning is currently not production ready - we need more tests for that!\n\nYou can install the pre-release from PyPI though using::\n\n    $ pip install django-model-revisioning>=0.0.1-alpha\n',
    'author': 'Vidir Valberg Gudmundsson',
    'author_email': 'valberg@orn.li',
    'url': 'https://github.com/valberg/django-model-revisioning',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
