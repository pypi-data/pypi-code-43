# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['desdeo_emo',
 'desdeo_emo.EAs',
 'desdeo_emo.Problem',
 'desdeo_emo.othertools',
 'desdeo_emo.population',
 'desdeo_emo.recombination',
 'desdeo_emo.selection']

package_data = \
{'': ['*']}

install_requires = \
['desdeo_problem>=0.8.0,<0.9.0',
 'diversipy>=0.8.0,<0.9.0',
 'jupyter>=1.0,<2.0',
 'numpy>=1.16,<2.0',
 'optproblems>=1.2,<2.0',
 'pandas>=0.25,<0.26',
 'plotly>=4.1,<5.0',
 'pyDOE>=0.3.8,<0.4.0',
 'pygmo>=2.10,<3.0',
 'scikit-learn>=0.21.2,<0.22.0',
 'scipy>=1.2,<2.0']

setup_kwargs = {
    'name': 'desdeo-emo',
    'version': '0.1.1',
    'description': 'The python version reference vector guided evolutionary algorithm.',
    'long_description': '# README\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/EchoBetaGlass/pyrvea/master)\n\nThe python version reference vector guided evolutionary algorithm.\n\nCurrently supported: Multi-objective minimization with visualization and interaction support. Preference is accepted as a reference point.\n\nTo test the code, open the [binder link](https://mybinder.org/v2/gh/industrial-optimization-group/desdeo-emo/master) and read example.ipynb.\n\nRead the documentation [here](https://pyrvea.readthedocs.io/en/latest/)\n\n### Requirements:\n* Python 3.6 or up\n* [Poetry dependency manager](https://github.com/sdispater/poetry): Only for developers\n\n### Installation process for normal users:\n* Run: `pip install pyrvea`\n\n### Installation process for developers:\n* Download and extract the code\n* Create a new virtual environment for the project\n* Run `poetry install` inside the virtual environment shell.\n\n## See the details of RVEA in the following paper\n\nR. Cheng, Y. Jin, M. Olhofer and B. Sendhoff,\nA Reference Vector Guided Evolutionary Algorithm for Many-objective\nOptimization, IEEE Transactions on Evolutionary Computation, 2016\n\nThe source code of pyrvea is implemented by Bhupinder Saini\n\nIf you have any questions about the code, please contact:\n\nBhupinder Saini: bhupinder.s.saini@jyu.fi\\\nProject researcher at University of Jyväskylä.',
    'author': 'Bhupinder Saini',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
