# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['audio_metadata', 'audio_metadata.formats']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.4',
 'bidict<1.0.0',
 'bitstruct>=6.0,<9.0',
 'more-itertools>=4.0,<8.0',
 'pprintpp<1.0.0',
 'tbm-utils>=1.0,<2.0',
 'wrapt>=1.0,<2.0']

extras_require = \
{'dev': ['coverage>=4.5,<5.0',
         'flake8>=3.5,<4.0',
         'flake8-builtins>=1.0,<2.0',
         'flake8-comprehensions>=2.0,<3.0',
         'flake8-import-order>=0.18,<0.19',
         'flake8-import-order-tbm>=1.0.0,<2.0.0',
         'nox>=2019,<2020',
         'pytest>=4.0,<6.0',
         'sphinx>=2.0,<3.0'],
 'doc': ['sphinx>=2.0,<3.0'],
 'lint': ['flake8>=3.5,<4.0',
          'flake8-builtins>=1.0,<2.0',
          'flake8-comprehensions>=2.0,<3.0',
          'flake8-import-order>=0.18,<0.19',
          'flake8-import-order-tbm>=1.0.0,<2.0.0'],
 'test': ['coverage>=4.5,<5.0', 'nox>=2019,<2020', 'pytest>=4.0,<6.0']}

setup_kwargs = {
    'name': 'audio-metadata',
    'version': '0.6.0',
    'description': 'A library for reading and, in the future, writing metadata from audio files.',
    'long_description': "# audio-metadata\n\n[![PyPI](https://img.shields.io/pypi/v/audio-metadata.svg?label=PyPI)](https://pypi.org/project/audio-metadata/)\n![](https://img.shields.io/badge/Python-3.6%2B-blue.svg)  \n[![Travis](https://img.shields.io/travis/thebigmunch/audio-metadata.svg?label=Travis)](https://travis-ci.org/thebigmunch/audio-metadata)\n[![Codecov](https://img.shields.io/codecov/c/github/thebigmunch/audio-metadata.svg?label=Codecov)](https://codecov.io/gh/thebigmunch/audio-metadata)  \n[![Docs - Stable](https://img.shields.io/readthedocs/audio-metadata/stable.svg?label=Docs%20%28Stable%29)](https://audio-metadata.readthedocs.io/en/stable/)\n[![Docs - Latest](https://img.shields.io/readthedocs/audio-metadata/latest.svg?label=Docs%20%28Latest%29)](https://audio-metadata.readthedocs.io/en/latest/)\n\n[audio-metadata](https://github.com/thebigmunch/audio-metadata) is a library for reading and, in the future, writing metadata from audio files.\n\n### Why another audio metadata library? / Why not just use mutagen et al?\n\nClean and understandable code, nice API, and good UX (user experience) are the focal points of audio-metadata.\nOne or more of these things I feel are lacking from already existing alternatives\nenough to want to write something from scratch with them in mind.\nAlso, there are certain features not present in other solutions that would be prohibitively painful to add.\n\n\n### So, why should I use it?\n\nFeatures and functionality that set it apart:\n\n* Uses the Python standard load(s)/dump(s) API.\n\t* Can load filepaths, file-like objects and binary data (bytes-like objects).\n* Metadata objects look like a dict **and** act like a dict.\n\t* Some common libraries shadow the representation of a dict\n\t  and/or dict methods but do not behave like a dict.\n\t* Supports attribute-style access that can be mixed with dict key-subscription.\n* All metadata objects have user-friendly representations.\n\t* This includes *humanized* representations of certain values\n\t  like filesize, bitrate, duration, and sample rate.\n\n```\n>>> import audio_metadata\n\n>>> metadata = audio_metadata.load('05 - Heart of Hearts.flac')\n\n>>> metadata\n<FLAC ({\n\t'filepath': '05 - Heart of Hearts.flac',\n\t'filesize': '44.23 MiB',\n\t'pictures': [],\n\t'seektable': <FLACSeekTable (37 seekpoints)>,\n\t'streaminfo': <FLACStreamInfo ({\n\t\t'bit_depth': 16,\n\t\t'bitrate': '1022 Kbps',\n\t\t'channels': 2,\n\t\t'duration': '06:03',\n\t\t'md5': '3ae700893d099a5d281a5d8db7847671',\n\t\t'sample_rate': '44.1 KHz',\n\t})>,\n\t'tags': <VorbisComment ({\n\t\t'album': ['Myth Takes'],\n\t\t'artist': ['!!!'],\n\t\t'bpm': ['119'],\n\t\t'date': ['2007'],\n\t\t'genre': ['Dance Punk'],\n\t\t'title': ['Heart of Hearts'],\n\t\t'tracknumber': ['05'],\n\t})>,\n})>\n\n>>> metadata['streaminfo']\n<FLACStreamInfo ({\n\t'bit_depth': 16,\n\t'bitrate': '1022 Kbps',\n\t'channels': 2,\n\t'duration': '06:03',\n\t'md5': '3ae700893d099a5d281a5d8db7847671',\n\t'sample_rate': '44.1 KHz',\n})>\n\n>>> metadata.streaminfo.bitrate\n1022134.0362995076\n\n>>> metadata.streaminfo['duration']\n362.9066666666667\n\n>>> metadata['streaminfo'].sample_rate\n44100\n```\n\n\n## Installation\n\n``pip install -U audio-metadata``\n\n\n## Usage\n\nFor the release version, see the [stable docs](https://audio-metadata.readthedocs.io/en/stable/).  \nFor the development version, see the [latest docs](https://audio-metadata.readthedocs.io/en/latest/).\n\nThe high-level API and basic usage are covered, but more advanced features/functionality need documentation.\n\n\n## TODO\n\nPlease don't submit issues regarding the following:\n\n* Docs, docs, and more docs.\n* Finish ID3 abstractions.\n* Add support for more file formats.\n\t* MP4 reading is already well underway.\n* Add write support.\n\nIf you're willing to [contribute](https://github.com/thebigmunch/audio-metadata/blob/master/.github/CONTRIBUTING.md)\nyour time to work on them, post on the **Development** category on the [Discourse forum](https://forum.thebigmunch.me/).\n\n\n## Appreciation\n\nShowing appreciation is always welcome.\n\n#### Thank\n\n[![Say Thanks](https://img.shields.io/badge/thank-thebigmunch-blue.svg?style=flat-square)](https://saythanks.io/to/thebigmunch)\n\nGet your own thanks inbox at [SayThanks.io](https://saythanks.io/).\n\n#### Contribute\n\n[Contribute](https://github.com/thebigmunch/audio-metadata/blob/master/.github/CONTRIBUTING.md) by submitting bug reports, feature requests, or code.\n\n#### Help Others/Stay Informed\n\n[Discourse forum](https://forum.thebigmunch.me/)\n\n#### Referrals/Donations\n\n[![Digital Ocean](https://img.shields.io/badge/Digital_Ocean-referral-orange.svg?style=flat-square)](https://bit.ly/DigitalOcean-tbm-referral) [![Namecheap](https://img.shields.io/badge/Namecheap-referral-orange.svg?style=flat-square)](http://bit.ly/Namecheap-tbm-referral) [![PayPal](https://img.shields.io/badge/PayPal-donate-brightgreen.svg?style=flat-square)](https://bit.ly/PayPal-thebigmunch)\n",
    'author': 'thebigmunch',
    'author_email': 'mail@thebigmunch.me',
    'url': 'https://github.com/thebigmunch/audio-metadata',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
