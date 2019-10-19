# chessdbdu.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess database update using custom deferred update for Berkeley DB.
"""

import os
import zipfile

# bsddb removed from Python 3.n
try:
    from bsddb3.db import (
        DB_CREATE,
        DB_RECOVER,
        DB_INIT_MPOOL,
        DB_INIT_LOCK,
        DB_INIT_LOG,
        DB_INIT_TXN,
        DB_PRIVATE,
        )
except ImportError:
    from bsddb.db import (
        DB_CREATE,
        DB_RECOVER,
        DB_INIT_MPOOL,
        DB_INIT_LOCK,
        DB_INIT_LOG,
        DB_INIT_TXN,
        DB_PRIVATE,
        )

from solentware_base.dbduapi import DBduapi, DBduapiError
from solentware_base.api.constants import FILEDESC
from solentware_base.api.segmentsize import SegmentSize

from ..core.filespec import (
    FileSpec,
    GAMES_FILE_DEF,
    DB_ENVIRONMENT_GIGABYTES,
    DB_ENVIRONMENT_BYTES,
    )
from ..core.chessrecord import ChessDBrecordGameImport


def chess_dbdu(
    dbpath,
    pgnpaths,
    file_records,
    reporter=lambda text, timestamp=True: None):
    """Open database, import games and close database."""
    cdb = ChessDatabase(dbpath, allowcreate=True)
    importer = ChessDBrecordGameImport()
    if cdb.open_context():
        cdb.set_defer_update(db=GAMES_FILE_DEF)
        for pp in pgnpaths:
            s = open(pp, 'r', encoding='iso-8859-1')
            importer.import_pgn(cdb, s, pp, reporter=reporter)
            s.close()
        if reporter is not None:
            reporter('Finishing import: please wait.')
            reporter('', timestamp=False)
        cdb.do_final_segment_deferred_updates(db=GAMES_FILE_DEF)
        cdb.unset_defer_update(db=GAMES_FILE_DEF)
    cdb.close_context()
    # There are no recoverable file full conditions for Berkeley DB (see DPT).
    return True


class ChessDatabase(DBduapi):

    """Provide custom deferred update for a database of games of chess.
    """
    # The optimum chunk size is the segment size.
    # Assuming 2Gb memory:
    # A default FreeBSD user process will not cause a MemoryError exception for
    # segment sizes up to 65536 records, so the optimum chunk size defined in
    # the superclass will be selected.
    # A MS Windows XP process will cause the MemoryError exeption which selects
    # the 32768 game chunk size.
    # A default OpenBSD user process will cause the MemoryError exception which
    # selects the 16384 game chunk size.
    # The error log problem fixed at chesstab-0.41.9 obscured what was actually
    # happening: OpenBSD gives a MemoryError exception but MS Windows XP heads
    # for thrashing swap space in some runs with a 65536 chunk size (depending
    # on order of processing indexes I think). Windows 10 Task Manager display
    # made this obvious.
    # The MemoryError exception or swap space thrashing will likely not occur
    # for a default OpenBSD user process or a MS Windows XP process with segment
    # sizes up to 32768 records. Monitoring with Top and Task Manager suggests
    # it gets close with OpenBSD.
    if SegmentSize.db_segment_size > 32768:
        for f, m in ((4, 700000000), (2, 1400000000)):
            try:
                b' ' * m
            except MemoryError:

                # Override the value in the superclass.
                deferred_update_points = frozenset(
                    [i for i in range(65536//f-1,
                                      SegmentSize.db_segment_size,
                                      65536//f)])
                
                break
        del f, m

    def __init__(self, DBfile, **kargs):
        """Define chess database.

        **kargs
        allowcreate == False - remove file descriptions from FileSpec so
        that superclass cannot create them.
        Other arguments are passed through to superclass __init__.
        
        """
        dbnames = FileSpec(**kargs)
        environment = {'flags': (DB_CREATE |
                                 DB_RECOVER |
                                 DB_INIT_MPOOL |
                                 DB_INIT_LOCK |
                                 DB_INIT_LOG |
                                 DB_INIT_TXN |
                                 DB_PRIVATE),
                       'gbytes': DB_ENVIRONMENT_GIGABYTES,
                       'bytes': DB_ENVIRONMENT_BYTES,
                       }
        # Deferred update for games file only
        for dd in list(dbnames.keys()):
            if dd != GAMES_FILE_DEF:
                del dbnames[dd]

        if not kargs.get('allowcreate', False):
            try:
                for dd in dbnames:
                    if FILEDESC in dbnames[dd]:
                        del dbnames[dd][FILEDESC]
            except:
                if __name__ == '__main__':
                    raise
                else:
                    raise DBduapiError('DB description invalid')

        try:
            super(ChessDatabase, self).__init__(
                dbnames,
                DBfile,
                environment)
        except DBduapiError:
            if __name__ == '__main__':
                raise
            else:
                raise DBduapiError('DB description invalid')
    
        self.set_defer_limit(20000)
    
    def open_context_prepare_import(self):
        """Return True

        No preparation actions thet need database open for Berkeley DB.

        """
        #return super(ChessDatabaseDeferred, self).open_context()
        return True
    
    def get_archive_names(self, files=()):
        """Return specified files and existing operating system files"""
        table_indicies = self.get_table_indicies()
        specs = {f for f in files
                 if self.get_table_index(f, f) in table_indicies}
        names = dict()
        for s in specs:
            v = self.get_database_instance(s, s)
            ns = names[os.path.join(
                self.get_database_folder(), v.get_database_file())] = []
            for v in self.get_associated_indicies(s):
                ns.append(self.get_database_instance(s, v))
        exists = [os.path.basename(n)
                  for n in names if os.path.exists('.'.join((n, 'zip')))]
        return (names, exists)

    def archive(self, flag=None, names=None):
        """Write a zip backup of files containing games.

        Intended to be a backup in case import fails.

        """
        if names is None:
            return False
        if not self.delete_archive(flag=flag, names=names):
            return
        if flag:
            for n in names:
                archiveguard = '.'.join((n, 'grd'))
                archivefile = '.'.join((n, 'zip'))
                c = zipfile.ZipFile(
                    archivefile,
                    mode='w',
                    compression=zipfile.ZIP_DEFLATED,
                    allowZip64=True)
                for s in names[n]:
                    an = os.path.join(s.get_database_file())
                    fn = os.path.join(
                        self.get_database_folder(), s.get_database_file())
                    c.write(fn, arcname=an)
                c.close()
                c = open(archiveguard, 'wb')
                c.close()
        return True

    def delete_archive(self, flag=None, names=None):
        """Delete a zip backup of files containing games."""
        if names is None:
            return False
        if flag:
            not_backups = []
            for n in names:
                archiveguard = '.'.join((n, 'grd'))
                archivefile = '.'.join((n, 'zip'))
                if not os.path.exists(archivefile):
                    try:
                        os.remove(archiveguard)
                    except:
                        pass
                    continue
                c = zipfile.ZipFile(
                    archivefile,
                    mode='r',
                    compression=zipfile.ZIP_DEFLATED,
                    allowZip64=True)
                namelist = c.namelist()
                sn = {os.path.join(
                    self.get_database_folder(), s.get_database_file())
                      for s in names[n]}
                extract = [e for e in namelist
                           if os.path.join(self.get_database_folder(), e) in sn]
                if len(extract) != len(namelist):
                    not_backups.append(os.path.basename(archivefile))
                    c.close()
                    continue
                c.close()
                try:
                    os.remove(archiveguard)
                except:
                    pass
                try:
                    os.remove(archivefile)
                except:
                    pass
            if not_backups:
                return
        return True

    def add_import_buttons(self, *a):
        """Add button actions for Berkeley DB to Import dialogue.

        None required.  Method exists for DPT compatibility.

        """
        pass

    def get_file_sizes(self):
        """Return an empty dictionary.

        No sizes needed.  Method exists for DPT compatibility.

        """
        return dict()

    def report_plans_for_estimate(self, estimates, reporter):
        """Remind user to check estimated time to do import.

        No planning needed.  Method exists for DPT compatibility.

        """
        # See comment near end of class definition Chess in relative module
        # ..gui.chess for explanation of this change.
        #reporter.append_text_only(''.join(
        #    ('The expected duration of the import may make starting ',
        #     'it now inconvenient.',
        #     )))
        #reporter.append_text_only('')
