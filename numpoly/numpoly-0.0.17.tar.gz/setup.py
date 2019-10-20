# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['numpoly',
 'numpoly.array_function',
 'numpoly.construct',
 'numpoly.poly_function']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16,<2.0']

setup_kwargs = {
    'name': 'numpoly',
    'version': '0.0.17',
    'description': 'Polynomials as a numpy datatype',
    'long_description': '|circleci| |codecov| |pypi| |readthedocs|\n\n.. |circleci| image:: https://circleci.com/gh/jonathf/numpoly/tree/master.svg?style=shield\n    :target: https://circleci.com/gh/jonathf/numpoly/tree/master\n.. |codecov| image:: https://codecov.io/gh/jonathf/numpoly/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/jonathf/numpoly\n.. |pypi| image:: https://badge.fury.io/py/numpoly.svg\n    :target: https://badge.fury.io/py/numpoly\n.. |readthedocs| image:: https://readthedocs.org/projects/numpoly/badge/?version=master\n    :target: http://numpoly.readthedocs.io/en/master/?badge=master\n\nNumpoly is a generic library for creating, manipulating polynomial arrays.\n\nMany numerical analysis, prominent in for example uncertainty quantification,\nuses polynomial approximations as proxy for real models to do analysis on.\nThese models are often solutions to non-linear problems discretized with high\nmesh. As such, the corresponding polynomial approximation consist of high\nnumber of dimensions and large multi-dimensional polynomial coefficients.\n\n``numpoly`` is a subclass of ``numpy.ndarray`` implemented to represent\npolynomials as array element. As such is fast and scales very well with the\nsize of the coefficients. It is also compatible with most ``numpy`` functions,\nwhere that makes sense, making the interface fairly intuitive. Some of the\ninterface is also inspired by the ``sympy`` interface.\n\n.. contents:: Table of Contents:\n\nInstallation\n------------\n\nInstallation should be straight forward:\n\n.. code-block:: bash\n\n    pip install numpoly\n\nAnd you should be ready to go.\n\nExample usage\n-------------\n\nConstructing polynomial is typically done using one of the available\nconstructors:\n\n.. code-block:: python\n\n   >>> poly1 = numpoly.monomial(("x", "y"), start=0, stop=3)\n   >>> print(poly1)\n   [1 y x x*y x**2 y**2 y**3 x*y**2 x**2*y x**3]\n\nIt is also possible to construct your own from symbols:\n\n.. code-block:: python\n\n   >>> x, y = numpoly.symbols("x y")\n   >>> poly2 = numpoly.polynomial([1, x**2-1, x*y, y**2-1])\n   >>> print(poly2)\n   [1 -1+x**2 x*y -1+y**2]\n\nOr in combination with other numpy objects:\n\n.. code-block:: python\n\n   >>> poly3 = x**numpy.arange(4)-y**numpy.arange(3, -1, -1)\n   >>> print(poly3)\n   [1-y**3 -y**2+x -y+x**2 -1+x**3]\n\nThe polynomials can be evaluated as needed:\n\n.. code-block:: python\n\n   >>> print(poly1(1, 2))\n   [1 2 1 2 1 4 8 4 2 1]\n   >>> print(poly2(x=[1, 2]))\n   [[1 1]\n    [0 3]\n    [y 2*y]\n    [-1+y**2 -1+y**2]]\n   >>> print(poly1(x=y, y=2*x))\n   [1 2*x y 2*x*y y**2 4*x**2 8*x**3 4*x**2*y 2*x*y**2 y**3]\n\nThe polynomials also support many numpy operations:\n\n.. code-block:: python\n\n   >>> print(numpy.reshape(poly2, (2, 2)))\n   [[1 -1+x**2]\n    [x*y -1+y**2]]\n   >>> print(poly1[::3].astype(float))\n   [1.0 x*y y**3 x**3]\n   >>> print(numpy.sum(poly1.reshape(2, 5), 0))\n   [1+y**2 y+y**3 x+x*y**2 x*y+x**2*y x**2+x**3]\n\nThere are also several polynomial specific operators:\n\n.. code-block:: python\n\n   >>> print(numpoly.diff(poly3, y))\n   [-3*y**2 -2*y -1 0]\n   >>> print(numpoly.gradient(poly3))\n   [[0 1 2*x 3*x**2]\n    [-3*y**2 -2*y -1 0]]\n\n\nDevelopment\n-----------\n\nDevelopment is done using `Poetry <https://poetry.eustace.io/>`_ manager.\nInside the repository directory, install and create a virtual enviroment with:\n\n.. code-block:: bash\n\n   poetry install\n\nTo run tests, run:\n\n.. code-block:: bash\n\n   poentry run pytest numpoly test --doctest-modules\n\nQuestions & Troubleshooting\n---------------------------\n\nFor any problems and questions you might have related to ``numpoly``, please\nfeel free to file an `issue <https://github.com/jonathf/numpoly/issues>`_.\n',
    'author': 'Jonathan Feinberg',
    'author_email': 'jonathf@gmail.com',
    'url': 'https://github.com/jonathf/numpoly',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
