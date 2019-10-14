
from setuptools import setup
setup(**{'author': 'D-Nitro',
 'author_email': 'd-nitro@kpn.com',
 'classifiers': ['Development Status :: 3 - Alpha',
                 'Framework :: Django :: 2.1',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Internet :: WWW/HTTP'],
 'description': 'Katka Django core application',
 'include_package_data': True,
 'install_requires': ['Django<3.0,>=2.1',
                      'djangorestframework<4.0.0,>=3.9.0',
                      'django-encrypted-model-fields<1.0.0,>=0.5.8',
                      'drf-nested-routers'],
 'long_description': '# Katka core\n'
                     '\n'
                     'Django app which is be responsible for storing '
                     'information abouts applications and teams.\n'
                     '\n'
                     '## Clone\n'
                     'You can clone this repository on: '
                     'https://github.com/kpn/katka-core\n'
                     '\n'
                     '## Setup\n'
                     'Setup your environment:\n'
                     '\n'
                     '```shell\n'
                     '$ make venv\n'
                     '```\n'
                     '\n'
                     '## Stack\n'
                     '\n'
                     'Katka core is built on top of the Python framework '
                     'Django and the Django Rest\n'
                     'Framework to build APIs. Under the hood it runs Python '
                     '3.7.\n'
                     '\n'
                     '### Dependencies\n'
                     '* [djangorestframework](djangorestframework): django '
                     'toolkit for building Web APIs\n'
                     '* '
                     '[django-encrypted-model-fields](django-encrypted-model-fields): '
                     'save encrypted fields on DB\n'
                     '\n'
                     '[djangorestframework]: '
                     'https://github.com/encode/django-rest-framework\n'
                     '[django-encrypted-model-fields]: '
                     'https://gitlab.com/lansharkconsulting/django/django-encrypted-model-fields/\n'
                     '\n'
                     '## Contributing\n'
                     '\n'
                     '### Workflow\n'
                     '1. Fork this repository\n'
                     '2. Clone your fork\n'
                     '3. Create and test your changes\n'
                     '4. Create a pull-request\n'
                     '5. Wait for default reviewers to review and merge your '
                     'PR\n'
                     '\n'
                     '## Running tests\n'
                     'Tests are run on docker by executing\n'
                     '```shell\n'
                     '$ make test\n'
                     '```\n'
                     '\n'
                     'Or using venv\n'
                     '```shell\n'
                     '$ make test_local\n'
                     '```\n'
                     '\n'
                     '## Versioning\n'
                     '\n'
                     'We use SemVer 2 for versioning. For the versions '
                     'available, see the tags on this \n'
                     'repository.\n'
                     '\n'
                     '## Authors\n'
                     '* *KPN I&P D-Nitro* - d-nitro@kpn.com\n',
 'long_description_content_type': 'text/markdown',
 'name': 'katka-core',
 'packages': ['katka',
              'tests',
              'katka.migrations',
              'tests.utils',
              'tests.unit',
              'tests.unit.migrations'],
 'tests_require': ['tox'],
 'url': 'https://github.com/kpn/katka-core',
 'version': '0.24.0',
 'zip_safe': False})
