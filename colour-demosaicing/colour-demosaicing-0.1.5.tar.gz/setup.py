# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colour_demosaicing',
 'colour_demosaicing.bayer',
 'colour_demosaicing.bayer.demosaicing',
 'colour_demosaicing.bayer.demosaicing.tests',
 'colour_demosaicing.bayer.tests']

package_data = \
{'': ['*'],
 'colour_demosaicing': ['examples/*',
                        'resources/colour-demosaicing-examples-datasets/*',
                        'resources/colour-demosaicing-tests-datasets/*']}

install_requires = \
['colour-science>=0.3.14,<0.4.0']

extras_require = \
{'development': ['biblib-simple',
                 'coverage',
                 'coveralls',
                 'flake8',
                 'invoke',
                 'jupyter',
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
 'plotting': ['backports.functools_lru_cache', 'matplotlib'],
 'read-the-docs': ['mock', 'numpy', 'sphinxcontrib-bibtex']}

setup_kwargs = {
    'name': 'colour-demosaicing',
    'version': '0.1.5',
    'description': 'CFA (Colour Filter Array) Demosaicing Algorithms for Python',
    'long_description': "Colour - Demosaicing\n====================\n\n.. start-badges\n\n|actions| |coveralls| |codacy| |version|\n\n.. |actions| image:: https://github.com/colour-science/colour-demosaicing/workflows/Continuous%20Integration/badge.svg\n    :target: https://github.com/colour-science/colour-demosaicing/actions\n    :alt: Develop Build Status\n.. |coveralls| image:: http://img.shields.io/coveralls/colour-science/colour-demosaicing/develop.svg?style=flat-square\n    :target: https://coveralls.io/r/colour-science/colour-demosaicing\n    :alt: Coverage Status\n.. |codacy| image:: https://img.shields.io/codacy/grade/984900e3a85e40239a0f8f633dd1ebcb/develop.svg?style=flat-square\n    :target: https://www.codacy.com/app/colour-science/colour-demosaicing\n    :alt: Code Grade\n.. |version| image:: https://img.shields.io/pypi/v/colour-demosaicing.svg?style=flat-square\n    :target: https://pypi.org/project/colour-demosaicing\n    :alt: Package Version\n\n.. end-badges\n\nA `Python <https://www.python.org/>`__ package implementing various\nCFA (Colour Filter Array) demosaicing algorithms and related utilities.\n\nIt is open source and freely available under the\n`New BSD License <https://opensource.org/licenses/BSD-3-Clause>`__ terms.\n\n..  image:: https://raw.githubusercontent.com/colour-science/colour-demosaicing/master/docs/_static/Demosaicing_001.png\n\n.. contents:: **Table of Contents**\n    :backlinks: none\n    :depth: 3\n\n.. sectnum::\n\nFeatures\n--------\n\nThe following CFA (Colour Filter Array) demosaicing algorithms are implemented:\n\n-   Bilinear\n-   Malvar (2004)\n-   DDFAPD - Menon (2007)\n\nInstallation\n------------\n\nBecause of their size, the resources dependencies needed to run the various\nexamples and unit tests are not provided within the Pypi package. They are\nseparately available as\n`Git Submodules <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`__\nwhen cloning the\n`repository <https://github.com/colour-science/colour-demosaicing>`__.\n\nPrimary Dependencies\n^^^^^^^^^^^^^^^^^^^^\n\n**Colour - Demosaicing** requires various dependencies in order to run:\n\n-  `Python >= 2.7 <https://www.python.org/download/releases/>`__ or\n   `Python >= 3.5 <https://www.python.org/download/releases/>`__\n-  `Colour Science <https://www.colour-science.org>`__\n\nPypi\n^^^^\n\nOnce the dependencies satisfied, **Colour - Demosaicing** can be installed from\nthe `Python Package Index <http://pypi.python.org/pypi/colour-demosaicing>`__ by\nissuing this command in a shell::\n\n\tpip install colour-demosaicing\n\nThe overall development dependencies are installed as follows::\n\n    pip install 'colour-demosaicing[development]'\n\nUsage\n-----\n\nAPI\n^^^\n\nThe main reference for `Colour - Demosaicing <https://github.com/colour-science/colour-demosaicing>`__\nis the `Colour - Demosaicing Manual <https://colour-demosaicing.readthedocs.io/en/latest/manual.html>`__.\n\nExamples\n^^^^^^^^\n\nVarious usage examples are available from the\n`examples directory <https://github.com/colour-science/colour-demosaicing/tree/master/colour_demosaicing/examples>`__.\n\nContributing\n------------\n\nIf you would like to contribute to `Colour - Demosaicing <https://github.com/colour-science/colour-demosaicing>`__,\nplease refer to the following `Contributing <https://www.colour-science.org/contributing/>`__\nguide for `Colour <https://github.com/colour-science/colour>`__.\n\nBibliography\n------------\n\nThe bibliography is available in the repository in\n`BibTeX <https://github.com/colour-science/colour-demosaicing/blob/develop/BIBLIOGRAPHY.bib>`__\nformat.\n\nCode of Conduct\n---------------\n\nThe *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,\nis available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct/>`__ page.\n\nAbout\n-----\n\n| **Colour - Demosaicing** by Colour Developers\n| Copyright © 2015-2019 – Colour Developers – `colour-science@googlegroups.com <colour-science@googlegroups.com>`__\n| This software is released under terms of New BSD License: https://opensource.org/licenses/BSD-3-Clause\n| `https://github.com/colour-science/colour-demosaicing <https://github.com/colour-science/colour-demosaicing>`__\n",
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
