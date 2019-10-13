# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['solid_mcad', 'solid_mcad.MCAD']

package_data = \
{'': ['*'],
 'solid_mcad.MCAD': ['PyOpenScad/*',
                     'PyOpenScad/examples/*',
                     'PyOpenScad/examples/mazebox/*',
                     'PyOpenScad/examples/playground/*',
                     'PyOpenScad/scratch/*',
                     'bitmap/*']}

install_requires = \
['solidpython>=0.3.2']

setup_kwargs = {
    'name': 'solid-mcad',
    'version': '0.1.1',
    'description': 'Python binding for the OpenSCAD language utility library, MCAD',
    'long_description': None,
    'author': 'Evan Jones',
    'author_email': 'evan_t_jones@mac.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
