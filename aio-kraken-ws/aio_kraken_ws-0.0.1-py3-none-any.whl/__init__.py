""" Module to collect ohlc candles from Kraken using websockets. """

from .kraken_ws import KrakenWs
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
