# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aiger_ptltl']

package_data = \
{'': ['*']}

install_requires = \
['py-aiger>=3.3.6,<4.0.0']

setup_kwargs = {
    'name': 'py-aiger-ptltl',
    'version': '1.0.0',
    'description': 'Library for generating (p)ast (t)ense (l)inear (t)emporal (l)ogic monitors as aiger circuits.',
    'long_description': "# py-aiger-past-ltl\n\nLibrary for generating (p)ast (t)ense (l)inear (t)emporal (l)ogic\nmonitors as aiger circuits. Builds on the [py-aiger](https://github.com/mvcisback/py-aiger) project.\n\n[![Build Status](https://cloud.drone.io/api/badges/mvcisback/py-aiger-past-ltl/status.svg)](https://cloud.drone.io/mvcisback/py-aiger-past-ltl)\n[![codecov](https://codecov.io/gh/mvcisback/py-aiger-past-ltl/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/py-aiger-past-ltl)\n[![PyPI version](https://badge.fury.io/py/py-aiger-ptltl.svg)](https://badge.fury.io/py/py-aiger-ptltl)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\n<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->\n**Table of Contents**\n\n- [Installation](#installation)\n- [Usage](#usage)\n\n<!-- markdown-toc end -->\n\n\n# Installation\n\nIf you just need to use `aiger_ptltl`, you can just run:\n\n`$ pip install py-aiger-ptltl`\n\nFor developers, note that this project uses the\n[poetry](https://poetry.eustace.io/) python package/dependency\nmanagement tool. Please familarize yourself with it and then\nrun:\n\n`$ poetry install`\n\n# Usage\n\nThe primary entry point for using `aiger_ptltl` is the `PTLTLExpr`\nclass which is a simple extension of `aiger.BoolExpr` to support the\ntemporal operators, historically, past (once), (variant) yesterday,\nand since.\n\n```python\nimport aiger_ptltl as ptltl\n\n# Atomic Propositions\nx = ptltl.atom('x')\ny = ptltl.atom('y')\nz = ptltl.atom('z')\n\n# Propositional logic\nexpr1 = ~x\nexpr2 = x & (y | z)\nexpr3 = (x & y) | ~z\nexpr4 = ~(x & y & z)\n\n# Temporal Logic\nexpr5 = x.historically()  #  (H x) ≡ x has held for all previous cycles (inclusive).\nexpr6 = x.once()  #  (P x) ≡ x once held in a past cycle (inclusive).\nexpr7 = x.vyest()  #  (Z x) ≡ x held in the previous cycle (true at time = 0).\nexpr8 = x.since(y)  #  [x S y] ≡ x has held since the cycle after y last held.\n\n# Composition\nexpr9 = expr7.since(expr8.vyest().vyest())\n```\n",
    'author': 'Marcell Vazquez-Chanlatte',
    'author_email': 'mvc@linux.com',
    'url': 'https://github.com/mvcisback/py-aiger-past-ltl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
