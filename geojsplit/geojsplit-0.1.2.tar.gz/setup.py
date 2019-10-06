# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['geojsplit']

package_data = \
{'': ['*']}

install_requires = \
['geojson>=2.5,<3.0', 'ijson>=2.4,<3.0', 'simplejson>=3.16,<4.0']

extras_require = \
{'docs': ['sphinx>=2.2,<3.0', 'sphinx_rtd_theme>=0.4.3,<0.5.0']}

entry_points = \
{'console_scripts': ['geojsplit = geojsplit.cli:main']}

setup_kwargs = {
    'name': 'geojsplit',
    'version': '0.1.2',
    'description': 'A python implementation of the npm package geojsplit. Used to split GeoJSON files into smaller pieces.',
    'long_description': '# geojsplit\nA python implementation of the node package geojsplit: https://github.com/woodb/geojsplit\n\n[![Build Status](https://travis-ci.com/underchemist/geojsplit.svg?branch=master)](https://travis-ci.com/underchemist/geojsplit)\n[![Documentation Status](https://readthedocs.org/projects/geojsplit/badge/?version=latest)](https://geojsplit.readthedocs.io/en/latest/?badge=latest)\n[![Coverage Status](https://coveralls.io/repos/github/underchemist/geojsplit/badge.svg?branch=master)](https://coveralls.io/github/underchemist/geojsplit?branch=master)\n![PyPI](https://img.shields.io/pypi/v/geojsplit)\n![GitHub](https://img.shields.io/github/license/underchemist/geojsplit)\n\n## Installation\n\n### With poetry\n\nFor an [introduction to poetry](https://dev.to/yukinagae/beginner-guide-on-poetry-new-python-dependency-management-tool-4327/).\n\n```\n$ poetry add geojsplit\n```\n\nwill add geojsplit to your current virtual environment and update your poetry.lock file. If you would like to contribute or develop geojsplit\n\n```\n$ git clone https://github.com/underchemist/geojsplit.git\n$ cd geojsplit\n$ poetry install\n```\n\nYou may need some extra configuration to make poetry play nice with conda virtual environments\n\n```\npoetry config settings.virtualenvs.path <path_to_conda_install>/envs  # tell poetry where you virtualenvs are stored\npoetry config settings.virtualenvs.create 0  # tell poetry not to try to create its own virtualenvs.\n```\n\nSee https://github.com/sdispater/poetry/issues/105#issuecomment-498042062 for more info.\n\n```\n$ poetry config settings.virtualenvs.path $CONDA_ENV_PATH\n$ poetry config settings.virtualenvs.create 0\n```\n\n### With pip\nThough geojsplit is developed using [poetry](https://poetry.eustace.io/) (and as such does not have a setup.py), [pep517](https://www.python.org/dev/peps/pep-0517/) implementation in pip means we can install it directly\n\n```\n$ pip install geojsplit\n```\n\n## Usage\n\nAlthough both the library code and the command line tool of geojsplit are relatively simple, there are use cases for both. You may want to use the backend `GeoJSONBatchStreamer` class directly in order to do more sophisticated manipulations with GeoJOSN documents. As a command line tool geojsplit also works well as a preprocessing step for working with large GeoJSON documents i.e. for piping into GDAL’s ogr2ogr tool.\n\n### As a library\n\nOnce installed, geojsplit can be imported in like\n\n```\nfrom geojsplit import geojsplit\n\ngeojson = geojsplit.GeoJSONBatchStreamer("/path/to/some.geojson")\n\nfor feature_collection in geojson.stream():\n    do_something(feature_collection)\n    ...\n```\n\nIf the `/path/to/some.geojson` does not exists, `FileNotFound` will be raised.\n\nYou can control how many features are streamed into a Feature Collection using the batch parameter (Default is 100).\n\n```\n>>> g = geojson.stream(batch=2)  # instatiate generator object\n>>> data = next(g)\n>>> print(data)\n{"features": [{"geometry": {"coordinates": [[[-118.254638, 33.7843], [-118.254637,\n33.784231], [-118.254556, 33.784232], [-118.254559, 33.784339], [-118.254669,\n33.784338], [-118.254668, 33.7843], [-118.254638, 33.7843]]], "type": "Polygon"},\n"properties": {}, "type": "Feature"}, {"geometry": {"coordinates": [[[-118.254414,\n33.784255], [-118.254232, 33.784255], [-118.254232, 33.784355], [-118.254414,\n33.784355], [-118.254414, 33.784255]]], "type": "Polygon"}, "properties": {}, "type":\n"Feature"}], "type": "FeatureCollection"}\n>>> print(len(data["features"]))\n2\n```\n\nIf your GeoJSON document has a different format or you want to iterate over different elements on your document, you can also pass a different value to the `prefix` keyword argument (Default is `\'features.item\'`). This is an argument passed directly down to a `ijson.items` call, for more information see https://github.com/ICRAR/ijson.\n\n### As a command line tool\n\nAfter installing you should have the geojsplit executable in your `PATH`.\n\n```\n$ geojsplit -h\nusage: geojsplit [-h] [-l GEOMETRY_COUNT] [-a SUFFIX_LENGTH] [-o OUTPUT]\n                [-n LIMIT] [-v] [-d] [--version]\n                geojson\n\nSplit a geojson file into many geojson files.\n\npositional arguments:\ngeojson               filename of geojson file to split\n\noptional arguments:\n-h, --help            show this help message and exit\n-l GEOMETRY_COUNT, --geometry-count GEOMETRY_COUNT\n                        the number of features to be distributed to each file.\n-a SUFFIX_LENGTH, --suffix-length SUFFIX_LENGTH\n                        number of characters in the suffix length for split\n                        geojsons\n-o OUTPUT, --output OUTPUT\n                        output directory to save split geojsons\n-n LIMIT, --limit LIMIT\n                        limit number of split geojson file to at most LIMIT,\n                        with GEOMETRY_COUNT number of features.\n-v, --verbose         increase output verbosity\n-d, --dry-run         see output without actually writing to file\n--version             show geojsplit version number\n```\n\nBy default splitted GeoJSON files are saved as `filename_x<SUFFIX_LENGTH characters long>.geojson`. Default SUFFIX_LENGTH is 4, meaning that 456976 unique files can be generated. If you need more use `-a` or `--suffix-length` to increase this value appropriately.\n\nThe `--geometry-count` flag corresponds to the batch keyword argument for `GeoJSONBatchStreamer.stream` method. Note that if GEOMETRY_COUNT does not divide equally into the number of features in the Feature Collection, the last batch of features will be < GEOMETRY_COUNT.\n\nFinally, to only iterate over the the first n elements of a GeoJSON document, use `--limit`.',
    'author': 'Yann-Sebastien Tremblay-Johnston',
    'author_email': 'yanns.tremblay@gmail.com',
    'url': 'https://github.com/underchemist/geojsplit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
