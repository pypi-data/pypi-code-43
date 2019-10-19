# dptselection.py
# Copyright 2016 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""DPT interface to chess database for selection rules index.
"""

from dptdb import dptapi

from solentware_grid.dpt.dptdatasource import DPTDataSource


class SelectionDS(DPTDataSource):
    
    """Extend to represent subset of games on file that match a selection rule.
    """

    def __init__(self, dbhome, dbset, dbname, newrow=None):
        super(SelectionDS, self).__init__(
            dbhome, dbset, dbname, newrow=newrow)

    def get_selection_rule_games(self, fullposition):
        """Find game records matching selection rule.
        """
        gamedb = self.dbhome.get_database(self.dbset, self.dbname)

        # This test copes with databases unavailable while Import in progress.
        # Proper solution awaits implementation of general solentware_grid
        # support.
        if gamedb is None:
            return

        games = gamedb.CreateRecordList()
        if not fullposition:
            self.set_recordset(games)
            return
        self.set_recordset(fullposition)
