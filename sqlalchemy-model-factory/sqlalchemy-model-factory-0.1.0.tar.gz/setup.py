# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['sqlalchemy_model_factory']

package_data = \
{'': ['*']}

install_requires = \
['sqlalchemy']

extras_require = \
{'docs': ['sphinx', 'm2r', 'sphinx_rtd_theme'], 'pytest': ['pytest>=1.0']}

entry_points = \
{'pytest11': ['model_manager = sqlalchemy_model_factory.pytest']}

setup_kwargs = {
    'name': 'sqlalchemy-model-factory',
    'version': '0.1.0',
    'description': 'A library to assist in generating models from a central location.',
    'long_description': None,
    'author': 'Dan Cardin',
    'author_email': 'ddcardin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
