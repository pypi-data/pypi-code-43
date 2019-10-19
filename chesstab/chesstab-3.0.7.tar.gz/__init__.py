# __init__.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""View a database of chess games created from data in PGN format.

Run "python -m chesstab.chessgames" assuming chesstab is in site-packages and
Python3.3 or later is the system Python.

PGN is "Portable Game Notation", the standard non-proprietary format for files
of chess game scores.

Sqlite3 via the apsw or sqlite packages, Berkeley DB via the db package, or DPT
via the dpt package, can be used as the database engine.

When importing games while running under Wine it will probably be necessary to
use the module "chessgames_winedptchunk".  The only known reason to run under
Wine is to use the DPT database engine on a platform other than Microsoft
Windows.
"""

from solentware_base.api.constants import (
    BSDDB_MODULE,
    BSDDB3_MODULE,
    DPT_MODULE,
    SQLITE3_MODULE,
    APSW_MODULE,
    )

APPLICATION_NAME = 'ChessTab'
ERROR_LOG = 'ErrorLog'

# Berkeley DB interface module name
_DBCHESS = 'chesstab.db.chessdb'

# DPT interface module name
_DPTCHESS = 'chesstab.dpt.chessdpt'

# sqlite3 interface module name
_SQLITE3CHESS = 'chesstab.sqlite.chesssqlite3'

# apsw interface module name
_APSWCHESS = 'chesstab.apsw.chessapsw'

# Map database module names to application module
APPLICATION_DATABASE_MODULE = {
    BSDDB_MODULE: _DBCHESS,
    BSDDB3_MODULE: _DBCHESS,
    SQLITE3_MODULE: _SQLITE3CHESS,
    APSW_MODULE: _APSWCHESS,
    DPT_MODULE: _DPTCHESS,
    }

# Berkeley DB partial position dataset module name
_DBPARTIALPOSITION = 'chesstab.db.dbcql'

# DPT partial position dataset module name
_DPTPARTIALPOSITION = 'chesstab.dpt.dptcql'

# sqlite3 partial position dataset module name
_SQLITE3PARTIALPOSITION = 'chesstab.sqlite.sqlite3cql'

# apsw partial position dataset module name
_APSWPARTIALPOSITION = 'chesstab.apsw.apswcql'

# Map database module names to partial position dataset module
PARTIAL_POSITION_MODULE = {
    BSDDB_MODULE: _DBPARTIALPOSITION,
    BSDDB3_MODULE: _DBPARTIALPOSITION,
    SQLITE3_MODULE: _SQLITE3PARTIALPOSITION,
    APSW_MODULE: _APSWPARTIALPOSITION,
    DPT_MODULE: _DPTPARTIALPOSITION,
    }

# Berkeley DB full position dataset module name
_DBFULLPOSITION = 'chesstab.db.dbfullpos'

# DPT full dataset module name
_DPTFULLPOSITION = 'chesstab.dpt.dptfullpos'

# sqlite3 full dataset module name
_SQLITE3FULLPOSITION = 'chesstab.sqlite.sqlite3fullpos'

# apsw full dataset module name
_APSWFULLPOSITION = 'chesstab.apsw.apswfullpos'

# Map database module names to full position dataset module
FULL_POSITION_MODULE = {
    BSDDB_MODULE: _DBFULLPOSITION,
    BSDDB3_MODULE: _DBFULLPOSITION,
    SQLITE3_MODULE: _SQLITE3FULLPOSITION,
    APSW_MODULE: _APSWFULLPOSITION,
    DPT_MODULE: _DPTFULLPOSITION,
    }

# Berkeley DB analysis dataset module name
_DBANALYSIS = 'chesstab.db.dbanalysis'

# DPT analysis dataset module name
_DPTANALYSIS = 'chesstab.dpt.dptanalysis'

# sqlite3 analysis dataset module name
_SQLITE3ANALYSIS = 'chesstab.sqlite.sqlite3analysis'

# apsw analysis dataset module name
_APSWANALYSIS = 'chesstab.apsw.apswanalysis'

# Map database module names to analysis dataset module
ANALYSIS_MODULE = {
    BSDDB_MODULE: _DBANALYSIS,
    BSDDB3_MODULE: _DBANALYSIS,
    SQLITE3_MODULE: _SQLITE3ANALYSIS,
    APSW_MODULE: _APSWANALYSIS,
    DPT_MODULE: _DPTANALYSIS,
    }

# Berkeley DB selection rules dataset module name
_DBSELECTION = 'chesstab.db.dbselection'

# DPT selection rules dataset module name
_DPTSELECTION = 'chesstab.dpt.dptselection'

# sqlite3 selection rules dataset module name
_SQLITE3SELECTION = 'chesstab.sqlite.sqlite3selection'

# apsw selection rules dataset module name
_APSWSELECTION = 'chesstab.apsw.apswselection'

# Map database module names to selection rules dataset module
SELECTION_MODULE = {
    BSDDB_MODULE: _DBSELECTION,
    BSDDB3_MODULE: _DBSELECTION,
    SQLITE3_MODULE: _SQLITE3SELECTION,
    APSW_MODULE: _APSWSELECTION,
    DPT_MODULE: _DPTSELECTION,
    }
