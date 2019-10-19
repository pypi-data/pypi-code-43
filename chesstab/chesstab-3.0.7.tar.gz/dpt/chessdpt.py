# chessdpt.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess database using DPT.

This module on Windows and Wine only.

"""

import os.path
import bz2
import shutil

from dptdb.dptapi import (
    FILEDISP_OLD,
    FIFLAGS_FULL_TABLEB,
    FIFLAGS_FULL_TABLED,
    FISTAT_DEFERRED_UPDATES,
    APIContextSpecification,
    APIFieldValue,
    )

from solentware_base.dptapi import DPTapi, DPTapiError
from solentware_base.api.constants import (
    FILEDESC,
    BRECPPG,
    BSIZE,
    DSIZE,
    DPT_DEFER_FOLDER,
    DPT_SYS_FOLDER,
    SECONDARY,
    )
from solentware_misc.workarounds import dialogues

from ..core.filespec import (
    FileSpec,
    PARTIAL_FILE_DEF,
    PARTIAL_FIELD_DEF,
    NEWGAMES_FIELD_DEF,
    NEWGAMES_FIELD_VALUE,
    )
from .. import APPLICATION_NAME, ERROR_LOG


class ChessDatabase(DPTapi):

    """Provide access to a database of games of chess.
    """

    def __init__(self, databasefolder, **kargs):
        """Define chess database.

        **kargs
        allowcreate == False - remove file descriptions from FileSpec so
        that superclass cannot create them.
        Other arguments are passed through to superclass __init__.
        
        """
        try:
            sysprint = kargs.pop('sysprint')
        except KeyError:
            sysprint = 'CONSOLE'
        ddnames = FileSpec(**kargs)

        if not kargs.get('allowcreate', False):
            try:
                for dd in ddnames:
                    if FILEDESC in ddnames[dd]:
                        del ddnames[dd][FILEDESC]
            except:
                if __name__ == '__main__':
                    raise
                else:
                    raise DPTapiError('DPT description invalid')

        try:
            super(ChessDatabase, self).__init__(
                ddnames,
                databasefolder,
                sysprint=sysprint,
                **kargs)
        except DPTapiError:
            if __name__ == '__main__':
                raise
            else:
                raise DPTapiError('DPT description invalid')

        self._broken_sizes = dict()

    def use_deferred_update_process(
        self,
        dptmultistepdu=False,
        dptchunksize=None,
        **kargs):
        """Return module name or None

        dptmultistepdu is ignored if dptchunksize is not None.
        dptmultistepdu is True: use multi-step deferred update
        otherwise use single-step deferred update.

        dptchunksize is None: dptmultistepdu determines deferred update module
        otherwise use single-step deferred update with the chunk size (assumed
        to be a valid chunk size)

        **kargs - soak up any arguments other database engines need.
        
        On non-Microsoft operating systems single-step update may not work.
        First encountered on upgrade to FreeBSD7.2 wine-1.1.23,1 dptv2r19.
        But single-step works on FreeBSD7.2 wine-1.1.0,1 dptv2r19.
        Wine source code comments state that memory-use calls do not return
        correct values. Evidently the incorrectness can vary by version
        making the DPT workarounds liable to fail also.

        runchessdptdu.py does DPT's single-step deferred update process.
        runchessdptduchunk.py does DPT's single-step deferred update process
        but splits the task into fixed size chunks, a number of games, which
        it is hoped are small enough to finish before all memory is used.
        runchessdptdumulti.py does DPT's multi-step deferred update process.

        Multi-step is about half an order of magnitude slower than single-step.

        """
        if dptchunksize is not None:
            return os.path.join(
                os.path.basename(os.path.dirname(__file__)),
                'runchessdptduchunk.py')
        if dptmultistepdu is True:
            return os.path.join(
                os.path.basename(os.path.dirname(__file__)),
                'runchessdptdumulti.py')
        else:
            return os.path.join(
                os.path.basename(os.path.dirname(__file__)),
                'runchessdptdu.py')

    def adjust_database_for_retry_import(self, files):
        """Increase file sizes taking file full into account"""
        # Increase the size of files allowing for the file full condition
        # which occurred while doing a deferred update for import.
        for dbn in self._broken_sizes.keys():
            self.database_definition[dbn].increase_size_of_full_file(
                self.dbservices,
                self.database_definition[dbn].get_file_parameters(
                    self.dbservices),
                self._broken_sizes[dbn])
        return

    def open_context(self):
        """Open all files if they are in Normal mode (FISTAT == 0)."""
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
        fistat = dict()
        for dbo in self.database_definition.values():
            fistat[dbo] = dbo.get_file_parameters(self.dbservices)['FISTAT']
        for dbo in self.database_definition.values():
            if fistat[dbo][0] != 0:
                break
        else:
            self.increase_database_size(files=None)
            return oc
        # At least one file is not in Normal state
        r = '\n'.join(
            ['\t'.join(
                (os.path.basename(dbo._file),
                 fistat[dbo][1]))
             for dbo in self.database_definition.values()])
        dialogues.showinfo(
            title='Open',
            message=''.join(
                (APPLICATION_NAME,
                 ' has opened the database but some of the files are ',
                 'not in the Normal state.\n\n',
                 r,
                 '\n\n',
                 APPLICATION_NAME,
                 ' will close the database on dismissing this ',
                 'dialogue.\n\nRestore the database from backups, or source ',
                 'data, before trying again.',
                 )),
            )
        return self.close_database()

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
        names = set()
        basenames = set()
        names.add(self.get_dptsysfolder())
        basenames.add(os.path.basename(self.get_dptsysfolder()))
        for fn in (ERROR_LOG,):
            defer = os.path.join(self.get_database_folder(), fn)
            if os.path.exists(defer):
                names.add(defer)
                basenames.add(os.path.basename(defer))
        for k, v in self.database_definition.items():
            names.add(v._file)
            basenames.add(os.path.basename(v._file))
        listnames = [n for n in os.listdir(self.get_database_folder())
                     if n not in basenames]
        if len(listnames):
            dialogues.showinfo(
                title='Delete',
                message=''.join(
                    ('There is at least one file or folder in\n\n',
                     self.get_database_folder(),
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
            os.rmdir(self.get_database_folder())
        except:
            pass
        return True

    def get_archive_names(self, files=()):
        """Return names and operating system files for archives and guards"""
        specs = {f for f in files if f in self.database_definition}
        names = [v._file for k, v in self.database_definition.items()
                 if k in specs]
        archives = dict()
        guards = dict()
        for n in names:
            archiveguard = '.'.join((n, 'grd'))
            archivefile = '.'.join((n, 'bz2'))
            for d, f in ((archives, archivefile), (guards, archiveguard)):
                if os.path.exists(f):
                    d[n] = f
        return (names, archives, guards)

    def open_after_import_without_backups(self, files=()):
        """Return open context after doing database engine specific actions.

        For DPT clear the file sizes before import area if the database was
        opened successfully as there is no need to retry the import.

        """
        oc = super(ChessDatabase, self).open_context()
        if not oc:
            action = dialogues.askyesno(
                title='Open',
                message=''.join(
                    (APPLICATION_NAME,
                     ' is unable to open the database and backups were ',
                     'not taken, so cannot restore the database.\n\nDo you ',
                     'want to save a copy of the broken database?',
                     )),
                )
            if action:
                return False
            return 'Files not opened'
        fistat = dict()
        file_sizes_for_import = dict()
        for dbn, dbo in self.database_definition.items():
            gfp = dbo.get_file_parameters(self.dbservices)
            fistat[dbo] = gfp['FISTAT']
            if dbn in files:
                file_sizes_for_import[dbn] = gfp
        for dbo in self.database_definition.values():
            if fistat[dbo][0] != 0:
                break
        else:
            # Assume all is well as file status is 0
            # Or just do nothing (as file_sizes_for_import may be removed)
            self.increase_database_size(files=None)
            self.mark_partial_positions_to_be_recalculated()
            return True
        # At least one file is not in Normal state after Import.
        # Check the files that had imports applied
        for dbn in file_sizes_for_import:
            status = file_sizes_for_import[dbn]['FISTAT'][0]
            flags = file_sizes_for_import[dbn]['FIFLAGS']
            if not ((flags & FIFLAGS_FULL_TABLEB) or
                    (flags & FIFLAGS_FULL_TABLED)):
                break
        else:
            # The file states are consistent with the possibility that the
            # import failed because at least one file was too small.
            # The file size information is kept for calculating an increase
            # in file size before trying the import again.
            dialogues.showinfo(
                title='Open',
                message=''.join(
                    ('The import failed.\n\n',
                     APPLICATION_NAME,
                     ' has opened the database but some of the files are full ',
                     'and backups were not taken, so cannot offer ',
                     'the option of retrying the import with a larger file, ',
                     'and cannot restore the database.  The database may not ',
                     'be usable.',
                     )),
                )
            self.close_database()
            return None
        # At least one file is not in Normal state.
        # None of these files had deferred updates for Import or the state does
        # not imply a file full condition where deferred updates occured.
        r = '\n'.join(
            ['\t'.join(
                (os.path.basename(dbo._file),
                 fistat[dbo][1]))
             for dbo in self.database_definition.values()])
        action = dialogues.askyesno(
            title='Open',
            message=''.join(
                (APPLICATION_NAME,
                 ' has opened the database but some of the files are ',
                 'not in the Normal state.\n\n',
                 r,
                 '\n\nAt least one of these files is neither just ',
                 'marked Deferred Update nor marked Full, and backups were ',
                 'not taken, so ', APPLICATION_NAME,
                 ' is not offering the option of ',
                 'retrying the import with a larger file.\n\nDo you want to ',
                 'save a copy of the broken database?',
                 )),
            )
        self.close_database()
        if not action:
            return 'Import failed'
        return False

    def open_after_import_with_backups(self, files=()):
        """Return open context after doing database engine specific actions.

        For DPT clear the file sizes before import area if the database was
        opened successfully as there is no need to retry the import.

        """
        oc = super(ChessDatabase, self).open_context()
        if not oc:
            action = dialogues.askyesno(
                title='Open',
                message=''.join(
                    (APPLICATION_NAME,
                     ' is unable to open the database so cannot offer the ',
                     'option of retrying the import with larger files.',
                     '\n\nDo you want to save a copy of the broken database ',
                     'before restoring the database from the backups taken?',
                     )),
                )
            if action:
                return False
            return 'Files not opened'
        # open_context() call after completion of Import sequence
        fistat = dict()
        file_sizes_for_import = dict()
        for dbn, dbo in self.database_definition.items():
            gfp = dbo.get_file_parameters(self.dbservices)
            fistat[dbo] = gfp['FISTAT']
            if dbn in files:
                file_sizes_for_import[dbn] = gfp
        for dbo in self.database_definition.values():
            if fistat[dbo][0] != 0:
                break
        else:
            self.increase_database_size(files=None)
            self.mark_partial_positions_to_be_recalculated()
            return oc
        # At least one file is not in Normal state after Import.
        # Check the files that had imports applied
        for dbn in file_sizes_for_import:
            status = file_sizes_for_import[dbn]['FISTAT'][0]
            flags = file_sizes_for_import[dbn]['FIFLAGS']
            if not ((status == 0) or
                    (status == FISTAT_DEFERRED_UPDATES) or
                    (flags & FIFLAGS_FULL_TABLEB) or
                    (flags & FIFLAGS_FULL_TABLED)):
                break
        else:
            # The file states are consistent with the possibility that the
            # import failed because at least one file was too small.
            # The file size information is kept for calculating an increase
            # in file size before trying the import again.
            if dialogues.askyesno(
                title='Retry Import',
                message=''.join(
                    ('The import failed because the games file was filled.\n\n',
                     'The file will be restored from backups.\n\nDo ',
                     'you want to retry the import with more space (20%) ',
                     'allocated to the games file?'
                     ))
                ):
                return None
            else:
                self.close_database()
                return 'Restore without retry'
        # At least one file is not in Normal state.
        # None of these files had deferred updates for Import or the state does
        # not imply a file full condition where deferred updates occured.
        r = '\n'.join(
            ['\t'.join(
                (os.path.basename(dbo._file),
                 fistat[dbo][1]))
             for dbo in self.database_definition.values()])
        action = dialogues.askyesno(
            title='Open',
            message=''.join(
                (APPLICATION_NAME,
                 ' has opened the database but some of the files are ',
                 'not in the Normal state.\n\n',
                 r,
                 '\n\nAt least one of these files is neither just ',
                 'marked Deferred Update nor marked Full so ',
                 APPLICATION_NAME, ' is not offering the option of retrying ',
                 'the import with a larger file.\n\nDo you want to save a ',
                 'copy of the broken database before restoring from backups?',
                 )),
            )
        self.close_database()
        if not action:
            return 'Import failed'
        return False

    def save_broken_database_details(self, files=()):
        """Save database engine specific detail of broken files to be restored.

        It is assumed that the Database Services object exists.

        """
        self._broken_sizes.clear()
        bs = self._broken_sizes
        for f in files:
            bs[f] = self.database_definition[f].get_file_parameters(
                self.dbservices)

    def mark_partial_positions_to_be_recalculated(self):
        """File all partial positions to be recalculated"""
        root = self.database_definition[PARTIAL_FILE_DEF]
        allrecords = root.foundset_all_records(PARTIAL_FIELD_DEF)
        root.get_database().FileRecordsUnder(
            allrecords,
            self._dbspec[PARTIAL_FILE_DEF][SECONDARY][NEWGAMES_FIELD_DEF],
            APIFieldValue(self.encode_record_selector(NEWGAMES_FIELD_VALUE)))
        root.get_database().DestroyRecordSet(allrecords)
        self.commit()
