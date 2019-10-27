# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colour_datasets',
 'colour_datasets.loaders',
 'colour_datasets.loaders.tests',
 'colour_datasets.records',
 'colour_datasets.records.tests',
 'colour_datasets.utilities',
 'colour_datasets.utilities.tests']

package_data = \
{'': ['*'],
 'colour_datasets': ['examples/*'],
 'colour_datasets.loaders.tests': ['resources/*'],
 'colour_datasets.utilities.tests': ['resources/*']}

install_requires = \
['cachetools', 'colour-science>=0.3.14,<0.4.0', 'tqdm', 'xlrd']

extras_require = \
{'development': ['biblib-simple',
                 'coverage',
                 'coveralls',
                 'flake8',
                 'invoke',
                 'mock',
                 'nose',
                 'pre-commit',
                 'pytest',
                 'restructuredtext-lint',
                 'sphinx',
                 'sphinx_rtd_theme',
                 'sphinxcontrib-bibtex',
                 'toml',
                 'twine',
                 'yapf==0.23'],
 'read-the-docs': ['mock', 'numpy', 'sphinxcontrib-bibtex']}

setup_kwargs = {
    'name': 'colour-datasets',
    'version': '0.1.0',
    'description': 'Colour science datasets for use with Colour',
    'long_description': 'Colour - Datasets\n=================\n\n.. start-badges\n\n|actions| |coveralls| |codacy| |version|\n\n.. |actions| image:: https://github.com/colour-science/colour-datasets/workflows/Continuous%20Integration/badge.svg\n    :target: https://github.com/colour-science/colour-datasets/actions\n    :alt: Develop Build Status\n.. |coveralls| image:: http://img.shields.io/coveralls/colour-science/colour-datasets/develop.svg?style=flat-square\n    :target: https://coveralls.io/r/colour-science/colour-datasets\n    :alt: Coverage Status\n.. |codacy| image:: https://img.shields.io/codacy/grade/984900e3a85e40239a0f8f633dd1ebcb/develop.svg?style=flat-square\n    :target: https://www.codacy.com/app/colour-science/colour-datasets\n    :alt: Code Grade\n.. |version| image:: https://img.shields.io/pypi/v/colour-datasets.svg?style=flat-square\n    :target: https://pypi.org/project/colour-datasets\n    :alt: Package Version\n\n.. end-badges\n\nColour science datasets for use with\n`Colour <https://github.com/colour-science/colour>`__ or any Python package\nmanipulating colours. The datasets are hosted in `Zenodo <https://zenodo.org>`__\nunder the\n`Colour Science - Datasets <https://zenodo.org/communities/colour-science-datasets/>`__\ncommunity.\n\nIt is open source and freely available under the\n`New BSD License <https://opensource.org/licenses/BSD-3-Clause>`__ terms.\n\n.. contents:: **Table of Contents**\n    :backlinks: none\n    :depth: 3\n\n.. sectnum::\n\nFeatures\n--------\n\n**Colour - Datasets** was created to overcome issues encountered frequently\nwhen trying to access or use colour science datasets:\n\n-   No straightforward ingestion path for dataset content.\n-   No simple loading mechanism for dataset content.\n-   Unavailability of the dataset, e.g. download url is down, dataset\n    content is passed directly from hand to hand.\n-   No information regarding the definitive origination of the dataset.\n\n**Colour - Datasets** offers all the above: it allows users to ingest and load\ncolour science datasets with a single function call. The datasets information\nis hosted on `Zenodo <https://zenodo.org/communities/colour-science-datasets/>`__\nwhere the record for a dataset typically contain:\n\n-   An *urls.txt* file describing the urls to source the dataset files from.\n-   A copy of those files in the eventuality where the source files are not\n    available or the content has changed without notice.\n-   Information about the authors, content and licensing.\n\nWhen no explicit licensing information is available, the dataset adopts the\n**Other (Not Open)** licensing scheme, implying that assessing usage conditions\nis at the sole discretion of the users.\n\nOnline\n------\n\n**Colour - Datasets** can be used online with\n`Google Colab <https://colab.research.google.com/notebook#fileId=1YwIfDTBVP3XUYJAyZVEDWj92DJCB0_3v&offline=true&sandboxMode=true>`__.\n\nInstallation\n------------\n\nPrimary Dependencies\n^^^^^^^^^^^^^^^^^^^^\n\n**Colour - Datasets** requires various dependencies in order to run:\n\n-  `Python >=2.7 <https://www.python.org/download/releases/>`__ or\n   `Python >=3.5 <https://www.python.org/download/releases/>`__\n-  `Colour Science <https://www.colour-science.org>`__\n-  `tqdm <https://tqdm.github.io/>`__\n-  `xlrd <https://xlrd.readthedocs.io/>`__\n\nPypi\n^^^^\n\nOnce the dependencies satisfied, **Colour - Datasets** can be installed from\nthe `Python Package Index <http://pypi.python.org/pypi/colour-datasets>`__ by\nissuing this command in a shell::\n\n\tpip install colour-datasets\n\nThe overall development dependencies are installed as follows::\n\n    pip install \'colour-datasets[development]\'\n\nUsage\n-----\n\nAPI\n^^^\n\nThe main reference for `Colour - Datasets <https://github.com/colour-science/colour-datasets>`__\nis the `Colour - Datasets Manual <https://colour-datasets.readthedocs.io/en/latest/manual.html>`__.\n\nExamples\n^^^^^^^^\n\nMost of the objects are available from the ``colour_datasets`` namespace:\n\n.. code-block:: python\n\n    >>> import colour_datasets\n\nThe available datasets are listed with the ``colour_datasets.datasets()``\ndefinition:\n\n.. code-block:: python\n\n    >>> print(colour_datasets.datasets())\n\n::\n\n    colour-science-datasets\n    =======================\n\n    Datasets : 16\n    Synced   : 1\n    URL      : https://zenodo.org/communities/colour-science-datasets/\n\n    Datasets\n    --------\n\n    [ ] 3269926 : Agfa IT8.7/2 Set\n    [ ] 3245883 : Camera Spectral Sensitivity Database\n    [ ] 3367463 : Constant Hue Loci Data\n    [ ] 3362536 : Constant Perceived-Hue Data\n    [ ] 3270903 : Corresponding-Colour Datasets\n    [ ] 3269920 : Forest Colors\n    [x] 3245875 : Labsphere SRS-99-020\n    [ ] 3269924 : Lumber Spectra\n    [ ] 3269918 : Munsell Colors Glossy (All) (Spectrofotometer Measured)\n    [ ] 3269916 : Munsell Colors Glossy (Spectrofotometer Measured)\n    [ ] 3269914 : Munsell Colors Matt (AOTF Measured)\n    [ ] 3269912 : Munsell Colors Matt (Spectrofotometer Measured)\n    [ ] 3245895 : New Color Specifications for ColorChecker SG and Classic Charts\n    [ ] 3252742 : Observer Function Database\n    [ ] 3269922 : Paper Spectra\n    [ ] 3372171 : RAW to ACES Utility Data\n\nA ticked checkbox means that the particular dataset has been synced locally.\nA dataset is loaded by using its unique number: *3245895*:\n\n.. code-block:: python\n\n    >>> print(colour_datasets.load(\'3245895\').keys())\n\n::\n\n    Pulling "New Color Specifications for ColorChecker SG and Classic Charts" record content...\n    Downloading "urls.txt" file: 8.19kB [00:01, 5.05kB/s]\n    Downloading "ColorChecker24_After_Nov2014.zip" file: 8.19kB [00:01, 6.52kB/s]\n    Downloading "ColorChecker24_Before_Nov2014.zip" file: 8.19kB [00:01, 7.66kB/s]\n    Downloading "ColorCheckerSG_After_Nov2014.zip" file: 8.19kB [00:01, 7.62kB/s]\n    Downloading "ColorCheckerSG_Before_Nov2014.zip" file: 8.19kB [00:00, 9.39kB/s]\n    Unpacking "/Users/kelsolaar/.colour-science/colour-datasets/3245895/dataset/ColorCheckerSG_Before_Nov2014.zip" archive...\n    Unpacking "/Users/kelsolaar/.colour-science/colour-datasets/3245895/dataset/ColorCheckerSG_After_Nov2014.zip" archive...\n    Unpacking "/Users/kelsolaar/.colour-science/colour-datasets/3245895/dataset/ColorChecker24_After_Nov2014.zip" archive...\n    Unpacking "/Users/kelsolaar/.colour-science/colour-datasets/3245895/dataset/ColorChecker24_Before_Nov2014.zip" archive...\n    odict_keys([\'ColorChecker24 - After November 2014\', \'ColorChecker24 - Before November 2014\', \'ColorCheckerSG - After November 2014\', \'ColorCheckerSG - Before November 2014\'])\n\nAlternatively, a dataset can be loaded by using its full title:\n*New Color Specifications for ColorChecker SG and Classic Charts*\n\n.. code-block:: python\n\n    >>> print(colour_datasets.load(\'3245895\').keys())\n    odict_keys([\'ColorChecker24 - After November 2014\', \'ColorChecker24 - Before November 2014\', \'ColorCheckerSG - After November 2014\', \'ColorCheckerSG - Before November 2014\'])\n\nContributing\n------------\n\nIf you would like to contribute to `Colour - Datasets <https://github.com/colour-science/colour-datasets>`__,\nplease refer to the following `Contributing <https://www.colour-science.org/contributing/>`__\nguide for `Colour <https://github.com/colour-science/colour>`__.\n\nBibliography\n------------\n\nThe bibliography is available in the repository in\n`BibTeX <https://github.com/colour-science/colour-datasets/blob/develop/BIBLIOGRAPHY.bib>`__\nformat.\n\nCode of Conduct\n---------------\n\nThe *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,\nis available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct/>`__ page.\n\nAbout\n-----\n\n| **Colour - Datasets** by Colour Developers\n| Copyright © 2019 – Colour Developers – `colour-science@googlegroups.com <colour-science@googlegroups.com>`__\n| This software is released under terms of New BSD License: https://opensource.org/licenses/BSD-3-Clause\n| `https://github.com/colour-science/colour-datasets <https://github.com/colour-science/colour-datasets>`__\n',
    'author': 'Colour Developers',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.colour-science.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
