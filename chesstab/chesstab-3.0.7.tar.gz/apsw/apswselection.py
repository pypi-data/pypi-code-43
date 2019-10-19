# apswselection.py
# Copyright 2016 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""sqlite3 interface to chess database for selection rules index.
"""

from solentware_grid.apsw.apswdatasource import Sqlite3DataSource


class SelectionDS(Sqlite3DataSource):
    
    """Extend to represent subset of games on file that match a selection rule.
    """

    def __init__(self, dbhome, dbset, dbname, newrow=None):
        super(SelectionDS, self).__init__(
            dbhome, dbset, dbname, newrow=newrow)

    def get_selection_rule_games(self, fullposition):
        """Find game records matching selection rule.
        """
        if not fullposition:
            self.set_recordset(self.dbhome.make_recordset(self.dbset))
            return
        self.set_recordset(fullposition)
