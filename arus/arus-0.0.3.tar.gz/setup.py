# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['arus',
 'arus.core',
 'arus.core.libs',
 'arus.core.libs.mhealth_format',
 'arus.core.libs.mhealth_format.tests',
 'arus.core.libs.signal_processing',
 'arus.core.libs.signal_processing.tests']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.1,<4.0',
 'numpy>=1.17,<2.0',
 'pandas>=0.25.1,<0.26.0',
 'pathos>=0.2.5,<0.3.0',
 'scipy>=1.3,<2.0']

setup_kwargs = {
    'name': 'arus',
    'version': '0.0.3',
    'description': 'Activity Recognition with Ubiquitous Sensing',
    'long_description': '## Overview\n\nARUS python package provides a set of functional APIs and classes to manage and process ubiquitous sensory data for activity recognition.\n\n## Get started\n\n### Prerequists\n\n```bash\npython >= 3.6\npipenv >= 2018.11.26\n```\n\n### Installation\n\n```bash\n> pip install git+https://github.com/qutang/arus.git#egg=arus\n```\n\nor with `pipenv`\n\n```bash\n> pipenv install git+https://github.com/qutang/arus.git#egg=arus\n```\n',
    'author': 'qutang',
    'author_email': 'tqshelly@gmail.com',
    'url': 'https://github.com/qutang/arus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
