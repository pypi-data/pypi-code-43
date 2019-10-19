# dptfullpos.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""DPT interface to chess database for full position index.
"""

from dptdb import dptapi

from solentware_grid.dpt.dptdatasource import DPTDataSource

from ..core.filespec import POSITIONS_FIELD_DEF


class FullPositionDS(DPTDataSource):
    
    """Extend to represent subset of games on file that match a postion.
    """

    def __init__(self, dbhome, dbset, dbname, newrow=None):
        """Extend to provide placeholder for position used to select games.
        """
        super(FullPositionDS, self).__init__(
            dbhome, dbset, dbname, newrow=newrow)
        # Position used as key to select games
        self.fullposition = None

    def get_full_position_games(self, fullposition):
        """Find game records matching full position."""
        self.fullposition = None

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

        positiongames = gamedb.FindRecords(
            dptapi.APIFindSpecification(
                self.dbhome.database_definition[
                    self.dbset].secondary[POSITIONS_FIELD_DEF],
                dptapi.FD_EQ,
                dptapi.APIFieldValue(
                    self.dbhome.encode_record_selector(fullposition))),
            dptapi.FD_LOCK_SHR)
        games.Place(positiongames)
        gamedb.DestroyRecordSet(positiongames)

        self.set_recordset(games)
        self.fullposition = fullposition
