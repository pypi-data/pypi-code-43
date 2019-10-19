# dptanalysis.py
# Copyright 2015 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""DPT interface to chess database for chess engine analysis index.
"""

from dptdb import dptapi

from solentware_grid.dpt.dptdatasource import DPTDataSource

from ..core.filespec import (
    VARIATION_FIELD_DEF,
    ENGINE_FIELD_DEF,
    ANALYSIS_FILE_DEF,
    )


class AnalysisDS(DPTDataSource):
    
    """Extend to represent chess engine analysis on file that match postion.
    """

    def __init__(self, dbhome, dbset, dbname, newrow=None):
        """Extend to provide placeholder for position used to select games.
        """
        super().__init__(dbhome, dbset, dbname, newrow=newrow)

        # FEN and engine used to do analysis.
        self.engine = None
        self.fen = None

    def find_position_analysis(self, fen):
        """Find analysis records matching fen position."""
        self.engine = None
        self.fen = None

        gamedb = self.dbhome.get_database(self.dbset, self.dbname)
        # This test copes with databases unavailable while Import in progress.
        # Proper solution awaits implementation of general solentware_grid
        # support.
        if gamedb is None:
            return
        analysis = gamedb.CreateRecordList()
        if not fen:
            self.set_recordset(analysis)
            return

        positionanalysis = gamedb.FindRecords(
            dptapi.APIFindSpecification(
                self.dbhome.database_definition[
                    self.dbset].secondary[VARIATION_FIELD_DEF],
                dptapi.FD_EQ,
                dptapi.APIFieldValue(fen)),
            dptapi.FD_LOCK_SHR)
        analysis.Place(positionanalysis)
        gamedb.DestroyRecordSet(positionanalysis)

        self.set_recordset(analysis)
        self.fen = fen

    def find_engine_analysis(self, engine):
        """Find analysis records matching engine."""
        self.engine = None
        self.fen = None

        gamedb = self.dbhome.get_database(self.dbset, self.dbname)
        # This test copes with databases unavailable while Import in progress.
        # Proper solution awaits implementation of general solentware_grid
        # support.
        if gamedb is None:
            return
        analysis = gamedb.CreateRecordList()
        if not engine:
            self.set_recordset(analysis)
            return

        positionanalysis = gamedb.FindRecords(
            dptapi.APIFindSpecification(
                self.dbhome.database_definition[
                    self.dbset].secondary[ENGINE_FIELD_DEF],
                dptapi.FD_EQ,
                dptapi.APIFieldValue(engine)),
            dptapi.FD_LOCK_SHR)
        analysis.Place(positionanalysis)
        gamedb.DestroyRecordSet(positionanalysis)

        self.set_recordset(analysis)
        self.engine = engine

    def find_engine_position_analysis(self, engine=None, fen=None):
        """Find analysis records matching engine and fen."""
        self.engine = None
        self.fen = None

        gamedb = self.dbhome.get_database(self.dbset, self.dbname)
        # This test copes with databases unavailable while Import in progress.
        # Proper solution awaits implementation of general solentware_grid
        # support.
        if gamedb is None:
            return
        if not engine:
            if not fen:
                self.set_recordset(gamedb.CreateRecordList())
            else:
                self.find_position_analysis(fen)
            return
        elif not fen:
            self.find_engine_analysis(engine)
            return

        fenanalysis = gamedb.FindRecords(
            dptapi.APIFindSpecification(
                self.dbhome.database_definition[
                    self.dbset].secondary[VARIATION_FIELD_DEF],
                dptapi.FD_EQ,
                dptapi.APIFieldValue(fen)),
            dptapi.FD_LOCK_SHR)
        engineanalysis = gamedb.FindRecords(
            dptapi.APIFindSpecification(
                self.dbhome.database_definition[
                    self.dbset].secondary[ENGINE_FIELD_DEF],
                dptapi.FD_EQ,
                dptapi.APIFieldValue(engine)),
            dptapi.FD_LOCK_SHR)

        gash = gamedb.CreateRecordList()
        gash.Place(fenanalysis)
        gash.Remove(engineanalysis)
        analysis = gamedb.CreateRecordList()
        analysis.Place(fenanalysis)
        analysis.Remove(gash)
        gamedb.DestroyRecordSet(fenanalysis)
        gamedb.DestroyRecordSet(engineanalysis)

        self.set_recordset(analysis)
        self.engine = engine
        self.fen = fen

    def get_position_analysis(self, fen):
        """Get analysis matching fen position.

        It is assumed merging data from all records matching fen makes sense.

        """
        self.find_position_analysis(fen)
        rsc = self.dbhome.create_recordset_cursor(
            self.dbset, self.dbset, self.recordset)
        analysis = self.newrow().value
        ar = self.newrow()
        arv = ar.value
        r = rsc.first()
        while r:
            ar.load_record(r)
            analysis.scale.update(arv.scale)
            analysis.variations.update(arv.variations)
            r = rsc.next()
        else:
            analysis.position = fen
        analysis.position = fen
        return analysis

    def get_position_analysis_records(self, fen):
        """Return list of analysis records matching fen position."""
        self.find_position_analysis(fen)
        records = []
        rsc = self.dbhome.create_recordset_cursor(
            self.dbset, self.dbset, self.recordset)
        r = rsc.first()
        while r:
            ar = self.newrow()
            ar.load_record(r)
            records.append(ar)
            r = rsc.next()
        return records
