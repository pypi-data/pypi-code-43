# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['geometry_to_spatialite']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.6.4,<2.0.0',
 'geojson>=2.5.0,<3.0.0',
 'pyshp>=2.1.0,<3.0.0',
 'sqlite-utils>=1.11,<2.0']

entry_points = \
{'console_scripts': ['geojson-to-spatialite = '
                     'geometry_to_spatialite.geojson:main',
                     'shapefile-to-spatialite = '
                     'geometry_to_spatialite.shapefile:main']}

setup_kwargs = {
    'name': 'geometry-to-spatialite',
    'version': '0.2.0',
    'description': 'Import geographic and spatial data from files into a SpatiaLite DB',
    'long_description': "# geometry-to-spatialite\n\n[![Build Status](https://travis-ci.org/chris48s/geometry-to-spatialite.svg?branch=master)](https://travis-ci.org/chris48s/geometry-to-spatialite)\n[![Coverage Status](https://coveralls.io/repos/github/chris48s/geometry-to-spatialite/badge.svg?branch=master)](https://coveralls.io/github/chris48s/geometry-to-spatialite?branch=master)\n[![PyPI Version](https://img.shields.io/pypi/v/geometry-to-spatialite.svg)](https://pypi.org/project/geometry-to-spatialite/)\n![License](https://img.shields.io/pypi/l/geometry-to-spatialite.svg)\n![Python Support](https://img.shields.io/pypi/pyversions/geometry-to-spatialite.svg)\n![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)\n\n\nImport geographic and spatial data from files into a SpatiaLite DB.\n\nThis project is primarily useful for browsing and publishing geographic and spatial data with [datasette](https://github.com/simonw/datasette) and [datasette-leaflet-geojson](https://github.com/simonw/datasette-leaflet-geojson). It is inspired by [csvs-to-sqlite](https://github.com/simonw/csvs-to-sqlite) and provides a similar interface.\n\n## Setup\n\n```\npip install geometry-to-spatialite\n```\n\nYou'll need python >=3.6 and the [SpatiaLite](https://www.gaia-gis.it/fossil/libspatialite/index) module for SQLite. \n\n### Install SpatiaLite on Debian/Ubuntu\n\n```\napt install spatialite-bin libsqlite3-mod-spatialite\n```\n\n### Install SpatiaLite on Mac\n\n```\nbrew update\nbrew install spatialite-tools\n```\n\n## Usage\n\n### On the console\n\nGeometry-to-spatialite installs two commands: `shapefile-to-spatialite` and `geojson-to-spatialite`. Both provide the same arguments.\n\nBasic usage\n\n```\nshapefile-to-spatialite myfile.shp mydatabase.db\n```\n\nThis will create a new SQLite database called `mydatabase.db` containing a single table, `myfile`\n\nYou can provide multiple files:\n\n```\nshapefile-to-spatialite one.shp two.shp bundle.db\n```\n\nThe `bundle.db` database will contain two tables, `one` and `two`.\n\nThis means you can use wildcards:\n\n```\nshapefile-to-spatialite ~/Downloads/*.shp mydownloads.db\n```\n\nIf you pass a path to one or more directories, the script will recursively search those directories for files and create tables for each one:\n\n```\nshapefile-to-spatialite ~/path/to/directory all-my-shapefiles.db\n```\n\nFor more help on usage and arguments, run `shapefile-to-spatialite --help` or `geojson-to-spatialite --help`\n\n### As a library\n\n```py\nfrom shapefile_to_spatialite import (\n    geojson_to_spatialite,\n    shp_to_spatialite,\n    DataImportError\n)\n\n\n# Use the defaults\ntry:\n    geojson_to_spatialite('mydatabase.db', 'myfile.geojson')\nexcept DataImportError:\n    raise\n\n\n# With optional params\n# geojson_to_spatialite() and shp_to_spatialite() support the same argument list\ntry:\n    geojson_to_spatialite(\n        'mydatabase.db',\n        'myfile.geojson',\n        table_name='custom',  # set a custom table name (defaults to the filename)\n        srid=3857,            # specify a custom SRID (default is 4326)\n        pk='id',              # field (str) or fields (list/tuple) to use as a\n                              # primary key (default is no primary key)\n        write_mode='append',  # pass 'replace' or 'append' to overwrite\n                              # or append to an existing table\n\n        # In most cases the spatialite extension will be automatically detected and loaded\n        # If not you can manully pass a path to the .so .dylib or .dll file\n        spatialite_extension='path/to/mod_spatialite.so'\n    )\nexcept DataImportError:\n    raise\n```\n\n## Troubleshooting\n\n### Failed to load the SpatiaLite extension\n\nGeometry-to-spatialite requires [SpatiaLite](https://www.gaia-gis.it/fossil/libspatialite/index) to be installed. See [Setup](#setup). Geometry-to-spatialite will attempt to automatically load the extension. If you've installed the extension and you're still seeing this error, you can use the `--spatialite-extension` flag (using on the console) or `spatialite_extension` (using as a library) to manually specify the path to the SpatiaLite extension.\n",
    'author': 'chris48s',
    'author_email': None,
    'url': 'https://github.com/chris48s/geometry-to-spatialite',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
