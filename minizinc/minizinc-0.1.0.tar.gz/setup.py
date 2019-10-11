# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['minizinc', 'minizinc.API', 'minizinc.CLI']

package_data = \
{'': ['*']}

install_requires = \
['lark-parser>=0.7.5,<0.8.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.6.0,<0.7.0']}

setup_kwargs = {
    'name': 'minizinc',
    'version': '0.1.0',
    'description': 'Access MiniZinc directly from Python',
    'long_description': '<!-- PROJECT LOGO -->\n<br />\n<p align="center">\n  <a href="https://gitlab.com/minizinc/minizinc-python">\n    <img src="https://www.minizinc.org/MiniZn_logo.png" alt="Logo" width="80" height="80">\n  </a>\n\n  <h3 align="center">MiniZinc Python</h3>\n\n  <p align="center">\n    The python package that allows you to access all of MiniZinc\'s functionalities directly from Python.\n    <br />\n    <a href="https://minizinc-python.readthedocs.io/en/latest/"><strong>Explore the docs »</strong></a>\n    <br />\n    <br />\n    <a href="https://gitlab.com/minizinc/minizinc-python/issues">Report Bug</a>\n    ·\n    <a href="https://gitlab.com/minizinc/minizinc-python/issues">Request Feature</a>\n  </p>\n</p>\n\n\n<!-- TABLE OF CONTENTS -->\n## Table of Contents\n\n* [About the Project](#about-the-project)\n* [Getting Started](#getting-started)\n  * [Installation](#installation)\n  * [Usage](#usage)\n* [Testing](#testing)\n* [Roadmap](#roadmap)\n* [Contributing](#contributing)\n* [License](#license)\n* [Contact](#contact)\n<!-- * [Acknowledgements](#acknowledgements) -->\n\n\n<!-- ABOUT THE PROJECT -->\n## About The Project\n\n_MiniZinc Python_ provides an interface from Python to the MiniZinc driver. The\nmost important goal of this project are to allow easy access to MiniZinc using\nnative Python structures. This will allow you to more easily make scripts to run\nMiniZinc, but will also allow the integration of MiniZinc models within bigger\n(Python) projects. This module also aims to expose an interface for meta-search.\nFor problems that are hard to solve, meta-search can provide solutions to reach\nmore or better solutions quickly.\n\n\n<!-- GETTING STARTED -->\n## Getting Started\n\nTo get a MiniZinc Python up and running follow these simple steps.\n\n### Installation\n\n_MiniZinc Python_ can be installed by running `pip install minizinc`. It\nrequires [MiniZinc](https://www.minizinc.org/) 2.2.0+ and\n[Python](https://www.python.org/) 3.6.0+ to be installed on the system. MiniZinc\npython expects the `minizinc` executable to be available on the executable path,\nthe `$PATH` environmental variable, or in a default installation location.\n\n_For more information, please refer to the\n[Documentation](https://minizinc-python.readthedocs.io/en/latest/)_\n\n\n### Usage\n\nOnce all prerequisites and MiniZinc Python are installed, a `minizinc` module\nwill be available in Python. The following Python code shows how to run a\ntypical MiniZinc model.\n\n```python\nimport minizinc\n\n# Create a MiniZinc model\nmodel = minizinc.Model()\nmodel.add_string("""\nvar -100..100: x;\nint: a; int: b; int: c;\nconstraint a*(x*x) + b*x = c;\nsolve satisfy;\n""")\n\n# Transform Model into a instance\ngecode = minizinc.Solver.lookup("gecode")\ninst = minizinc.Instance(gecode, model)\ninst["a"] = 1\ninst["b"] = 4\ninst["c"] = 0\n\n# Solve the instance\nresult = inst.solve(all_solutions=True)\nfor i in range(len(result)):\n    print("x = {}".format(result[i, "x"]))\n```\n\n_For more examples, please refer to the\n[Documentation](https://minizinc-python.readthedocs.io/en/latest/)_\n\n<!-- TESTING INSTRUCTIONS -->\n## Testing\n\nMiniZinc Python uses [Tox](https://pypi.org/project/tox/) environments to test\nits coding style and functionality. The code style tests are executed using\n[Black](https://pypi.org/project/black/),\n[Flake8](https://pypi.org/project/flake8/), and\n[isort](https://pypi.org/project/isort/). The functionality tests are\nconstructed using the [PyTest]() unit testing framework.\n\n  * To run all tests, simply execute `tox` in the repository directory.\n  * Individual environments can be triggered using the `-e` flag.\n    * To test the coding style of the repository run `tox -e check`\n    * The `py3x` environments are used to test a specific Python version; for\n      example, to test using Python version 3.7 run `tox -e py37`\n\nTox can also be used to generate the documentation, `tox -e docs`, and to\ntypeset the Python code, `tox -e format`.\n\n<!-- ROADMAP -->\n## Roadmap\n\nSee the [open issues](https://gitlab.com/minizinc/minizinc-python/issues) for a\nlist of proposed features (and known issues).\n\n\n<!-- CONTRIBUTING -->\n## Contributing\n\nContributions are what make the open source community such an amazing place to\nbe learn, inspire, and create. Any contributions you make are **greatly\nappreciated**.\n\n1. Fork the Project\n2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)\n3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)\n4. Push to the Branch (`git push origin feature/AmazingFeature`)\n5. Open a Merge Request\n\n\n<!-- LICENSE -->\n## License\n\nDistributed under the Mozilla Public License Version 2.0. See `LICENSE` for more information.\n\n\n<!-- CONTACT -->\n## Contact\n👤 **Jip J. Dekker**\n  * Twitter: [@DekkerOne](https://twitter.com/DekkerOne)\n  * Github: [Dekker1](https://github.com/Dekker1)\n\n🏛 **MiniZinc**\n  * Website: [https://www.minizinc.org/](https://www.minizinc.org/)\n\n<!-- ACKNOWLEDGEMENTS -->\n<!-- ## Acknowledgements -->\n\n<!-- * []() -->\n<!-- * []() -->\n<!-- * []() -->\n',
    'author': 'Jip J. Dekker',
    'author_email': 'jip@dekker.one',
    'url': 'https://www.minizinc.org/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
