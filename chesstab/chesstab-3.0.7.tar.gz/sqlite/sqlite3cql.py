# sqlite3cql.py
# Copyright 2016 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""sqlite3 interface to chess database partial position index using ChessQL.

The ChessQueryLanguageDS class represents a subset of games which match a Chess
Query Language query.

"""

from solentware_base.api.find import Find

from solentware_grid.sqlite.sqlite3datasource import Sqlite3DataSource

from ..basecore.cqlgames import ChessQLGames


class ChessQueryLanguageDS(Sqlite3DataSource, ChessQLGames):
    
    """Represent subset of games that match a Chess Query Language query."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        # recordclass argument must be used to support non-index field finds.
        self.cqlfinder = Find(self.dbhome, self.dbset)

        self.not_implemented = set()
