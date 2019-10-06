# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['thumbgen']

package_data = \
{'': ['*']}

install_requires = \
['PyGObject>=3.34,<4.0',
 'click>=7.0,<8.0',
 'loguru>=0.3.2,<0.4.0',
 'tqdm>=4.36,<5.0']

entry_points = \
{'console_scripts': ['fix = scripts:fix', 'thumbgen = thumbgen.thumbgen:main']}

setup_kwargs = {
    'name': 'thumbgen',
    'version': '0.1.1',
    'description': "Pre-generates thumbnails for 'Gnome Files' formerly known as nautilus.",
    'long_description': '# Thumbgen\n\nPre-generates thumbnails for \'Gnome Files\' formerly known as nautilus. This is useful if you have a lot of files which you want to glance over but you have to wait for them to load as you scroll.\nSupports **Python 3.5+** and any Linux distro using Gnome Desktop 3.\n\n## Basic Usage\n```\n# generating thumbnails for two directories\nthumbgen -d directory1/directory1_1 directory2\n\n# Pulling up the help\nthumbgen --help\n```\n\n## Command Line Options\n| short | long          | Description                                                                                         |\n|-------|---------------|-----------------------------------------------------------------------------------------------------|\n| -d    | --img_dirs    | directories to recursively generate thumbnails seperated by space, eg: "dir1/dir2 dir3"  [required] |\n| -w    | --workers     | no of cpus to use for processing                                                                    |\n| -i    | --only_images | Whether to only look for images to be thumbnailed                                                   |\n| -r    | --recursive   | Whether to recursively look for files                                                               |\n|       | --help        | CLI help                                                                                            |\n\n\n## Installation\n\nInstall PyGObject pre-requisites for your OS from [here](https://pygobject.readthedocs.io/en/latest/getting_started.html). For Ubuntu/Debian:\n\n```\nsudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0\n```\n\nThen install Thumbgen using:\n```\npip install thumbgen\n```\n',
    'author': 'Mudassir Khan',
    'author_email': 'mudassirkhan19@gmail.com',
    'url': 'https://github.com/difference-engine/thumbnail-generator-ubuntu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
