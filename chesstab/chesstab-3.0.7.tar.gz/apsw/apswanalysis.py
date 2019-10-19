# apswanalysis.py
# Copyright 2015 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""sqlite3 interface to chess database for chess engine analysis index.
"""

# This line should be the only substantive difference between: 
# apsw/sqlite3analysisbit.py
# db/dbanalysisbit.py
# sqlite/sqlite3analysisbit.py
# Some rearrangement removing these three modules should be possible; and might
# include the dpt version too.
from solentware_grid.apsw.apswdatasource import Sqlite3DataSource

from ..core.filespec import (
    VARIATION_FIELD_DEF,
    ENGINE_FIELD_DEF,
    ANALYSIS_FILE_DEF,
    )


class AnalysisDS(Sqlite3DataSource):
    
    """Extend to represent chess engine analysis on file that match postion.

    Notes:

    The find_*() methods should migrate to the database engine modules and the
    get_*() methods should migrate to a ../core/? module.
    
    """

    def __init__(self, dbhome, dbset, dbname, newrow=None):
        super().__init__(dbhome, dbset, dbname, newrow=newrow)

        # FEN and engine used to do analysis.
        self.engine = None
        self.fen = None

    def find_position_analysis(self, fen):
        """Find analysis records matching fen position.
        """
        self.engine = None
        self.fen = None
        if not fen:
            self.set_recordset(self.dbhome.make_recordset(self.dbset))
            return
            
        recordset = self.dbhome.make_recordset_key(
            self.dbset, VARIATION_FIELD_DEF, fen)

        self.set_recordset(recordset)
        self.fen = fen

    def find_engine_analysis(self, engine):
        """Find analysis records matching engine.
        """
        self.engine = None
        self.fen = None
        if not engine:
            self.set_recordset(self.dbhome.make_recordset(self.dbset))
            return
            
        recordset = self.dbhome.make_recordset_key(
            self.dbset, ENGINE_FIELD_DEF, engine)

        self.set_recordset(recordset)
        self.engine = engine

    def find_engine_position_analysis(self, engine=None, fen=None):
        """Find analysis records matching engine and fen.
        """
        self.engine = None
        self.fen = None
        if not engine:
            if not fen:
                self.set_recordset(self.dbhome.make_recordset(self.dbset))
            else:
                self.find_position_analysis(fen)
            return
        elif not fen:
            self.find_engine_analysis(engine)
            return
            
        fenset = self.dbhome.make_recordset_key(
            self.dbset, VARIATION_FIELD_DEF, fen)

        # Inefficient, should do just the non-empty segments in fenset.
        engineset = self.dbhome.make_recordset_key(
            self.dbset, ENGINE_FIELD_DEF, engine)
        self.set_recordset(engineset & fenset)

        self.engine = engine
        self.fen = fen

    def get_position_analysis(self, fen):
        """Get analysis matching fen position.

        It is assumed merging data from all records matching fen makes sense.

        """
        self.find_position_analysis(fen)
        analysis = self.newrow().value
        ar = self.newrow()
        arv = ar.value
        rsc = self.get_cursor()
        try:
            r = rsc.first()
            while r:
                ar.load_record(r)
                analysis.scale.update(arv.scale)
                analysis.variations.update(arv.variations)
                r = rsc.next()
            else:
                analysis.position = fen
            return analysis
        finally:
            rsc.close()

    def get_position_analysis_records(self, fen):
        """Return list of analysis records matching fen position."""
        self.find_position_analysis(fen)
        records = []
        rsc = self.get_cursor()
        try:
            r = rsc.first()
            while r:
                ar = self.newrow()
                ar.load_record(r)
                records.append(ar)
                r = rsc.next()
            return records
        finally:
            rsc.close()
