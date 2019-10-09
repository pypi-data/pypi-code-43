# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['blender_asset_tracer',
 'blender_asset_tracer.blendfile',
 'blender_asset_tracer.cli',
 'blender_asset_tracer.pack',
 'blender_asset_tracer.pack.shaman',
 'blender_asset_tracer.trace']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.11,<3.0']

extras_require = \
{'s3': ['boto3>=1.9,<2.0']}

entry_points = \
{'console_scripts': ['bat = blender_asset_tracer.cli:cli_main']}

setup_kwargs = {
    'name': 'blender-asset-tracer',
    'version': '1.2.1',
    'description': 'BAT parses Blend files and produces dependency information. After installation run `bat --help`',
    'long_description': None,
    'author': 'Sybren A. Stüvel',
    'author_email': 'sybren@stuvel.eu',
    'url': 'https://developer.blender.org/project/profile/79/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
