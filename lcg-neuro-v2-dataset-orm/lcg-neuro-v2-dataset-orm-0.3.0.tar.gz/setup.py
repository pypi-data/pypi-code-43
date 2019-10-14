# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['v2_dataset', 'v2_dataset.model', 'v2_dataset.model.sorting', 'v2_dataset.orm']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'environ_config>=18.2,<19.0',
 'iso8601>=0.1.12,<0.2.0',
 'lcg-neuro-compneuro>=0.1.0,<0.2.0',
 'lcg-neuro-plx>=0.3.1,<0.4.0',
 'marshmallow>=2.19,<3.0',
 'numpy>=1.16,<2.0',
 'packaging>=19.2,<20.0',
 'pandas>=0.24.2,<0.25.0',
 'pedroasad-attrs-patch>=0.2.1,<0.3.0',
 'pint>=0.9.0,<0.10.0',
 'sqlalchemy>=1.3,<2.0',
 'stringcase>=1.2,<2.0',
 'tqdm>=4.32,<5.0']

setup_kwargs = {
    'name': 'lcg-neuro-v2-dataset-orm',
    'version': '0.3.0',
    'description': 'High resolution recordings in primate secondary visual cortex',
    'long_description': "# v2_dataset &ndash; Python object-relational mapping (ORM) and tools for the V2 Dataset\n\n[![][badge-python]][python-docs]\n[![][badge-version]][latest release]\n\n[![][badge-black]][Black]\n\n[![][badge-ci-status]][repository-master]\n![][badge-cov]\n\n- [Documentation](https://lcg.gitlab.io/neuro/v2/dataset/python-orm)\n- [Issue tracker](https://gitlab.com/lcg/neuro/v2/dataset/python-orm/issues)\n- [Repository contents](MANIFEST.md)\n- [History of changes](CHANGELOG.md)\n- [Contribution/development guide](CONTRIBUTING.md)\n\n---\n\nThis repository contains a [Python package][latest release] based on the [SQLAlchemy] object-relational mapping (ORM) framework for accessing the V2 Dataset's curated information.\nIt also contains a minimal [command-line interface](https://lcg.gitlab.io/neuro/v2/dataset/python-orm/cli.html) that supports the creation of [SQLite] databases to hold curated information and its manipulation through a set of [parsing routines](https://lcg.gitlab.io/neuro/v2/dataset/python-orm/api/v2_dataset.db.parsing.html) that are being continuously developed.\n\nThe curated information itself is stored in the [contents repository], together with information on how to obtain the recording data (which is not open-sourced, as of now).\nThe [contents repository] should be cloned *separately* and linked from your working copy, as explained below.\n\n## Installation and setup\n\nThe library may be installed with\n\n   ```bash\n   pip install lcg-neuro-v2-dataset-orm\n   ```\n\nAdditional steps:\n   \n1. Clone the V2 Dataset's [contents repository] to any directory on your computer, *e.g.*:\n\n   ```bash\n   git clone git@gitlab.com:lcg/neuro/v2/dataset/contents /data/v2-dataset\n   ```\n   \n   **Make sure** to check out a **compatible version** of the [contents repository].\n   Usually, the latest version of the library will be compatible with the latest version of the dataset.\n\n1. The library must be able to locate the dataset directory, which can be done in one of two ways:\n\n   * If Define a `V2_DATASET_DIR` environment variable pointing to the directory where you cloned the [contents repository] (you may do it with a `.envrc` file), or\n   * Create a symlink named `dataset` (it is Git-ignored in this repository) in your working copy or library installation directory (`/lib/pythonx.y/site-packages/lcg-neuro-v2-dataset-orm`) pointing to the [contents repository] copy.\n\n**Note:** You may need `g++` or `clang` to compile some dependent libraries's extensions.\n\n## Development notes\n\n### Git LFS and cloning\n\nCloning may take a while because we use [Git LFS] to track larger files that are included mainly for testing.\nAfter the initial cloning, further pushing/pulling/fetching should only take as long as needed to download missing files, which we intend to keep at a minimum over this project's lifetime.\n\n**Important:** you must install [Git LFS] before cloning.\n\n---\n\n*&mdash; Powered by [GitLab CI]*<br>\n*&mdash; Created by [Pedro Asad\n&lt;pasad@lcg.ufrj.br&gt;](mailto:pasad@lcg.ufrj.br) using [cookiecutter] and [@pedroasad.com/templates/python/python/app-1.0.0](https://gitlab.com/pedroasad.com/templates/python/python-app/tags/1.0.0)*  \n\n[Black]: https://pypi.org/project/black/\n[CHANGELOG]: ./CHANGELOG.md\n[CONTRIBUTING]: ./CONTRIBUTING.md\n[Git LFS]: https://git-lfs.github.com/\n[Gitlab CI]: https://docs.gitlab.com/ee/ci\n[LICENSE]: ./LICENSE.txt\n[MANIFEST]: ./MANIFEST.md\n[README]: https://gitlab.com/lcg/neuro/v2/dataset/python-orm/blob/master/README.md\n[SQLAlchemy]: https://www.sqlalchemy.org\n[SQLite]: https://www.sqlite.org\n[badge-black]: https://img.shields.io/badge/code%20style-Black-black.svg\n[badge-ci-coverage]: https://gitlab.com/lcg/neuro/v2/dataset/python-orm/badges/master/coverage.svg\n[badge-ci-status]: https://gitlab.com/lcg/neuro/v2/dataset/python-orm/badges/master/pipeline.svg\n[badge-cov]: https://gitlab.com/lcg/neuro/v2/dataset/python-orm/badges/master/coverage.svg\n[badge-python]: https://img.shields.io/badge/Python-%E2%89%A53.6-blue.svg\n[badge-version]: https://img.shields.io/badge/version-0.3.0%20-orange.svg\n[contents repository]: https://gitlab.com/lcg/neuro/v2/dataset/contents\n[cookiecutter]: http://cookiecutter.readthedocs.io/\n[latest release]: https://test.pypi.org/project/lcg-neuro-v2-dataset-orm/0.3.0/\n[python-docs]: https://docs.python.org/3.6\n[repository-codecov]: https://codecov.io/gl/lcg:neuro:v2:dataset/python-orm\n[repository-master]: https://gitlab.com/lcg/neuro/v2/dataset/python-orm\n[repository-security]: https://gitlab.com/lcg/neuro/v2/dataset/python-orm/security\n[repository]: https://gitlab.com/lcg/neuro/v2/dataset/python-orm\n",
    'author': 'Pedro Asad',
    'author_email': 'pasad@lcg.ufrj.br',
    'url': 'https://lcg.gitlab.io/neuro/v2/dataset/python-orm',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
