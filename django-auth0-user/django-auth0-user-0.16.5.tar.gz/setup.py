# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['django_auth0_user',
 'django_auth0_user.management',
 'django_auth0_user.management.commands',
 'django_auth0_user.migrations',
 'django_auth0_user.rest_framework',
 'django_auth0_user.templatetags',
 'django_auth0_user.util']

package_data = \
{'': ['*']}

install_requires = \
['cached-property>=1.5.1,<2.0.0',
 'social-auth-app-django>=3.1.0,<4.0.0',
 'social-auth-core[openidconnect]>=3.2.0,<4.0.0']

extras_require = \
{'auth0': ['auth0-python>=3.9.1,<4.0.0'],
 'drf': ['djangorestframework>=3.10.3,<4.0.0',
         'djangorestframework-jwt>=1.11.0,<2.0.0',
         'pyjwt>=1.7.1,<2.0.0']}

setup_kwargs = {
    'name': 'django-auth0-user',
    'version': '0.16.5',
    'description': 'Django Authentication and Authorisation using Auth0 and Python Social Auth',
    'long_description': None,
    'author': 'Samuel Bishop',
    'author_email': 'sam@techdragon.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/techdragon/django-auth0-user',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
