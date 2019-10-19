# chessdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess database using Berkeley DB.

The Berkeley DB interface has significantly worse performance than DPT when
doing multi-index searches.  However it is retained since DPT became available
because tracking down problems in the chess logic using IDLE can be easier
in the *nix environment.
"""

import os
import zipfile

# bsddb removed from Python 3.n
try:
    from bsddb3.db import (
        DB_BTREE,
        DB_HASH,
        DB_RECNO,
        DB_DUPSORT,
        DB_DUP,
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
        DB_BTREE,
        DB_HASH,
        DB_RECNO,
        DB_DUPSORT,
        DB_DUP,
        DB_CREATE,
        DB_RECOVER,
        DB_INIT_MPOOL,
        DB_INIT_LOCK,
        DB_INIT_LOG,
        DB_INIT_TXN,
        DB_PRIVATE,
        )

from solentware_base.dbapi import DBapi
from solentware_misc.workarounds import dialogues

from ..core.filespec import (
    FileSpec,
    GAMES_FILE_DEF,
    DB_ENVIRONMENT_GIGABYTES,
    DB_ENVIRONMENT_BYTES,
    NEWGAMES_FIELD_DEF,
    NEWGAMES_FIELD_VALUE,
    PARTIAL_FILE_DEF,
    )
from .. import APPLICATION_NAME, ERROR_LOG


class ChessDatabase(DBapi):

    """Provide access to a database of games of chess.
    """

    def __init__(self, DBfile, **kargs):
        """Define chess database.

        **kargs
        Arguments are passed through to superclass __init__.
        
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

        super(ChessDatabase, self).__init__(
            dbnames,
            DBfile,
            environment)

    def restore_dialogue(self, names=()):
        """Restore files containing games from a zip backup.

        Intended to be a backup in case import fails.

        """
        exists = [os.path.basename(n)
                  for n in names if os.path.exists('.'.join((n, 'zip')))]
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
            c = zipfile.ZipFile(
                '.'.join((n, 'broken', 'zip')),
                mode='w',
                compression=zipfile.ZIP_DEFLATED,
                allowZip64=True)
            for s in names[n]:
                an = os.path.join(s.get_database_file())
                fn = os.path.join(
                    self.get_database_folder(), s.get_database_file())
                c.write(fn, arcname=an)
            c.close()

    def delete_backups(self, names=()):
        """Delete backup files."""
        for n in names:
            try:
                os.remove('.'.join((n, 'grd')))
            except:
                pass
            try:
                os.remove('.'.join((n, 'zip')))
            except:
                pass

    def restore_backups(self, names=()):
        """Restore database from backup files."""
        not_restored = []
        for n in names:
            c = zipfile.ZipFile(
                '.'.join((n, 'zip')),
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
                not_restored.append(os.path.basename('.'.join((n, 'zip'))))
                c.close()
                continue
            c.extractall(path=self.get_database_folder(), members=extract)
            c.close()
        if not_restored:
            dialogues.showinfo(
                title='Restore files from backup',
                message=''.join(
                    ('The backup files\n\n',
                     '\n'.join(not_restored),
                     '\n\ndo not contain all and only the expected files.\n\n',
                     'The files will be left as they are.\n\nClick "OK" ',
                     'when ready to proceed.',
                     )),
                )
            return False
        return True

    def delete_database(self):
        """Close and delete the open chess database."""
        df = self.get_database_folder()
        files = [os.path.join(df, f) for f in self.get_database_filenames()]
        folders = [df]
        files.append(os.path.join(df, ERROR_LOG))
        for extn in ('grd', 'zip'):
            files.append(
                os.path.join(
                    df,
                    '.'.join(
                        (self.get_database_instance(
                            GAMES_FILE_DEF,
                            GAMES_FILE_DEF).get_database_file(),
                         extn))))
        self.close_database()
        for f in files:
            if os.path.isfile(f):
                try:
                    os.remove(f)
                except:
                    pass
        done = True
        for f in folders:
            if os.path.isdir(f):
                try:
                    os.rmdir(f)
                except:
                    done = False
        if not done:
            dialogues.showinfo(
                title='Delete',
                message=''.join(
                    ('There is at least one file or folder in\n\n',
                     df,
                     '\n\nwhich may not be part of the database.  These items ',
                     'have not been deleted by ', APPLICATION_NAME, '.',
                     ))
                )
        return True

    def use_deferred_update_process(self, **kargs):
        """Return module name False or None

        **kargs - soak up any arguments other database engines need.
        
        runchessdbdu.py runs the deferred update code in a separate process.

        """
        return os.path.join(
            os.path.basename(os.path.dirname(__file__)),
            'runchessdbdu.py')

    def get_archive_names(self, files=()):
        """Return names and operating system files for archives and guards"""
        table_indicies = self.get_table_indicies()
        specs = {f for f in files
                 if self.get_table_index(f, f) in table_indicies}
        names = dict()
        archives = dict()
        guards = dict()
        for s in specs:
            v = self.get_database_instance(s, s)
            ns = names[os.path.join(
                self.get_database_folder(), v.get_database_file())] = []
            for v in self.get_associated_indicies(s):
                ns.append(self.get_database_instance(s, v))
        for n in names:
            archiveguard = '.'.join((n, 'grd'))
            archivefile = '.'.join((n, 'zip'))
            for d, f in ((archives, archivefile), (guards, archiveguard)):
                if os.path.exists(f):
                    d[n] = f
        return (names, archives, guards)

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

    def open_after_import_without_backups(self, **ka):
        """Return True after doing database engine specific open actions.

        For Berkeley DB just call open_context.

        """
        oc = super(ChessDatabase, self).open_context()
        if not oc:
            return 'Files not opened'
        return True

    def open_after_import_with_backups(self, files=()):
        """Return True after doing database engine specific open actions.

        For Berkeley DB just call open_context.

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
