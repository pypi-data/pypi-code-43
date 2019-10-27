# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colour_hdri',
 'colour_hdri.calibration',
 'colour_hdri.calibration.tests',
 'colour_hdri.generation',
 'colour_hdri.generation.tests',
 'colour_hdri.models',
 'colour_hdri.models.datasets',
 'colour_hdri.models.tests',
 'colour_hdri.plotting',
 'colour_hdri.process',
 'colour_hdri.process.tests',
 'colour_hdri.recovery',
 'colour_hdri.recovery.tests',
 'colour_hdri.sampling',
 'colour_hdri.sampling.tests',
 'colour_hdri.tonemapping',
 'colour_hdri.tonemapping.global_operators',
 'colour_hdri.tonemapping.global_operators.tests',
 'colour_hdri.utilities',
 'colour_hdri.utilities.tests']

package_data = \
{'': ['*'],
 'colour_hdri': ['examples/*',
                 'resources/colour-hdri-examples-datasets/*',
                 'resources/colour-hdri-tests-datasets/*']}

install_requires = \
['colour-science>=0.3.14,<0.4.0', 'recordclass']

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
 'optional': ['colour-demosaicing', 'rawpy'],
 'plotting': ['backports.functools_lru_cache', 'matplotlib'],
 'read-the-docs': ['mock', 'numpy', 'sphinxcontrib-bibtex']}

setup_kwargs = {
    'name': 'colour-hdri',
    'version': '0.1.6',
    'description': 'HDRI / Radiance image processing algorithms for Python',
    'long_description': "Colour - HDRI\n=============\n\n.. start-badges\n\n|actions| |coveralls| |codacy| |version|\n\n.. |actions| image:: https://github.com/colour-science/colour-hdri/workflows/Continuous%20Integration/badge.svg\n    :target: https://github.com/colour-science/colour-hdri/actions\n    :alt: Develop Build Status\n.. |coveralls| image:: http://img.shields.io/coveralls/colour-science/colour-hdri/develop.svg?style=flat-square\n    :target: https://coveralls.io/r/colour-science/colour-hdri\n    :alt: Coverage Status\n.. |codacy| image:: https://img.shields.io/codacy/grade/290ad2c23b0749b99a1d548ca47d9062/develop.svg?style=flat-square\n    :target: https://www.codacy.com/app/colour-science/colour-hdri\n    :alt: Code Grade\n.. |version| image:: https://img.shields.io/pypi/v/colour-hdri.svg?style=flat-square\n    :target: https://pypi.org/project/colour-hdri\n    :alt: Package Version\n\n.. end-badges\n\nA `Python <https://www.python.org/>`__ package implementing various\nHDRI / Radiance image processing algorithms.\n\nIt is open source and freely available under the\n`New BSD License <https://opensource.org/licenses/BSD-3-Clause>`__ terms.\n\n..  image:: https://raw.githubusercontent.com/colour-science/colour-hdri/master/docs/_static/Radiance_001.png\n\n.. contents:: **Table of Contents**\n    :backlinks: none\n    :depth: 3\n\n.. sectnum::\n\nFeatures\n--------\n\nThe following features are available:\n\n-   HDRI / Radiance Image Generation\n-   Debevec (1997) Camera Response Function Computation\n-   Grossberg (2003) Histogram Based Image Sampling\n-   Variance Minimization Light Probe Sampling\n-   Global Tonemapping Operators\n-   Adobe DNG SDK Colour Processing\n-   Absolute Luminance Calibration\n-   Raw Processing Helpers\n\nInstallation\n------------\n\nBecause of their size, the resources dependencies needed to run the various\nexamples and unit tests are not provided within the Pypi package. They are\nseparately available as\n`Git Submodules <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`__\nwhen cloning the\n`repository <https://github.com/colour-science/colour-hdri>`__.\n\nPrimary Dependencies\n^^^^^^^^^^^^^^^^^^^^\n\n**Colour - HDRI** requires various dependencies in order to run:\n\n-  `Python >= 2.7 <https://www.python.org/download/releases/>`__ or\n   `Python >= 3.5 <https://www.python.org/download/releases/>`__\n-  `Colour Science <https://www.colour-science.org>`__\n-  `Recordclass <https://pypi.org/project/recordclass/>`__\n\nOptional Features Dependencies\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\n-   `colour-demosaicing <https://github.com/colour-science/colour-demosaicing>`__\n-   `Adobe DNG Converter <https://www.adobe.com/support/downloads/product.jsp?product=106&platform=Mac>`__\n-   `dcraw <https://www.cybercom.net/~dcoffin/dcraw/>`__\n-   `ExifTool <http://www.sno.phy.queensu.ca/~phil/exiftool/>`__\n-   `rawpy <https://github.com/neothemachine/rawpy>`__\n\nPypi\n^^^^\n\nOnce the dependencies satisfied, **Colour - HDRI** can be installed from\nthe `Python Package Index <http://pypi.python.org/pypi/colour-hdri>`__ by\nissuing this command in a shell::\n\n\tpip install colour-hdri\n\nThe optional features dependencies are installed as follows::\n\n    pip install 'colour-hdri[optional]'\n\nThe figures plotting dependencies are installed as follows::\n\n    pip install 'colour-hdri[plotting]'\n\nThe overall development dependencies are installed as follows::\n\n    pip install 'colour-hdri[development]'\n\nUsage\n-----\n\nAPI\n^^^\n\nThe main reference for `Colour - HDRI <https://github.com/colour-science/colour-hdri>`__\nis the `Colour - HDRI Manual <https://colour-hdri.readthedocs.io/en/latest/manual.html>`__.\n\nExamples\n^^^^^^^^\n\nVarious usage examples are available from the\n`examples directory <https://github.com/colour-science/colour-hdri/tree/master/colour_hdri/examples>`__.\n\nContributing\n------------\n\nIf you would like to contribute to `Colour - HDRI <https://github.com/colour-science/colour-hdri>`__,\nplease refer to the following `Contributing <https://www.colour-science.org/contributing/>`__\nguide for `Colour <https://github.com/colour-science/colour>`__.\n\nBibliography\n------------\n\nThe bibliography is available in the repository in\n`BibTeX <https://github.com/colour-science/colour-hdri/blob/develop/BIBLIOGRAPHY.bib>`__\nformat.\n\nCode of Conduct\n---------------\n\nThe *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,\nis available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct/>`__ page.\n\nAbout\n-----\n\n| **Colour - HDRI** by Colour Developers\n| Copyright © 2015-2019 – Colour Developers – `colour-science@googlegroups.com <colour-science@googlegroups.com>`__\n| This software is released under terms of New BSD License: https://opensource.org/licenses/BSD-3-Clause\n| `https://github.com/colour-science/colour-hdri <https://github.com/colour-science/colour-hdri>`__\n",
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
