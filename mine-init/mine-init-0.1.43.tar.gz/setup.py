# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mine_init']

package_data = \
{'': ['*']}

install_requires = \
['packmaker==0.2.2']

entry_points = \
{'console_scripts': ['mine-init = mine_init:main']}

setup_kwargs = {
    'name': 'mine-init',
    'version': '0.1.43',
    'description': 'A docker friendly startup routine for Minecraft servers.',
    'long_description': '===========\n mine-init\n===========\n----------------------------------------------------------\n A docker friendly startup routine for Minecraft servers.\n----------------------------------------------------------\n\n|build-status| |coverage|\n\nMain Documentation\n==================\n\n`Main Index`_\n\n.. |build-status| image:: https://gitlab.routh.io/minecraft/tools/mine-init/badges/master/pipeline.svg\n    :target: https://gitlab.routh.io/minecraft/tools/mine-init/pipelines\n\n.. |coverage| image:: https://gitlab.routh.io/minecraft/tools/mine-init/badges/master/coverage.svg\n    :target: http://minecraft.pages.routh.io/tools/mine-init/reports/\n    :alt: Coverage status\n\n.. _Main Index: http://minecraft.pages.routh.io/tools/mine-init/\n',
    'author': 'Chris Routh',
    'author_email': 'chris@routh.io',
    'url': 'https://gitlab.routh.io/minecraft/tools/mine-init',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
