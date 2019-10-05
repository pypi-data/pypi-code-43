# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['underground', 'underground.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'google>=2.0,<3.0',
 'gtfs-realtime-bindings>=0.0.6,<0.0.7',
 'protobuf3-to-dict>=0.1.5,<0.2.0',
 'pydantic>=0.31.1,<0.32.0',
 'pytz>=2019.2,<2020.0',
 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['underground = underground.cli.cli:entry_point']}

setup_kwargs = {
    'name': 'underground',
    'version': '0.2.7.1',
    'description': "Utilities for NYC's realtime MTA data feeds.",
    'long_description': '# Python MTA Utilities\n\n[![GitHub Actions status](https://github.com/nolanbconaway/underground/workflows/Main%20Workflow/badge.svg)](https://github.com/nolanbconaway/underground/actions)\n[![codecov](https://codecov.io/gh/nolanbconaway/underground/branch/master/graph/badge.svg)](https://codecov.io/gh/nolanbconaway/underground)\n\nThis is a set of Python utilities that I use to deal with [real-time NYC subway data](https://datamine.mta.info/).\n\nI usually want to know when trains are going to depart a specific stop along a specific train line, so right now the tools are mostly for that. But I tried to write them to support arbitrary functionality.\n\n## Install\n\nNot on pypi just yet, so:\n\n``` sh\npip install git+https://github.com/nolanbconaway/underground.git#egg=underground\n```\n\nTo request data from the MTA, you\'ll also need a free API key.[Register here](https://datamine.mta.info/user/register).\n\n## Python API\n\nOnce you have your API key, use the Python API like:\n\n``` python\nimport os\n\nfrom underground import metadata, SubwayFeed\n\nAPI_KEY = os.getenv(\'MTA_API_KEY\')\nROUTE = \'Q\'\n\n# get feed id for the Q train route\nFEED_ID = metadata.get_feed_id(ROUTE)\n\n# request and serialize the feed data.\nfeed = SubwayFeed.get(FEED_ID, api_key=API_KEY)\n\n# request will automatically try to read from $MTA_API_KEY if a key is not provided,\n# so this also works:\nfeed = SubwayFeed.get(FEED_ID)\n\n# extract train stops on each line\nq_train_stops = feed.extract_stop_dict()[ROUTE]\n```\n\n`feed.extract_stop_dict` will return a dictionary of dictionaries, like:\n\n    {\n\n      "route_1": {\n        "stop_1": [datetime.datetime(...), datetime.datetime(...)], \n        "stop_2": [datetime.datetime(...), datetime.datetime(...)], \n        ...\n      }, \n      "route_2": {\n        "stop_1": [datetime.datetime(...), datetime.datetime(...)], \n        "stop_2": [datetime.datetime(...), datetime.datetime(...)], \n        ...\n      }\n\n    }\n\n> Note: future functionality to be written around the `SubwayFeed` class.\n\n## CLI\n\nThe `underground` command line tool is also installed with the package.\n\n    $ underground --help\n    Usage: underground [OPTIONS] COMMAND [ARGS]...\n\n      Command line handlers for MTA realtime data.\n\n    Options:\n\n      --help  Show this message and exit.\n\n      feed       Request an MTA feed.\n      findstops  Find your stop ID.\n      stops      Print out train departure times for all stops on a subway line.\n\n### `feed` \n\n    $ underground feed --help\n    Usage: underground feed [OPTIONS] [1|2|36|11|16|51|21|26|31]\n\n      Request an MTA feed.\n\n    Options:\n\n      --api-key TEXT         MTA API key. Will be read from $MTA_API_KEY if not\n                             provided.\n      --json                 Option to output the feed data as JSON. Otherwise\n                             output will be bytes.\n      -r, --retries INTEGER  Retry attempts in case of API connection failure.\n                             Default 100.\n      --help                 Show this message and exit.\n\nUse it like\n\n    $ export MTA_API_KEY=\'...\'\n    $ underground feed 16 --json > feed_16.json\n\n### `stops` \n\n    $ underground stops --help\n    Usage: underground stops [OPTIONS] [H|M|D|1|Z|A|N|GS|SI|J|G|Q|L|B|R|F|E|2|7|W|\n                             6|4|C|5|FS]\n        \n      Print out train departure times for all stops on a subway line.\n\n    Options:\n\n      -f, --format TEXT      strftime format for stop times. Use `epoch` for a\n                             unix timestamp.\n      -r, --retries INTEGER  Retry attempts in case of API connection failure.\n                             Default 100.\n      --api-key TEXT         MTA API key. Will be read from $MTA_API_KEY if not\n                             provided.\n      -t, --timezone TEXT    Output timezone. Ignored if --epoch. Default to NYC\n                             time.\n      --help                 Show this message and exit.\n\nStops are printed to stdout in the format `stop_id t1 t2 ... tn` .\n\n``` sh\n$ export MTA_API_KEY=\'...\'\n$ underground stops Q | tail -2\nQ05S 19:01 19:09 19:16 19:25 19:34 19:44 19:51 19:58\nQ04S 19:03 19:11 19:18 19:27 19:36 19:46 19:53 20:00\n```\n\nIf you know your stop id (stop IDs can be found in [stops.txt](http://web.mta.info/developers/data/nyct/subway/google_transit.zip)), you can grep the results:\n\n``` sh\n$ underground stops Q | grep Q05S\nQ05S 19:09 19:16 19:25 19:34 19:44 19:51 19:58\n```\n\nIf you don\'t know your stop, see below for a handy tool!\n\n### `findstops` \n\n    $ underground findstops --help\n    Usage: underground findstops [OPTIONS] QUERY...\n\n      Find your stop ID.\n\n      Query a location and look for your stop ID, like:\n\n      $ underground findstops parkside av\n\n    Options:\n\n      --json  Option to output the data as JSON. Otherwise will be human readable\n              table.\n\n      --help  Show this message and exit.\n\nEnter the name of your stop and a table of stops with matching names will be returned.\n\n    $ underground findstops parkside\n    ID: D27N    Direction: NORTH    Lat/Lon: 40.655292, -73.961495    Name: PARKSIDE AV\n    ID: D27S    Direction: SOUTH    Lat/Lon: 40.655292, -73.961495    Name: PARKSIDE AV\n\nSome names are ambiguous (try "fulton st"), for these you\'ll have to dig into the [metadata](http://web.mta.info/developers/data/nyct/subway/google_transit.zip) more carefully.\n\n## Todo\n\nNone of this is particularly important, I am happy with the API at the moment.\n\n*   [ ] Better exception printing from click.\n*   [ ] Pypi?\n*   [ ] Markdown auto format. Check as a part of the build process.\n*   [x] Add some tooling to make finding your stop easier.\n*   [ ] Add method to SubwayFeed which counts trains per line/direction.\n\n',
    'author': 'Nolan Conaway',
    'author_email': 'nolanbconaway@gmail.com',
    'url': 'https://github.com/nolanbconaway/underground',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
