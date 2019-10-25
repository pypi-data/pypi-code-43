#
# Copyright (c) 2010, 2013, 2014, 2015
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
from coils.core import \
    BLOBManager, ProcessLogEntry, \
    OGO_ROLE_SYSTEM_ADMIN, OGO_ROLE_WORKFLOW_ADMIN, \
    AccessForbiddenException
from coils.core.logic import DeleteCommand
from utility import \
    filename_for_versioned_process_code, \
    filename_for_process_code, \
    filename_for_process_markup


class DeleteProcess(DeleteCommand):
    __domain__ = "process"
    __operation__ = "delete"

    def check_run_permissions(self):
        if (
            self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN) or
            self._ctx.has_role(OGO_ROLE_WORKFLOW_ADMIN)
        ):
            return

        rights = self._ctx.access_manager.access_rights(self.obj, )
        if set('dw').intersection(rights):
            return

        raise AccessForbiddenException(
            'Insufficient privileges to delete process OGo#{0}'
            .format(self.obj.object_id, )
        )

    def get_by_id(self, pid, access_check):
        '''
            Get the process by id in order to support delete by id
            :param pid: process id
            :param access_check: should access processing be disabled?
            Probably not.
        '''
        return self._ctx.run_command(
            'process::get', id=pid, access_check=access_check,
        )

    def delete_process_log_entries(self):
        '''Delete the corresponding entries from the process_log table.'''

        self.log.debug(
            'Deleted {0} process log entries for OGo#{1}'
            .format(
                self._ctx.db_session().query(ProcessLogEntry)
                .filter(
                    ProcessLogEntry.process_id == self.obj.object_id,
                ).delete(),
                self.obj.object_id, )
            )

    def release_process_run_lock(self):
        '''Delete the process run lock (if any)'''
        prop = self._ctx.property_manager.get_property(
            self.obj, 'http://www.opengroupware.us/oie', 'lockToken',
        )
        if prop:
            token = prop.get_string_value()
            lock = self._ctx.lock_manager.get_lock(token)
            if lock:
                tmp = None
                if self.obj.object_id == lock.object_id:
                    tmp = self.obj
                else:
                    tmp = self._ctx.type_manager.get_entity(lock.object_id)
                if tmp:
                    if self._ctx.lock_manager.unlock(
                        entity=tmp,
                        token=lock.token,
                        context_id=lock.owner_id,
                    ):
                        self.log.info(
                            'Released run lock token related to '
                            'OGo#{0} [{1}] for OGo#{2} [Process]'
                            .format(
                                tmp.object_id,
                                tmp.__entityName__,
                                self.obj.object_id,
                            )
                        )

    def run(self):
        '''
            Delete the process entity.
            Currently it deletes the shelf, the messages, the versioned state,
            and the process_log entries.  Are we missing anything?
        '''
        self.log.debug(
            'Deleting data for processId#{0}'.format(self.obj.object_id, )
        )
        BLOBManager.DeleteShelf(uuid=self.obj.uuid)
        messages = self._ctx.run_command(
            'process::get-messages', process=self.obj,
        )
        for message in messages:
            self.log.debug('Deleting message {0}'.format(message.uuid, ))
            self._ctx.run_command('message::delete', uuid=message.uuid, )

        for vid in range(self.obj.version):
            BLOBManager.Delete(
                filename_for_versioned_process_code(self.obj.object_id, vid, )
            )

        for filename in [
            filename_for_process_markup(self.obj),
            filename_for_process_code(self.obj)
        ]:
            BLOBManager.Delete(filename)

        self.delete_process_log_entries()

        self.release_process_run_lock()

        DeleteCommand.run(self)
