# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['arus',
 'arus.core',
 'arus.core.accelerometer',
 'arus.core.accelerometer.features',
 'arus.core.accelerometer.features.tests',
 'arus.core.accelerometer.tests',
 'arus.core.libs',
 'arus.core.libs.dsp',
 'arus.core.libs.dsp.tests',
 'arus.core.libs.mhealth_format',
 'arus.core.libs.mhealth_format.tests']

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
    'version': '0.2.6',
    'description': 'Activity Recognition with Ubiquitous Sensing',
    'long_description': '## Overview\n\n__arus__ python package provides a computation framework to manage and process ubiquitous sensory data for activity recognition.\n\n[![PyPI version](https://badge.fury.io/py/arus.svg)](https://badge.fury.io/py/arus)\n[![Downloads](https://pepy.tech/badge/arus)](https://pepy.tech/project/arus)\n[![Build Status](https://travis-ci.org/qutang/arus.svg?branch=master)](https://travis-ci.org/qutang/arus)\n[![codecov](https://codecov.io/gh/qutang/arus/branch/master/graph/badge.svg)](https://codecov.io/gh/qutang/arus)\n\n\n## Get started\n\n#### Prerequists\n\n```bash\npython >= 3.6\n```\n\n#### Installation\n\n```bash\n> pip install arus\n```\n\nor with `pipenv`\n\n```bash\n> pipenv install arus\n```\n\nor with `poetry`\n\n```bash\n> poetry add arus\n```\n\n### Plugins\n\n`arus` packages can be extended to involve more file types, Bluetooth devices or network protocols. The following list includes official plugins that extend `arus`.\n\n#### Official plugins\n\n1. [`arus-stream-metawear`](https://qutang.github.io/arus-stream-metawear/): a `Stream` class that can be used to stream data acquired from a Metawear device (A wireless Bluetooth sensor) in real-time.\n\n\n### Development\n\n#### Prerequists\n\n```bash\npython >= 3.6\npoetry >= 0.12.17\n```\n\n#### Set up development environment\n\n```bash\n> git clone https://github.com/qutang/arus.git\n> cd arus\n> poetry install\n```',
    'author': 'qutang',
    'author_email': 'tqshelly@gmail.com',
    'url': 'https://github.com/qutang/arus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
