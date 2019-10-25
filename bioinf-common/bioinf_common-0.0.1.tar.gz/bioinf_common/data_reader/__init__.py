from .biogrid import load_biogrid
from .stringdb import load_stringdb

from .cosmic import load_cosmic

from .go import load_goterms
from .msigdb import load_msigdb
from .kegg import load_kegg_database


__all__ = [
    'load_biogrid', 'load_stringdb', 'load_cosmic',
    'load_goterms', 'load_msigdb', 'load_kegg_database'
]
