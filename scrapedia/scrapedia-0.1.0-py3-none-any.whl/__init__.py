"""
Scrapedia: A web scraper of Futpédia
====================================

__license__ =  MIT
__author__ = 'Lucas Góes'
__email__ = 'lucas.rd.goes@gmail.com'
"""

from .scrapers import *
from .version import __version__


__all__ = ['errors', 'models', 'packers', 'parsers', 'pipeline', 'requesters',
		   'scrapers', 'seekers']
