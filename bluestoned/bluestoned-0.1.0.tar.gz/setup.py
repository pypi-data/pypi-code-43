# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['bluestoned']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17,<2.0',
 'opencv-python>=4.1,<5.0',
 'tqdm>=4.36,<5.0',
 'verboselogs>=1.7,<2.0']

entry_points = \
{'console_scripts': ['bluestoned = bluestoned.main:cli']}

setup_kwargs = {
    'name': 'bluestoned',
    'version': '0.1.0',
    'description': 'find bluescreen chroma keys or other color rangers in video files and images using OpenCV',
    'long_description': None,
    'author': 'Nik Cubrilovic',
    'author_email': 'git@nikcub.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
