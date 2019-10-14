# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['keat_scripts', 'keats']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.2.1,<0.3.0',
 'poetry-setup>=0.3.6,<0.4.0',
 'termcolor>=1.1,<2.0',
 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['keats = keats:main']}

setup_kwargs = {
    'name': 'keats',
    'version': '0.2.27',
    'description': 'Utilities for managing version, changelogs, and project releases.',
    'long_description': '# Keats\n[![PyPI version](https://badge.fury.io/py/keats.svg)](https://badge.fury.io/py/keats)\n\n![John Keats](assets/keats.jpg)\n\nKeats is an Python build, installation, and workflow manager.\n\nFeatures include forced change logs, release scripts, and package version control.\n\n## Why\n\nEvery Python developer seems to have their own tricks and scripts for\nmaintaining changelogs, package versions, and managing releases. Rather\nthan reinventing the wheel everytime you develop a new pacakge, Keats\nprovides a standard workflow for doing python package releases. No\ncustomization or Makefiles are required.\n\n## Usage\n\nTo install **Keats** to your project, run:\n\n```bash\npoetry run add --dev keats\n```\n\nVerify your installation by running\n\n```bash\npoetry run keats keats\n```\n\nTo list documentation, run keats with no arguments\n\n```bash\npoetry run keats\n```\n\nTo begin version managment by creating a `__version__.py` in\nyour main package, run\n\n```bash\npoetry run keats version up\n```\n\nFrom within your python project, you can access your version number and\nother package information using something like (usually in the `__init__.py`\nof your main package).\n\n```python\nfrom .__version__.py import __version__, __title__, __authors__ # and so on\n```\n\nTo bump to the next version and update your change log (for more on change logs, see below)\n\n```\npoetry run keats bump\n```\n\nTo bump to a specific version:\n\n```\npoetry run keats bump <optional version>\n```\n\nTo bump without updating the change log:\n\n```bash\npoetry run keats version bump\n```\n\n\n**Changelogs**\n\nChangelogs are important understanding project status and developer intentions. \nKeats encourages an up-to-date changelog by providing an standard interface\nfor maintaining and updating change logs using the following files:\n\n* `.keats/changelog.json` - JSON formatted list of changes, with version number, dates, and optional change list.\n* `.keats/changelog.md` - markdown formatted changelog\n\nThe recommended way to use this is to run `keats bump` which will\nbump your package version *and* update your change log:\n\n```\npoetry run keats bump <optional version>\n```\n\nThis will provide an interactive script to update your changelog\nwith a description and a list of changes. Entries are appended to the\n`.keats/changelog.json` and saved. The file is then converted to a markdown\nfile for readability or documentation purposes.\n\nTo just update your change log:\n\n```bash\npoetry run keats changelog add\n```\n\nIf you want to just update the `.keats/changelog.md` from the json file,\nrun:\n\n```bash\npoetry run keats changelog up\n```\n\nTo clear your change logs:\n\n```bash\npoetry rubn keats changelog clear\n```\n\n## Global installation\n\nTo install **Keats** globally, run:\n\n```bash\npip install keats\n```\n\nYou can then run all of the commands without the `poetry run`\nprefix, given that your current directory is a Python project\nwith a `pyproject.toml` file.',
    'author': 'Justin Vrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://github.com/jvrana/keats',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
