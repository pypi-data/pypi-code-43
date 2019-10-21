# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_model_subscription', 'model_subscription']

package_data = \
{'': ['*']}

install_requires = \
['django-lifecycle>=0.3.0,<0.4.0']

extras_require = \
{':python_version >= "2.7" and python_version < "2.8" or python_version >= "3.4" and python_version < "3.5"': ['typing>=3.6,<4.0']}

setup_kwargs = {
    'name': 'django-model-subscription',
    'version': '0.0.4',
    'description': 'Subscription model for a django model instance.',
    'long_description': '# django-model-subscription\n',
    'author': 'Tonye Jack',
    'author_email': 'tonyejck@gmail.com',
    'url': 'https://github.com/jackton1/django-model-subscription',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
