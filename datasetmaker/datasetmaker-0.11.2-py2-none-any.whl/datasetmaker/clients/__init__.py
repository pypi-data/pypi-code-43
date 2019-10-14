from .esv import ESVClient
from .hdi import HDIClient
from .meps import MEPs
from .mynewsflash.client import MyNewsFlashClient
from .nobel import NobelClient
from .scb import SCBClient
from .sipri import SIPRI
from .unsc import UNSC
from .valforsk import ValforskClient
from .wikipedia.client import WikipediaClient
from .worldbank import WorldBank


available = {
    # 'oecd': OECD,
    # 'skolverket': SKVClient,
    # 'socialstyrelsen': SocialstyrelsenClient,
    'esv': ESVClient,
    'hdi': HDIClient,
    'meps': MEPs,
    'mynewsflash': MyNewsFlashClient,
    'nobel': NobelClient,
    'scb': SCBClient,
    'sipri': SIPRI,
    'unsc': UNSC,
    'valforsk': ValforskClient,
    'wikipedia': WikipediaClient,
    'worldbank': WorldBank,
}
