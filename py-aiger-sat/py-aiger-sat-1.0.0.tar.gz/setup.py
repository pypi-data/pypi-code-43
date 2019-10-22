# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aiger_sat']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0',
 'py-aiger-cnf>=1.0.0,<2.0.0',
 'py-aiger>=3.3.6,<4.0.0',
 'python-sat>=0.1.4.dev13,<0.2.0']

setup_kwargs = {
    'name': 'py-aiger-sat',
    'version': '1.0.0',
    'description': 'Pythonic interface between AIGs and SAT solvers.',
    'long_description': "# py-aiger-sat\nPythonic interface between AIGs and SAT solvers.\n\n[![Build Status](https://cloud.drone.io/api/badges/mvcisback/py-aiger-sat/status.svg)](https://cloud.drone.io/mvcisback/py-aiger-sat)\n[![codecov](https://codecov.io/gh/mvcisback/py-aiger-sat/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/py-aiger-sat)\n[![PyPI version](https://badge.fury.io/py/py-aiger-sat.svg)](https://badge.fury.io/py/py-aiger-sat)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\n<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->\n**Table of Contents**\n\n- [Installation](#installation)\n- [Usage](#usage)\n\n<!-- markdown-toc end -->\n\n\n# Installation\n\nIf you just need to use `aiger_sat`, you can just run:\n\n`$ pip install py-aiger-sat`\n\nFor developers, note that this project uses the\n[poetry](https://poetry.eustace.io/) python package/dependency\nmanagement tool. Please familarize yourself with it and then\nrun:\n\n`$ poetry install`\n\n# Usage\n\n`aiger_sat` has two seperate API's. The first, called the Object API,\ncenters around the `SolverWrapper` object - a thin wrapper around a\n`pysat` solver. The second is a Function API which exposes 4 functions\n`solve`, `is_sat`, `is_valid`, and `are_equiv`. The function API is\nprimarily useful for simple 1-off SAT instances, where as the object\nAPI is more useful when incremental solves are needed, or the\nunderlying `pysat` solver must be exposed.\n\n## Object API\n\n```python\nfrom aiger_sat import SolverWrapper\n\nsolver = SolverWrapper()  # defaults to Glucose4\n\nfrom pysat.solver import Glucose3\nsolver2 = SolverWrapper(solver=Glucose3)\n```\n\n`solver` operate on boolean expressions in the form of `aiger`\ncircuits with a single output. For example,\n\n\n```python\nimport aiger\n\nx, y, z = map(aiger.atom, ['x', 'y', 'z'])\n\nexpr = (x & y) | ~z\nsolver.add_expr(expr)\nassert solver.is_sat()\nmodel = solver.get_model()\nprint(model)  # {'x': True, 'y': False, 'z': False}\nassert expr(model)\n```\n\nFurther, `aiger_sat` supports making assumptions and computing\nunsat_cores.\n\n```python\n# Make invalid assumption.\nassert not solver.is_sat(assumptions={\n    'x': False,\n    'z': True,\n})\nassert not solver.unsolved\n\ncore = solver.get_unsat_core()\nassert core == {'x': False, 'z': True}\n```\n\n## Function API\n\n```python\nimport aiger\nimport aiger_sat\n\nx, y, z = map(aiger.atom, ['x', 'y', 'z'])\nassert aiger_sat.is_sat(x & y & z)\n\nmodel = aiger_sat.solve(x & y & z)\nassert model == {'x': True, 'y': True, 'z': True}\n\nassert aiger_sat.is_valid(aiger.atom(True))\n\nexpr1 = x & y\nexpr2 = x & y & (z | ~z)\nassert aiger_sat.are_equiv(expr1, expr2)\n```\n",
    'author': 'Marcell Vazquez-Chanlatte',
    'author_email': 'mvc@linux.com',
    'url': 'https://github.com/mvcisback/py-aiger-sat',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
