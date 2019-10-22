# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['spotify', 'spotify.models', 'spotify.sync']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6,<4.0']

setup_kwargs = {
    'name': 'spotify',
    'version': '0.8.0',
    'description': 'spotify.py is an asynchronous API wrapper for Spotify written in Python.',
    'long_description': '![logo](/docs/source/_static/images/logo.png)\n\n\n![Version info](https://img.shields.io/pypi/v/spotify.svg)\n[![GitHub stars](https://img.shields.io/github/stars/mental32/spotify.py.svg)](https://github.com/mental32/spotify.py/stargazers)\n![Discord](https://img.shields.io/discord/438465139197607939.svg?style=flat-square)\n![Travis](https://api.travis-ci.org/mental32/spotify.py.svg?branch=master)\n\n# spotify.py\n\nAn API library for the spotify client and the Spotify Web API written in Python.\n\nSpotify.py is an asyncronous API library for Spotify. While maintaining an\nemphasis on being purely asyncronous the library provides syncronous\nfunctionality with the `spotify.sync` module.\n\n```python\nimport spotify.sync as spotify  # Nothing requires async/await now!\n```\n\n## Index\n\n - [Installing](#Installing)\n - [Examples](#Examples)\n - [Resources](#Resources)\n\n## Installing\n\nTo install the library simply clone it and run setup.py\n- `git clone https://github.com/mental32/spotify.py`\n- `pip3 -U install .`\n\nor use pypi\n\n- `pip3 install -U spotify` (latest stable)\n- `pip3 install -U git+https://github.com/mental32/spotify.py#egg=spotify` (nightly)\n\n## Examples\n### Sorting a playlist by popularity\n\n```py\nimport sys\nimport getpass\n\nimport spotify\n\nasync def main():\n    client = spotify.Client(client_id, secret)\n\n    playlist_uri = input("playlist_id: ")\n    client_id = input("client_id: ")\n    secret = getpass.getpass("application secret:")\n    token = getpass.getpass("user token:")\n\n    user = await spotify.User.from_token(client, token)\n\n    for playlist in await user.get_playlists():\n        if playlist.uri == playlist_uri:\n            await playlist.sort(reverse=True, key=(lambda track: track.popularity))\n            break\n    else:\n        print(\'No playlists were found!\', file=sys.stderr)\n\nif __name__ == \'__main__\':\n    client.loop.run_until_complete(main())\n```\n\n### Required oauth scopes for methods\n\n```py\nimport spotify\nfrom spotify.utils import get_scope_metadata\n\n# In order to call this method sucessfully the "user-modify-playback-state" scope is required.\nprint(get_scope_metadata(spotify.Player.play))  # => ["user-modify-playback-state"]\n\n# Some methods have no oauth scope requirements, so `None` will be returned instead.\nprint(get_scope_metadata(spotify.Playlist.get_tracks))  # => None\n```\n\n### Usage with flask\n\n```py\nimport string\nimport random\nfrom typing import Tuple, Dict\n\nimport flask\nimport spotify.sync as spotify\n\nSPOTIFY_CLIENT = spotify.Client(\'SPOTIFY_CLIENT_ID\', \'SPOTIFY_CLIENT_SECRET\')\n\nAPP = flask.Flask(__name__)\nAPP.config.from_mapping({\'spotify_client\': SPOTIFY_CLIENT})\n\nREDIRECT_URI: str = \'http://localhost:8888/spotify/callback\'\n\nOAUTH2_SCOPES: Tuple[str] = (\'user-modify-playback-state\', \'user-read-currently-playing\', \'user-read-playback-state\')\nOAUTH2: spotify.OAuth2 = spotify.OAuth2(SPOTIFY_CLIENT.id, REDIRECT_URI, scope=OAUTH2_SCOPES)\n\nSPOTIFY_USERS: Dict[str, spotify.User] = {}\n\n\n@APP.route(\'/spotify/callback\')\ndef spotify_callback():\n    try:\n        code = flask.request.args[\'code\']\n    except KeyError:\n        return flask.redirect(\'/spotify/failed\')\n    else:\n        key = \'\'.join(random.choice(string.ascii_uppercase) for _ in range(16))\n        SPOTIFY_USERS[key] = spotify.User.from_code(\n            SPOTIFY_CLIENT,\n            code,\n            redirect_uri=REDIRECT_URI,\n            refresh=True\n        )\n\n        flask.session[\'spotify_user_id\'] = key\n\n    return flask.redirect(\'/\')\n\n@APP.route(\'spotify/failed\')\ndef spotify_failed():\n    flask.session.pop(\'spotify_user_id\', None)\n    return \'Failed to authenticate with Spotify.\'\n\n@APP.route(\'/\')\n@APP.route(\'/index\')\ndef index():\n    try:\n        return repr(SPOTIFY_USERS[flask.session[\'spotify_user_id\']])\n    except KeyError:\n        return flask.redirect(OAUTH2.url)\n\nif __name__ == \'__main__\':\n    APP.run(\'127.0.0.1\', port=8888, debug=False)\n```\n\n## Resources\n\nFor resources look at the [examples](https://github.com/mental32/spotify.py/tree/master/examples) or ask in the [discord](https://discord.gg/k43FSFF)\n',
    'author': 'mental',
    'author_email': 'm3nta1@yahoo.com',
    'url': 'https://github.com/mental32/spotify.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
