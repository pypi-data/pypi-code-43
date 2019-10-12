# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['sqlalchemy_model_factory']

package_data = \
{'': ['*']}

install_requires = \
['sqlalchemy']

extras_require = \
{'docs': ['sphinx', 'm2r', 'sphinx_rtd_theme'], 'pytest': ['pytest>=1.0']}

entry_points = \
{'pytest11': ['model_manager = sqlalchemy_model_factory.pytest']}

setup_kwargs = {
    'name': 'sqlalchemy-model-factory',
    'version': '0.1.1',
    'description': 'A library to assist in generating models from a central location.',
    'long_description': '[![Actions Status](https://github.com/dancardin/sqlalchemy-model-factory/workflows/build/badge.svg)](https://github.com/dancardin/sqlalchemy-model-factory/actions) [![codecov](https://codecov.io/gh/DanCardin/sqlalchemy-model-factory/branch/master/graph/badge.svg)](https://codecov.io/gh/DanCardin/sqlalchemy-model-factory) [![Documentation Status](https://readthedocs.org/projects/sqlalchemy-model-factory/badge/?version=latest)](https://sqlalchemy-model-factory.readthedocs.io/en/latest/?badge=latest)\n\nsqlalchemy-model-factory aims to make it easy to write factory functions for sqlalchemy\nmodels, particularly for use in testing.\n\nIt should make it easy to define as many factories as you might want, with as little\nboilerplate as possible, while remaining as unopinionated as possible about the behavior\ngoing in your factories.\n\nInstallation\n------------\n\n```python\npip install sqlalchemy-model-factory\n```\n\nUsage\n-----\n\nSuppose you\'ve defined a `Widget` model, and for example you want to test some API code\nthat queries for `Widget` instances. Couple of factory functions might look like so:\n\n```python\n# tests/test_example_which_uses_pytest\nfrom sqlalchemy_model_factory import autoincrement, register_at\nfrom . import models\n\n@register_at(\'widget\')\ndef new_widget(name, weight, color, size, **etc):\n    """My goal is to allow you to specify *all* the options a widget might require.\n    """\n    return Widget(name, weight, color, size, **etc)\n\n@register_at(\'widget\', name=\'default\')\n@autoincrement\ndef new_default_widget(autoincrement=1):\n    """My goal is to give you a widget with as little input as possible.\n    """\n    # I\'m gonna call the other factory function...because i can!\n    return new_widget(\n        f\'default_name{autoincrement}\',\n        weight=autoincrement,\n        color=\'rgb({0}, {0}, {0})\'.format(autoincrement),\n        size=autoincrement,\n    )\n```\n\nWhat this does, is register those functions to the registry of factory functions, within\nthe "widget" namespace, at the `name` (defaults to `new`) location in the namespace.\n\nSo when I go to write a test, all I need to do is accept the `mf` fixture (and lets say\na `session` db connection fixture to make assertions against) and I can call all the\nfactories that have been registered.\n\n```python\ndef test_example_model(mf, session):\n    widget1 = mf.widget.new(\'name\', 1, \'rgb(0, 0, 0)\', 1)\n    widget2 = mf.widget.default()\n    widget3 = mf.widget.default()\n    widget4 = mf.widget.default()\n\n    widgets = session.query(Widget).all()\n    assert len(widgets) == 4\n    assert widgets[0].name == \'name\'\n    assert widgets[1].id == widget2.id\n    assert widgets[2].name == widget3.name\n    assert widgets[3].color == \'rgb(3, 3, 3)\'\n```\n\nIn a simple toy example, where you don\'t gain much on the calls themselves the benefits\nare primarily:\n* The instances are automatically put into the database and cleaned up after the test.\n* You can make assertions without hardcoding the values, because you get back a handle on the object.\n\nBut as the graph of models required to set up a particular scenario grows:\n* You can define factories as complex as you want\n  * They can create related objects and assign them to relationships\n  * They can be given sources of randomness or uniqueness to not violate constraints\n  * They can compose with eachother (when called normally, they\'re the same as the original function).\n',
    'author': 'Dan Cardin',
    'author_email': 'ddcardin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dancardin/sqlalchemy-model-factory',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
