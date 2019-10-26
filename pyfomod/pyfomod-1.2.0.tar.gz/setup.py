# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['pyfomod']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4,<5']

setup_kwargs = {
    'name': 'pyfomod',
    'version': '1.2.0',
    'description': 'A high-level fomod library written in Python.',
    'long_description': '# pyfomod\n\n[![PyPi](https://img.shields.io/pypi/v/pyfomod.svg?style=flat-square&label=PyPI)](https://pypi.org/project/pyfomod/)\n![Python Versions](https://img.shields.io/pypi/pyversions/pyfomod.svg?style=flat-square&label=Python%20Versions)\n[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FGandaG%2Fpyfomod%2Fbadge%3Fref%3Dmaster&style=flat-square)](https://actions-badge.atrox.dev/GandaG/pyfomod/goto?ref=master)\n\n*A high-level fomod library written in Python.*\n\n> :warning: **Note**: This is a mature library with all planned features added and no known bugs - do not be alarmed by the lack of commits.\n\n*pyfomod* makes it easy to work on fomod installers:\n\n- Pythonic data struture\n- Easy data extraction and modification\n- No need to deal with complex xml schemas or trial and error changes\n\n*pyfomod* automatically ignores any schema errors in an installer and corrects them\nwhen writing - you can fix most schema errors simply by parsing then writing the\ninstaller with *pyfomod*.\n\n## Installation\n\nTo install *pyfomod*, use pip:\n\n    pip install pyfomod\n\n## Quick Examples\n\nUse an existing installer:\n\n``` python\n>>> root = pyfomod.parse("path/to/package")\n```\n\nGet the installer metadata::\n\n``` python\n>>> root.name\n\'Example Name\'\n>>> root.author\n\'Example Author\'\n>>> root.description\n\'This is an example of metadata!\'\n>>> root.version\n\'1.0.0\'\n>>> root.website\n\'https://www.nexusmods.com/example/mods/1337\'\n```\n\nCreate a new installer:\n\n``` python\n>>> root = pyfomod.Root()\n```\n\nSave the installer:\n\n``` python\n>>> pyfomod.write(root, "path/to/package")\n```\n\n## Documentation\n\nFor more information check out *pyfomod*\'s documentation at [pyfomod.rtfd.io](https://pyfomod.rtfd.io)\n\n## Issues\n\nPlease use the [GitHub issue tracker](https://github.com/GandaG/pyfomod/issues)\nto submit bugs or request features.\n\n## What Is Fomod Anyway?\n\nFomod is a package format for mod installers. It\'s game-agnostic, meaning it\nworks on any game. It follows a specific package struture with a mandatory\nxml file in a subfolder that follows a specific xml schema and an optional\nxml file that does not. For more information visit the\n[fomod documentation](https://github.com/GandaG/fomod-docs).\n\n## Development\n\n*pyfomod* uses poetry to manage package versions:\n\n    path/to/python.exe -m pip install poetry\n    path/to/python.exe -m poetry install\n\nEnsure that everything is correct before committing:\n\n    path/to/python.exe -m poetry run check\n    path/to/python.exe -m poetry run test\n\nWhen you\'re done with a feature/fix, bump the version:\n\n    path/to/python.exe -m poetry run bump2version {major|minor|patch}\n\nTo finally publish to PYPI:\n\n    path/to/python.exe -m poetry publish --build -u $PYPI_USER -p $PYPI_PASS\n',
    'author': 'Daniel Nunes',
    'author_email': 'daniel.henri.nunes@gmail.com',
    'url': 'https://github.com/GandaG/pyfomod',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
