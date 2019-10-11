# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': '.'}

packages = \
['cvbuilder',
 'cvbuilder.__syspatch__',
 'cvbuilder.__syspatch__.patched',
 'cvbuilder.__syspatch__.vendor',
 'cvbuilder.__syspatch__.vendor.colorama',
 'cvbuilder.__syspatch__.vendor.fire',
 'cvbuilder.__syspatch__.vendor.fire.console',
 'cvbuilder.__syspatch__.vendor.pexpect',
 'cvbuilder.__syspatch__.vendor.psutil',
 'cvbuilder.__syspatch__.vendor.tqdm']

package_data = \
{'': ['*'], 'cvbuilder': ['config/*']}

install_requires = \
['numpy>=1.17,<2.0', 'pip>=10.0.0', 'requests']

entry_points = \
{'console_scripts': ['cvbuilder = cvbuilder.cli:main']}

setup_kwargs = {
    'name': 'cvbuilder',
    'version': '0.2.36',
    'description': 'Package for building OpenCV 4.1.2 including Python 3 bindings from the official sources.',
    'long_description': "# OpenCV Hands-Free\n\n**Unofficial** OpenCV builder for Python.\n\nThis package aims at building OpenCV 4.1.2 with Python bindings from the official sources.\nIt provides a simple command line interface for starting the process of downloading the\nofficial sources, configuring the build dependencies, compiling and installing the resulting\nCV2 shared object within a virtual environment.\n\nIn contrast to [opencv-python](https://github.com/skvark/opencv-python) it will not provide any\nwheels and therefore the installation / build process will be by far slower (depending on the\nactual system performance).\n\n**IMPORTANT NOTE**\n\nDepending on the usage and system dependencies, the on-the-fly build output can\ncontain video and GUI functionality and the contrib package.\n\n\n## Features\n\n* builds against Python >= 3.6\n* runs and builds inside virtual environment\n* includes video support\n* supports OpenCV check (import, build information)\n* compiles with many flags enabled (which???)\n\n## Supported OS\n\n* Debian Jessie, Stretch\n* Ubuntu 18.04\n* LinuxMint 18.2\n* Manjaro\n* Arch\n* Raspbian 9 (Stretch)\n\n\n## Supported Python runtimes\n\n* CPython 3.6, 3.7\n* PyPy (not yet)\n\n**Note:** PyPy (7.1.1) is not supported yet due to missing path variables in module `sysconfig`.\n\n## Installation\n\n1. Use a Python's [virtual environment](https://docs.python.org/3/library/venv.html)\nor even better add the package via [poetry](https://github.com/sdispater/poetry): `poetry add cvbuilder`\n1. Follow instructions below\n\n\n## Usage\n\nAfter installing the package via `pip` / `pipenv` / `poetry`, you can manually invoke `cvbuilder` commands.\n\n### Install system dependencies\n\n```bash\ncvbuilder system --enable-gui --enable-video\n```\n\n### Download, configure, build, install\n\nThe `do-it-all` command is:\n\n```bash\ncvbuilder build\n```\n\nor if you already downloaded the source zip files in the default temporary\ndirectory or need to rerun the process in a clean way:\n\n```bash\ncvbuilder build --clean\n```\n\n\n## Custom\n\nIf you need to run the individual steps (i.e. for debugging) the following\ncommands are provided.\n\n### Download sources\n\n```bash\ncvbuilder download\n```\n\n### Generate make config\n\n```bash\ncvbuilder configure [--tmpdir XYZ]\n```\n\n### Compile\n\n```bash\ncvbuilder make\n```\n\n### Install\n\n```bash\ncvbuilder install\n```\n\n### Dump\n\n```bash\ncvbuilder dump\n```\n\n### Check\n\nYou can run the check command:\n\n```bash\ncvbuilder check\n``` \n\nin order to check whether the build process and installation worked.\n\n\n# Running OpenCV\n\nNow everything should be up and running and you should be able to work with OpenCV:\n\n1. Start a python REPL: `poetry run python`\n1. Import the CV package: `import cv2`\n1. Read [OpenCV documentation](http://docs.opencv.org/)\n",
    'author': 'Hannes Römer',
    'author_email': 'none@example.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
