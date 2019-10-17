# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['rye']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'colorama>=0.4,<0.5',
 'settingscascade>=0.3.4,<0.4.0',
 'toml>=0.10,<0.11',
 'virtualenv>=16.6,<17.0']

entry_points = \
{'console_scripts': ['rye = rye.__main__:cli']}

setup_kwargs = {
    'name': 'rye',
    'version': '0.3',
    'description': '',
    'long_description': 'Intro\n======\n|pypi| |bld| |cvg| |black|\n\nRye is a python task automation tool. It is `one`_ `of`_ a `long`_\n`list`_ of other projects. The question at this point should by, why?\nThe answer is that I had a workflow in mind, but couldn\'t quite get any\nof the other tools to do it.\n\n* Read from a simple config file\n* Maintain a set of virtualenvs for each environment\n* Update those environments when my pyproject.toml or poetry.lock files changed.\n* Run all my tasks in parallel\n* Let tasks share environments where that makes sense (lint and typing?)\n* Work with poetry\n* Allow installing dependencies and the package separately (for Dockerfile caching)\n\nI was trying to set this up without thinking it through a ton, and kept fighting with\ntox\'s built in defaults. I looked at stuff like Nox and Invoke- Nox required more\nprogramming then tox and still had a bunch of defaults I\'d have to figure out how to\noverride. Invoke would have just been working from scratch.\n\nWhat I really wanted was a makefile- list tasks, specify dependencies for those tasks,\nand rebuild them when the dependencies change. The actual commands to run should\nbe completely configurable. I know enough to set this up with a Makefile- but that would\nbe a decent amount of custom code. What if I could make it LOOK like tox, but behave like\nMake?\n\n\n.. code-block:: toml\n\n\t# pyproject.toml\n\t[tool.rye]\n\tdefault_tasks = ["test", "lint", "format", "typing"]\n\n\t[tool.rye."task.pytest"]\n\ttarget_environments = ["poetry.py37", "poetry.py36"]\n\n\t[tool.rye."poetry.py36"."task.pytest"]\n\tcommands = [["pytest", "tests", "--no-cov"]]\n\n\t[tool.rye."task.lint"]\n\ttarget_environments = ["poetry.py37"]\n\tcommands = [["pylint", "src/rye", "tests"]]\n\n\t[tool.rye."task.format"]\n\ttarget_environments = ["poetry.py37"]\n\tcommands = [\n\t\t["black", ".", "--check"],\n\t\t["isort", "-rc", "-tc", "--check-only", "src", "tests"],\n\t]\n\n\t[tool.rye."task.typing"]\n\ttarget_environments = ["poetry.py37"]\n\tcommands = [\n\t\t["mypy", "src/rye", "--ignore-missing-imports"],\n\t]\n\n.. code-block:: bash\n\n\t$ rye\n\tRunning tasks- [\'poetry.py37\', \'TASK poetry.py37#lint\', \'TASK poetry.py37#format\', \'TASK poetry.py37#typing\']\n\tENV poetry.py37 > Preparing Env\n\tENV poetry.py37 > Already using interpreter /home/pbecotte/venvs/rye/bin/python3.7\n\tENV poetry.py37 > Using base prefix \'/usr\'\n\tENV poetry.py37 > New python executable in /home/pbecotte/PycharmProjects/rye/.rye/py37/bin/python3.7\n\tENV poetry.py37 > Also creating executable in /home/pbecotte/PycharmProjects/rye/.rye/py37/bin/python\n\tENV poetry.py37 > Installing setuptools, pip, wheel...\n\nRead the full documentation at https://rye.readthedocs.io/en/latest/\nOr check out the source at https://gitlab.com/pjbecotte/rye\n\nInstallation\n==================\n\nYou can install Rye from pypi-\n\n::\n\n\tpip install rye\n\n.. |cvg| image:: https://gitlab.com/pjbecotte/rye/badges/master/coverage.svg\n.. |bld| image:: https://gitlab.com/pjbecotte/rye/badges/master/pipeline.svg\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n.. |pypi| image:: https://badge.fury.io/py/rye.svg\n\n.. _one: https://github.com/theacodes/nox\n.. _of: https://github.com/tox-dev/tox\n.. _long: https://github.com/fabric/fabric\n.. _list: https://www.gnu.org/software/make/\n',
    'author': 'Paul Becotte',
    'author_email': 'pjbecotte@gmail.com',
    'url': 'https://gitlab.com/pjbecotte/rye',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
