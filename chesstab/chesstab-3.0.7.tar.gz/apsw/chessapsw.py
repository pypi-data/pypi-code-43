# chessapsw.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess database using sqlite3.
"""

import os
import bz2
import shutil
#from apsw import ConstraintError

from solentware_base.apswapi import Sqlite3api, Sqlite3apiError
from solentware_base.api.constants import (
    FILEDESC,
    )
from solentware_misc.workarounds import dialogues

from ..core.filespec import (
    FileSpec,
    NEWGAMES_FIELD_DEF,
    NEWGAMES_FIELD_VALUE,
    PARTIAL_FILE_DEF,
    )
from .. import APPLICATION_NAME, ERROR_LOG


class ChessDatabase(Sqlite3api):

    """Provide access to a database of games of chess.
    """

    def __init__(self, sqlite3file, **kargs):
        """Define chess database.

        **kargs
        allowcreate == False - remove file descriptions from FileSpec so
        that superclass cannot create them.
        Other arguments are passed through to superclass __init__.
        
        """
        names = FileSpec(**kargs)

        if not kargs.get('allowcreate', False):
            try:
                for t in names:
                    if FILEDESC in names[t]:
                        del names[t][FILEDESC]
            except:
                if __name__ == '__main__':
                    raise
                else:
                    raise Sqlite3apiError('sqlite3 description invalid')

        try:
            super(ChessDatabase, self).__init__(
                names,
                sqlite3file,
                **kargs)
        except Sqlite3apiError:
            if __name__ == '__main__':
                raise
            else:
                raise Sqlite3apiError('sqlite3 description invalid')

    def use_deferred_update_process(self, **kargs):
        """Return path to deferred update module.

        **kargs - soak up any arguments other database engines need.
        
        """
        return os.path.join(
            os.path.basename(os.path.dirname(__file__)),
            'runchessapswdu.py')

    def open_context(self):
        """Return True after doing database engine specific open actions."""
        oc = super(ChessDatabase, self).open_context()
        if not oc:
            dialogues.showinfo(
                title='Open',
                message=''.join(
                    (APPLICATION_NAME,
                     ' is unable to open the database.\n\nRestore the ',
                     'database from backups, or source data, before trying ',
                     'again.',
                     )),
                )
            return 'Unable to open database'
        return True

    def restore_dialogue(self, names=()):
        """Restore a file containing games from a bz2 backup.

        Intended to restore backups after an import fails.

        """
        exists = [os.path.basename(n)
                  for n in names if os.path.exists('.'.join((n, 'bz2')))]
        if not exists:
            return False
        return dialogues.askyesnocancel(
            title='Save broken files and Restore backups',
            message=''.join(
                ('An Import has just failed.\n\nImport backups of the ',
                 'following files exist.\n\n',
                 '\n'.join(exists),
                 '\n\nClick "Yes" to replace the probably broken files with ',
                 'their backups and save the replaced files for examination ',
                 'later.  The backups will then be deleted.\n\nClick "No" to ',
                 'replace the probably broken files with their backups ',
                 'without saving the replaced files for examination later.  ',
                 'The backups will then be deleted.\n\nClick "Cancel" to ',
                 'leave all files as they are for later action.',
                 )),
            )

    def dump_database(self, names=()):
        """Dump database in compressed files."""
        for n in names:
            c = bz2.BZ2Compressor()
            archivename = '.'.join((n, 'broken', 'bz2'))
            fi = open(n, 'rb')
            fo = open(archivename, 'wb')
            try:
                inp = fi.read(10000000)
                while inp:
                    co = c.compress(inp)
                    if co:
                        fo.write(co)
                    inp = fi.read(10000000)
                co = c.flush()
                if co:
                    fo.write(co)
            finally:
                fo.close()
                fi.close()

    def delete_backups(self, names=()):
        """Delete backup files."""
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

    def restore_backups(self, names=()):
        """Restore database from backup files."""
        for n in names:
            c = bz2.BZ2Decompressor()
            archivename = '.'.join((n, 'bz2'))
            fi = open(archivename, 'rb')
            fo = open(n, 'wb')
            try:
                inp = fi.read(1000000)
                while inp:
                    co = c.decompress(inp)
                    if co:
                        fo.write(co)
                    inp = fi.read(1000000)
            finally:
                fo.close()
                fi.close()
        return True

    def delete_database(self):
        """Close and delete the open chess database."""
        sqfile = self.get_database_home()
        names = {sqfile}
        basenames = set()
        listnames = []
        if len(listnames):
            dialogues.showinfo(
                title='Delete',
                message=''.join(
                    ('There is at least one file or folder in\n\n',
                     sqfile,
                     '\n\nwhich may not be part of the database.  These items ',
                     'will not be deleted by ', APPLICATION_NAME, '.',
                     ))
                )
        self.close_database()
        for n in names:
            if os.path.isdir(n):
                shutil.rmtree(n, ignore_errors=True)
            else:
                os.remove(n)
        try:
            d, f = os.path.split(sqfile)
            if f == os.path.basename(d):
                os.rmdir(d)
            os.rmdir(sqfile)
        except:
            pass
        return True

    def get_archive_names(self, files=()):
        """Return names and operating system files for archives and guards"""
        names = self.get_database_home(),
        archives = dict()
        guards = dict()
        for n in names:
            archiveguard = '.'.join((n, 'grd'))
            archivefile = '.'.join((n, 'bz2'))
            for d, f in ((archives, archivefile), (guards, archiveguard)):
                if os.path.exists(f):
                    d[n] = f
        return (names, archives, guards)

    def open_after_import_without_backups(self, **ka):
        """Return True after doing database engine specific open actions.

        For sqlite3 just call open_context.

        """
        oc = super(ChessDatabase, self).open_context()
        if not oc:
            return 'Files not opened'
        return True

    def open_after_import_with_backups(self, files=()):
        """Return True after doing database engine specific open actions.

        For sqlite3 just call open_context.

        """
        oc = super(ChessDatabase, self).open_context()
        if not oc:
            return 'Files not opened'
        return True

    def save_broken_database_details(self, files=()):
        """Save database engine specific detail of broken files to be restored.

        It is assumed that the Database Services object exists.

        """
        pass

    def adjust_database_for_retry_import(self, files):
        """Database engine specific actions to do before re-trying an import"""
        pass

    def mark_partial_positions_to_be_recalculated(self):
        """File all partial positions to be recalculated."""

        # The version with the try statement avoids changing
        # apswapi.Sqlite3Secondary.file_records_under()
        # to do an 'imsert or replace' rather than an 'insert' while the
        # consequences elsewhere are unknown.
        # The problem appears if at least one list of games matching a partial
        # position has been created.  The list does not need to be displayed.
        self.start_transaction()
        allrecords = self.make_recordset_all(
            PARTIAL_FILE_DEF, PARTIAL_FILE_DEF)
        self.file_records_under(
            PARTIAL_FILE_DEF,
            NEWGAMES_FIELD_DEF,
            allrecords,
            self.encode_record_selector(NEWGAMES_FIELD_VALUE),
            )
        allrecords.close()
        self.commit()
        #self.start_transaction()
        #allrecords = self.make_recordset_all(
        #    PARTIAL_FILE_DEF, PARTIAL_FILE_DEF)
        #try:
        #    self.file_records_under(
        #        PARTIAL_FILE_DEF,
        #        NEWGAMES_FIELD_DEF,
        #        allrecords,
        #        self.encode_record_selector(NEWGAMES_FIELD_VALUE),
        #        )
        #    self.commit()

        ## sqlite3 raises IntegrityError instead.
        #except ConstraintError:

        #    self.backout()
        #    dialogues.showwarning(
        #        title='Partial Position Update',
        #        message=''.join(('The partial position update related to a ',
        #                         'game update has failed.\n\nThis is known ',
        #                         'to happen if two or more partial positions ',
        #                         'have the same name when using an Sqlite3 ',
        #                         'database.\n\nPlease look at the list of ',
        #                         'partial positions and rename so each name ',
        #                         'is used once only.\n\n(The problem will be ',
        #                         'fixed in a future version of ',
        #                         APPLICATION_NAME,
        #                         '. The other supported databases do not ',
        #                         'suffer this problem.)',
        #                         )))
        #finally:
        #    allrecords.close()
