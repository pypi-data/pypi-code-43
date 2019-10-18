# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['settingscascade']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=2.10,<2.11', 'sortedcontainers>=2.1,<2.2']

setup_kwargs = {
    'name': 'settingscascade',
    'version': '0.4.2',
    'description': 'Cascade settings from multiple levels of specificity',
    'long_description': 'Intro\n======\n|pypi| |bld| |cvg| |black|\n\nOne of the most common ways to let users customize the way an app\nworks is to use config files. This means that many projects wind up\nincluding an implementation to read in the config values, specify\ndefaults, control which values get looked up when, and enforce some\nsort of schema.\n\nsettingscascade is designed to handle this scenario. While it can be\nused in simple situations, it really shines when you need to pull in\nvalues from a variety of sources, have a rich set of defaults, and\ngive users flexibility in configuring overrides at various levels.\nThe model it uses is CSS, mimicking the way that css uses selectors\nto cascade settings from various levels of specificity. Your users\nspecify rule blocks the same as they would in CSS-\n\n.. code-block:: yaml\n\n\t# Each rule block has a selector, using CSS semantics\n\t# this block is for a task element with the class "default"\n\ttask.default:\n\t    command: "echo hello"\n\t    on_complete: "echo world"\n\n\t# You can specify top level settings as well for a final\n\t# level of fallback\n\tproject_name: "my project"\n\nThen your app can use the config\n\n.. code-block:: python\n\n\t# Task represents an element (like a div or a in HTML).\n\t# you can specify what values are valid for this element type\n\tclass Task(SettingsSchema):\n\t\t_name_ = task\n\t\tcommand: str\n\t\ton_complete: str\n\n\tconfig = SettingsManager(yaml.load("config.yml"), [Task])\n\n\t# In your code, you can pull an element from the settingsmanager\n\t# object and find the rules that apply. This is like an element\n\t# <task class="default"></task>\n\ttask_config = config.task(class="default")\n\trun_task(\n\t\tcommand=task_config.command,\n\t\ton_complete=task_config.on_complete,\n\t\tname=config.project_name,\n\t)\n\nRead the full documentation at https://settingscascade.readthedocs.io/en/latest/\n\nInstallation\n==================\n\nYou can install settingscascade from pypi-\n\n::\n\n\tpip install settingscascade\n\n.. |cvg| image:: https://gitlab.com/pjbecotte/settingscascade/badges/master/coverage.svg\n.. |bld| image:: https://gitlab.com/pjbecotte/settingscascade/badges/master/pipeline.svg\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n.. |pypi| image:: https://badge.fury.io/py/settingscascade.svg\n',
    'author': 'Paul Becotte',
    'author_email': 'pjbecotte@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/pjbecotte/settingscascade',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
