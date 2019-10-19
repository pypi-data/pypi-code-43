# chessdptdu.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess database update using DPT single-step deferred update.

This module on Windows only.  Use multi-step module on Wine because Wine
support for a critical function used by single-step is not reliable. There
is no sure way to spot that module is running on Wine.

See www.dptoolkit.com for details of DPT

"""

import os
import bz2

from io import StringIO

from dptdb.dptapi import (
    FILEDISP_OLD,
    FISTAT_DEFERRED_UPDATES,
    APIContextSpecification,
    )

from solentware_base.dptduapi import DPTduapi, DPTduapiError
from solentware_base.api.constants import FILEDESC, BRECPPG, BSIZE, DSIZE, TABLE_B_SIZE
from solentware_misc.workarounds import dialogues

from ..core.filespec import (
    FileSpec,
    GAMES_FILE_DEF,
    PIECES_PER_POSITION,
    POSITIONS_PER_GAME,
    )
from ..core.chessrecord import ChessDBrecordGameImport

# Current practical way to determine if running on Wine, taking advantage of
# a problem found in ..core.uci which prevents UCI chess engines being used to
# do position analysis in this environment.  Here the consequence is Wine's
# useless answers to queries about memory usage made within DPT and the impact
# on the useful frequency of progress reports.
# CHUNKGAMES deals this this under Wine.  A safe value for a PC with 2Gb memory
# is 6144.  Almost get away with 8192 but it seems system housekeeping tasks,
# if nothing else, will cause this to fail at some point during a large import.
# Must be safe to add 8192 for every extra 2Gb, and possibly every extra 1Gb
# assuming system tasks are not greedy with the extra memory.
# The DPT segment size is 65280 because 32 bytes are reserved and 8160 bytes of
# the 8192 byte page are used for the bitmap.  Use 65536 as segment size and
# ignore the DPT segment size so report points are similar to other database
# engines.
# DB_SEGMENT_SIZE has no effect on processing apart from report points.
DB_SEGMENT_SIZE = 65536
import multiprocessing
try:
    multiprocessing.Queue()
    _DEFERRED_UPDATE_POINTS = DB_SEGMENT_SIZE - 1,
except OSError:
    _DEFERRED_UPDATE_POINTS = tuple(
        [i for i in range(DB_SEGMENT_SIZE//8-1,
                          DB_SEGMENT_SIZE,
                          DB_SEGMENT_SIZE//8)])
del multiprocessing
del DB_SEGMENT_SIZE
CHUNKGAMES = 6144


def chess_dptdu(
    dbpath,
    pgnpaths,
    file_records,
    reporter=lambda text, timestamp=True: None):
    """Open database, import games and close database."""
    cdb = ChessDatabase(dbpath, allowcreate=True)
    importer = ChessDBrecordGameImport()
    if cdb.open_context(files=file_records):
        for pp in pgnpaths:
            s = open(pp, 'r', encoding='iso-8859-1')
            importer.import_pgn(cdb, s, pp, reporter=reporter)
            s.close()
        reporter('Finishing import: please wait.')
        reporter('', timestamp=False)
    cdb.close_context()
    cdb.open_context_allocated(files=file_records)
    status = True
    for f in file_records:
        if (FISTAT_DEFERRED_UPDATES !=
            cdb.get_database_instance(
                f, None).get_file_parameters(cdb.dbservices)['FISTAT'][0]):
            status = False
    cdb.close_context()
    return status


def chess_dptdu_chunks(
    dbpath,
    pgnpaths,
    file_records,
    reporter=lambda text, timestamp=True: None):
    """Open database, import games in fixed chunks and close database."""

    def write_chunk(sample=None):
        if cdb.open_context(files=sample):

            # chess_dptdu_chunks does the reporting so do not pass reporter to
            # import_pgn, but the name of the source file is mandantory.
            importer.import_pgn(cdb,
                                StringIO(''.join(games)),
                                pp)
            
        cdb.close_context()
        games[:] = []

    cdb = ChessDatabase(dbpath, allowcreate=True)
    importer = ChessDBrecordGameImport()
    chunks = []
    games = []
    gamelines = []
    newgamestring = '[Event "'
    records = file_records
    for pp in pgnpaths:
        cdb._text_file_size = os.path.getsize(pp)
        inp = open(pp, 'r', encoding='iso-8859-1')
        line = inp.readline()
        reporter('Extracting games from ' + pp)
        count = 0
        while line:
            if line.startswith(newgamestring):
                games.append(''.join(gamelines))
                gamelines = []
                if len(games) >= CHUNKGAMES:
                    records = write_chunk(sample=records)
                    count += 1
                    reporter(' '.join(('Chunk',
                                       str(count),
                                       'written, total games added:',
                                       str(CHUNKGAMES * count),
                                       )))
            gamelines.append(line)
            line = inp.readline()
        inp.close()
        if gamelines:
            games.append(''.join(gamelines))
            records = write_chunk(sample=records)
        reporter('Extraction from ' + pp + ' done')
        reporter('', timestamp=False)
    reporter('Finishing import: please wait.')
    reporter('', timestamp=False)
    cdb.open_context_allocated(files=file_records)
    status = True
    for f in file_records:
        if (FISTAT_DEFERRED_UPDATES !=
            cdb.get_database_instance(
                f, None).get_file_parameters(cdb.dbservices)['FISTAT'][0]):
            status = False
    cdb.close_context()
    return status


class ChessDatabaseDeferred(object):

    """Provide deferred update methods for a database of games of chess.

    Subclasses must include a subclass of dptbase.Database as a superclass.
    
    """
    # ChessDatabaseDeferred.deferred_update_points is not needed in DPT, like
    # the similar attribute in chessdbbitdu.ChessDatabase for example, because
    # DPT does it's own memory management for deferred updates.
    # The same attribute is provided to allow the import_pgn method called in
    # this module's chess_dptdu and chess_dptdu_chunks functions to report
    # progress at regular intervals.
    # The values are set differently because Wine does not give a useful answer
    # to DPT's memory usage questions.
    deferred_update_points = frozenset(_DEFERRED_UPDATE_POINTS)

    def __init__(self, databasefolder, **kargs):
        """Define chess database.

        **kargs
        allowcreate == False - remove file descriptions from FileSpec so
        that superclass cannot create them.
        Other arguments are passed through to superclass __init__.
        
        """
        ddnames = FileSpec(**kargs)
        # Deferred update for games file only
        for dd in list(ddnames.keys()):
            if dd != GAMES_FILE_DEF:
                del ddnames[dd]

        if not kargs.get('allowcreate', False):
            try:
                for dd in ddnames:
                    if FILEDESC in ddnames[dd]:
                        del ddnames[dd][FILEDESC]
            except:
                if __name__ == '__main__':
                    raise
                else:
                    raise DPTduapiError('DPT description invalid')

        try:
            super(ChessDatabaseDeferred, self).__init__(
                ddnames,
                databasefolder,
                **kargs)
        except DPTduapiError:
            if __name__ == '__main__':
                raise
            else:
                raise DPTduapiError('DPT description invalid')

        # Retain import estimates for increase size by button actions
        self._import_estimates = None
        self._notional_record_counts = None
        # Methods passed by UI to populate report widgets
        self._reporter = None

    def open_context(self, files=None):
        """Open all files if they are in DEFERRED_UPDATE mode."""
        oc = super(ChessDatabaseDeferred, self).open_context()
        if oc:
            vr = self.dbservices.Core().GetViewerResetter()
            for dbo in self.database_definition.values():
                if vr.ViewAsInt(
                    'FISTAT',
                    dbo.get_database()) != FISTAT_DEFERRED_UPDATES:
                    break
            else:
                if files is None:
                    files = dict()
                self.increase_database_size(files=files)
                return oc
            self.close_database()
            raise DPTduapiError('A file is not in deferred update mode')
        return oc
    
    def open_context_prepare_import(self):
        """Open all files normally"""
        return super(ChessDatabaseDeferred, self).open_context()
    
    def get_archive_names(self, files=()):
        """Return specified files and existing operating system files"""
        specs = {f for f in files if f in self.database_definition}
        names = [v._file for k, v in self.database_definition.items()
                 if k in specs]
        exists = [os.path.basename(n)
                  for n in names if os.path.exists('.'.join((n, 'bz2')))]
        return (names, exists)

    def get_pages_for_record_counts(self, counts=(0, 0)):
        """Return Table B and Table D pages needed for record counts"""
        brecppg = self.database_definition[GAMES_FILE_DEF]._filedesc[BRECPPG]
        return (
            counts[0] // brecppg,
            (counts[1] * self.database_definition[GAMES_FILE_DEF]._btod_factor
             ) // brecppg,
            )

    def archive(self, flag=None, names=None):
        """Write a bz2 backup of file containing games.

        Intended to be a backup in case import fails.

        """
        if names is None:
            return False
        if not self.delete_archive(flag=flag, names=names):
            return
        if flag:
            for n in names:
                c = bz2.BZ2Compressor()
                archiveguard = '.'.join((n, 'grd'))
                archivename = '.'.join((n, 'bz2'))
                fi = open(n, 'rb')
                fo = open(archivename, 'wb')
                inp = fi.read(10000000)
                while inp:
                    co = c.compress(inp)
                    if co:
                        fo.write(co)
                    inp = fi.read(10000000)
                co = c.flush()
                if co:
                    fo.write(co)
                fo.close()
                fi.close()
                c = open(archiveguard, 'wb')
                c.close()
        return True

    def delete_archive(self, flag=None, names=None):
        """Delete a bz2 backup of file containing games."""
        if names is None:
            return False
        if flag:
            for n in names:
                archiveguard = '.'.join((n, 'grd'))
                archivename = '.'.join((n, 'bz2'))
                try:
                    os.remove(archiveguard)
                except:
                    pass
                try:
                    os.remove(archivename)
                except:
                    pass
        return True

    def get_database_table_sizes(self, files=None):
        """Return Table B and D size and usage in pages for files."""
        if files is None:
            files = dict()
        fs = dict()
        for k, v in self.get_database_parameters(
            files=list(files.keys())).items():
            fs[k] = (v['BSIZE'], v['BHIGHPG'], v['DSIZE'], v['DPGSUSED'])
        fi = self.get_database_increase(files=files)
        self.close_context()
        return fs, fi

    def add_import_buttons(self,
                           master,
                           try_command_wrapper,
                           try_event_wrapper,
                           widget,
                           tkinter_module):
        """Add button actions for DPT to Import dialogue.

        Increase data and index space available.

        """
        index = tkinter_module.Button(
            master=master,
            text='Increase Index',
            underline=13,
            command=try_command_wrapper(
                self._increase_index, master))
        index.pack(side=tkinter_module.RIGHT, padx=12)
        widget.bind('<Alt-x>', try_event_wrapper(self._increase_index))
        data = tkinter_module.Button(
            master=master,
            text='Increase Data',
            underline=9,
            command=try_command_wrapper(
                self._increase_data, master))
        data.pack(side=tkinter_module.RIGHT, padx=12)
        widget.bind('<Alt-d>', try_event_wrapper(self._increase_data))

    def _increase_data(self, event=None):
        """Add maximum of current free space and default size to Table B.

        event is ignored and is present for compatibility between button click
        and keypress,

        """
        self.open_context_normal(files=(GAMES_FILE_DEF,))
        increase_done = False
        for k, v in self.get_database_parameters(
            files=(GAMES_FILE_DEF,)).items():
            bsize = v['BSIZE']
            bused = max(0, v['BHIGHPG'])
            bneeded = self.get_pages_for_record_counts(
                self._notional_record_counts[k])[0]
            bincrease = min(bneeded * 2, bsize - bused)
            message = ''.join(
                ('The free data size of the ',
                 k,
                 ' file will be increased from ',
                 str(bsize - bused),
                 ' pages to ',
                 str(bincrease + bsize - bused),
                 ' pages.'))
            if len(self.database_definition[k].get_extents()) % 2 == 0:
                 message = ''.join(
                     (message,
                      '\n\nAt present it is better to do index increases ',
                      'first for this file, if you need to do any, because ',
                      'a new extent (fragment) would not be needed.'))
            if dialogues.askyesno(
                title='Increase Data Size',
                message=''.join(
                    (message,
                     '\n\nDo you want to increase the data size?',
                     ))):
                increase_done = True
                self.database_definition[k].get_database().Increase(bincrease,
                                                                    False)
        if increase_done:
            self._reporter.append_text(
                ' '.join(
                    ('Recalculation of planned database size increases',
                     'after data size increase by user action.',
                     )))
            self._reporter.append_text_only('')
            self._report_plans_for_estimate()
        self.close_context()

    def _increase_index(self, event=None):
        """Add maximum of current free space and default size to Table D.

        event is ignored and is present for compatibility between button click
        and keypress,

        """
        self.open_context_normal(files=(GAMES_FILE_DEF,))
        increase_done = False
        for k, v in self.get_database_parameters(
            files=(GAMES_FILE_DEF,)).items():
            dsize = v['DSIZE']
            dused = v['DPGSUSED']
            dneeded = self.get_pages_for_record_counts(
                self._notional_record_counts[k])[1]
            dincrease = min(dneeded * 2, dsize - dused)
            message = ''.join(
                ('The free index size of the ',
                 k,
                 ' file will be increased from ',
                 str(dsize - dused),
                 ' pages to ',
                 str(dincrease + dsize - dused),
                 ' pages.'))
            if len(self.database_definition[k].get_extents()) % 2 != 0:
                 message = ''.join(
                     (message,
                      '\n\nAt present it is better to do data increases ',
                      'first for this file, if you need to do any, because ',
                      'a new extent (fragment) would not be needed.'))
            if dialogues.askyesno(
                title='Increase Index Size',
                message=''.join(
                    (message,
                     '\n\nDo you want to increase the index size?',
                     ))):
                increase_done = True
                self.database_definition[k].get_database().Increase(dincrease,
                                                                    True)
        if increase_done:
            self._reporter.append_text(
                ' '.join(
                    ('Recalculation of planned database size increases',
                     'after index size increase by user action.',
                     )))
            self._reporter.append_text_only('')
            self._report_plans_for_estimate()
        self.close_context()

    def get_file_sizes(self):
        """Return dictionary of notional record counts for data and index."""
        return self._notional_record_counts

    def report_plans_for_estimate(self, estimates, reporter):
        """Calculate and report file size adjustments to do import

        Note the reporter and headline methods for initial report and possible
        later recalculations.

        Pass estimates through to self._report_plans_for_estimate

        """
        # See comment near end of class definition Chess in relative module
        # ..gui.chess for explanation of this change.
        self._reporter = reporter
        self._report_plans_for_estimate(estimates=estimates)

    def _report_plans_for_estimate(self, estimates=None):
        """Recalculate and report file size adjustments to do import

        Create dictionary of effective game counts for sizing Games file.
        This will be passed to the import job which will increase Table B and
        Table D according to file specification.

        The counts for Table B and Table D can be different.  If the average
        data bytes per game is greater than Page size / Records per page the
        count must be increased to allow for the unused record numbers.  If
        the average positions per game or pieces per position are not the
        values used to calculate the steady-state ratio of Table B to Table D
        the count must be adjusted to compensate.

        """
        append_text = self._reporter.append_text
        append_text_only = self._reporter.append_text_only
        if estimates is not None:
            self._import_estimates = estimates
        (gamecount,
         bytes_per_game,
         positions_per_game,
         pieces_per_game,
         errorcount,
         bytes_per_error,
         estimate,
         gamesamplecount,
         errorsamplecount) = self._import_estimates[:9]
        brecppg = self.database_definition[GAMES_FILE_DEF]._filedesc[BRECPPG]
        d_count = (
            (gamecount * (positions_per_game + pieces_per_game)) //
            (POSITIONS_PER_GAME * (1 + PIECES_PER_POSITION)))
        if bytes_per_game > (TABLE_B_SIZE // brecppg):
            b_count = int(
                (gamecount * bytes_per_game) / (TABLE_B_SIZE / brecppg))
        else:
            b_count = gamecount
        self._notional_record_counts = {
            GAMES_FILE_DEF: (b_count, d_count),
            }
        append_text('Current file size and free space:')
        free = dict()
        sizes, increases = self.get_database_table_sizes(
            files=self._notional_record_counts)
        for fn, ds in sizes.items():
            bsize, bused, dsize, dused = ds
            bused = max(0, bused)
            free[fn] = (bsize - bused, dsize - dused)
            append_text_only(fn)
            append_text_only(
                ' '.join(('Current data area size', str(bsize), 'pages')))
            append_text_only(
                ' '.join(('Current index area size', str(dsize), 'pages')))
            append_text_only(
                ' '.join(
                    ('Current data area free', str(bsize - bused), 'pages')))
            append_text_only(
                ' '.join(
                    ('Current index area free', str(dsize - dused), 'pages')))
        append_text_only('')
        append_text('File space needed for import:')
        for fn, fc in self._notional_record_counts.items():
            append_text_only(fn)
            b, d = self.get_pages_for_record_counts(fc)
            append_text_only(
                ' '.join(('Estimated', str(b), 'pages needed for data')))
            append_text_only(
                ' '.join(('Estimated', str(d), 'pages needed for indexes')))
        append_text_only('')
        append_text(
            'File size increases planned and free space when done:')
        for fn, ti in increases.items():
            bi, di = ti
            bf, df = free[fn]
            append_text_only(fn)
            append_text_only(
                ' '.join(('Data area increase', str(bi), 'pages')))
            append_text_only(
                ' '.join(('Index area increase', str(di), 'pages')))
            append_text_only(
                ' '.join(('Data area free', str(bi + bf), 'pages')))
            append_text_only(
                ' '.join(('Index area free', str(di + df), 'pages')))
        append_text_only('')
        append_text_only(
            ''.join(
                ('Comparison of the required and free data or index ',
                 'space may justify using the Increase Data and, or, ',
                 'Increase Index actions to get more space immediately ',
                 'given your knowledge of the PGN file being imported.',
                 )))
        append_text_only('')
        append_text_only('')


class ChessDatabase(ChessDatabaseDeferred, DPTduapi):

    """Provide single-step deferred update for a database of games of chess.
    """
