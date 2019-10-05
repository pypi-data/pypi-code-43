''' podfeed

Documentation for this package is available at
https://mmazzocchi.github.io/podfeed/
'''

from logging import getLogger, NullHandler
LOGGER = getLogger('podfeed')
LOGGER.addHandler(NullHandler())

from .parser import StandardFeedParser
from .parser import parseFeed
from .playlists import Playlist
