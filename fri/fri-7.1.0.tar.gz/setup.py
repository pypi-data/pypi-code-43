# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['fri', 'fri.model', 'fri.toydata']

package_data = \
{'': ['*'], 'fri': ['tests/*']}

install_requires = \
['attrs>=19.3.0,<20.0.0',
 'cvxpy==1.0.25',
 'ecos>=2.0.7,<3.0.0',
 'joblib>=0.14.0,<0.15.0',
 'matplotlib>=3.1,<4.0',
 'numpy>=1.17,<2.0',
 'scikit-learn>=0.21.1,<0.22.0',
 'scipy>=1.0,<2.0']

setup_kwargs = {
    'name': 'fri',
    'version': '7.1.0',
    'description': 'Implementation of Feature Relevance Bounds method to perform Feature Selection and further analysis.',
    'long_description': '# Feature Relevance Intervals - FRI\n\n![Feature Relevance Intervals - FRI](docs/relevancebars.png)\n\n\n![Travis (.org)](https://img.shields.io/travis/lpfann/fri)\n![Coveralls github](https://img.shields.io/coveralls/github/lpfann/fri)\n[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1188749.svg)](https://doi.org/10.5281/zenodo.1188749)\n[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lpfann/fri/blob/master/doc/source/notebooks/Guide.ipynb)\n![PyPI](https://img.shields.io/pypi/v/fri)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fri)\n![GitHub](https://img.shields.io/github/license/lpfann/fri)\n\n__FRI__ is a Python 3 package for analytical feature selection\npurposes. It allows superior feature selection in the sense that all\nimportant features are conserved. At the moment we support multiple\nlinear models for solving Classification, Regression and Ordinal\nRegression Problems. We also support LUPI paradigm where at learning\ntime, privileged information is available.\n\n\n## Documentation\nCheck out our online documentation at [fri.lpfann.me](https://fri.lpfann.me).\nThere you can find a quick start guide and more background information.\n\nYou can also run the guide directly without setup online [here](https://colab.research.google.com/github/lpfann/fri/blob/master/doc/source/notebooks/Guide.ipynb).\n\n\n## Installation\n`FRI` requires __Python 3.6+__. \n\nFor a __stable__ version from `PyPI` use\n```shell\n$ pip install fri\n```\n\n## Usage\nPlease refer to the [documentation](https://fri.lpfann.me) for advice.\nFor a quick start we provide a simple guide which leads through the main functions.\n\n## References  \n\n[1] Göpfert C, Pfannschmidt L, Hammer B. Feature Relevance Bounds for Linear Classification. In: Proceedings of the ESANN. 25th European Symposium on Artificial Neural Networks, Computational Intelligence and Machine Learning;\n<https://pub.uni-bielefeld.de/publication/2908201>\n\n[2] Göpfert C, Pfannschmidt L, Göpfert JP, Hammer B. Interpretation of Linear Classifiers by Means of Feature Relevance Bounds. Neurocomputing.\n<https://pub.uni-bielefeld.de/publication/2915273>\n\n[3] Lukas Pfannschmidt, Jonathan Jakob, Michael Biehl, Peter Tino, Barbara Hammer: Feature Relevance Bounds for Ordinal Regression. Proceedings of the ESANN. 27th European Symposium on Artificial Neural Networks, Computational Intelligence and Machine Learning; Accepted.\n<https://pub.uni-bielefeld.de/record/2933893>\n\n[4] Pfannschmidt L, Göpfert C, Neumann U, Heider D, Hammer B: FRI - Feature Relevance Intervals for Interpretable and Interactive Data Exploration. Presented at the 16th IEEE International Conference on Computational Intelligence in Bioinformatics and Computational Biology, Certosa di Pontignano, Siena - Tuscany, Italy. <https://ieeexplore.ieee.org/document/8791489>\n',
    'author': 'Lukas Pfannschmidt',
    'author_email': 'lukas@lpfann.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://fri.lpfann.me',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
