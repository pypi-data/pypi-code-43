# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['geojson_rewind']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'geojson-rewind',
    'version': '0.2.0',
    'description': 'A Python library for enforcing polygon ring winding order in GeoJSON',
    'long_description': "# geojson-rewind\n\n[![Build Status](https://travis-ci.org/chris48s/geojson-rewind.svg?branch=master)](https://travis-ci.org/chris48s/geojson-rewind)\n[![Coverage Status](https://coveralls.io/repos/github/chris48s/geojson-rewind/badge.svg?branch=master)](https://coveralls.io/github/chris48s/geojson-rewind?branch=master)\n![PyPI Version](https://img.shields.io/pypi/v/geojson-rewind.svg)\n![License](https://img.shields.io/pypi/l/geojson-rewind.svg)\n![Python Support](https://img.shields.io/pypi/pyversions/geojson-rewind.svg)\n\nA Python library for enforcing polygon ring winding order in GeoJSON\n\nThe [GeoJSON](https://tools.ietf.org/html/rfc7946) spec mandates the [right hand rule](https://tools.ietf.org/html/rfc7946#section-3.1.6):\n\n> A linear ring MUST follow the right-hand rule with respect to the area it bounds, i.e., exterior rings are counterclockwise, and holes are clockwise.\n\nThis helps you generate compliant Polygon and MultiPolygon geometries.\n\n## Installation\n\n```\npip install geojson-rewind\n```\n\n## Usage\n\n```py\n>>> input = {\n...     'geometry': {   'coordinates': [   [   [100, 0],\n...                                            [100, 1],\n...                                            [101, 1],\n...                                            [101, 0],\n...                                            [100, 0]]],\n...                     'type': 'Polygon'},\n...     'properties': {'foo': 'bar'},\n...     'type': 'Feature'}\n>>> from geojson_rewind import rewind\n>>> output = rewind(input)\n>>> import pprint\n>>> pp = pprint.PrettyPrinter(indent=4)\n>>> pp.pprint(output)\n{   'geometry': {   'coordinates': [   [   [100, 0],\n                                           [101, 0],\n                                           [101, 1],\n                                           [100, 1],\n                                           [100, 0]]],\n                    'type': 'Polygon'},\n    'properties': {'foo': 'bar'},\n    'type': 'Feature'}\n```\n\n## Acknowledgements\n\n`geojson-rewind` is a python port of Mapbox's javascript [geojson-rewind](https://github.com/mapbox/geojson-rewind) package. Credit to [Tom MacWright](https://github.com/tmcw) and [contributors](https://github.com/mapbox/geojson-rewind/graphs/contributors).\n",
    'author': 'chris48s',
    'author_email': None,
    'url': 'https://github.com/chris48s/geojson-rewind',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
