# dbfullpos.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""bsddb interface to chess database for full position index
"""

from solentware_grid.db.dbdatasource import DBDataSource

from ..core.filespec import POSITIONS_FIELD_DEF


class FullPositionDS(DBDataSource):
    
    """Represent subset of games on file that match a postion.
    """

    def __init__(self, dbhome, dbset, dbname, newrow=None):
        """Extend to provide placeholder for position used to select games.
        """
        super(FullPositionDS, self).__init__(
            dbhome, dbset, dbname, newrow=newrow)
        # Position used as key to select games
        self.fullposition = None

    def get_full_position_games(self, fullposition):
        """Find game records matching full position.
        """
        self.fullposition = None
        if not fullposition:
            self.set_recordset(self.dbhome.make_recordset(self.dbset))
            return
            
        recordset = self.dbhome.make_recordset_key(
            self.dbset,
            POSITIONS_FIELD_DEF,
            self.dbhome.encode_record_selector(fullposition))

        self.set_recordset(recordset)
        self.fullposition = fullposition
