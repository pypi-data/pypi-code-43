#!/usr/bin/env python
# Copyright (c) 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2019
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
import os
import shutil
import zipfile
import tarfile
from coils.core import BLOBManager, CoilsException
from coils.core.logic import ActionCommand


class QueueProcessAction(ActionCommand):
    '''
    Queue a new process from execution. The input of this action will be
    the input message of the new process.
    '''
    __domain__ = "action"
    __operation__ = "queue-process"
    __aliases__ = ['queueProcess', 'queueProcessAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def _copy_xattrs(self, from_, to_, ):
        '''
        Copy object properties that look like XATTRs from the specified
        entity [likely the current process] to the specified target [the
        new "child" process being created].
        '''
        for prop in self._ctx.pm.get_properties(entity=from_):
            if (
                prop.namespace == 'http://www.opengroupware.us/oie' and
                prop.name.startswith('xattr_')
            ):
                self._ctx.property_manager.set_property(
                    entity=to_,
                    namespace='http://www.opengroupware.us/oie',
                    attribute=prop.name,
                    value=prop.get_value(),
                )

    def _queue_process(self, route, rfile, filename):
        """
        Create a new process with the specified input an parameters.
        Place the new process in the queued state.
        Implments XATTR inheritance, origin labels, and setting XATTR's
        provided in action parameters
        """

        # TODO: Is this initial copy necessary?
        input_handle = BLOBManager.ScratchFile(suffix='.message')
        shutil.copyfileobj(rfile, input_handle)
        input_handle.seek(0)

        """
        Messages are not required to have labels, so it is likely that filename
        will be None - in which case we create an input label of "unnamed".
        filename can only be expected to be defined when the process has been
        queued from an archive [where each item in the archive will be named].
        """
        if filename is None:
            filename = 'unnamed'

        #
        # Create Process
        #

        process = self._ctx.run_command(
            'process::new',
            values={
                'route_id': route.object_id,
                'handle': input_handle,
            },
        )

        if process is None:
            """
            process::new can choose not to create a process due to
            run-control rules of the route.  In that case the Logic command
            returns a NULL.
            """
            self.log_message(
                message=(
                    'Creation of Process from OGo#{0} [Route: "{1}"] '
                    'supressed by run-control for message labelled "{2}".'
                    .format(
                        route.object_id,
                        route.name,
                        filename,
                    )
                ),
                category='info',
            )
            BLOBManager.Close(input_handle)
            return None

        # process created
        process.state = 'Q'  # Set state of process to queued
        # inherit attributes from parent process
        process.priority = self._priority
        process.task_id = self.process.task_id
        process.parent_id = self.process.object_id

        # XATTR Inheritance
        if self._inherit_xattrs:
            self._copy_xattrs(from_=self.process, to_=process, )

        # Set Origin Label
        self._ctx.property_manager.set_property(
            entity=process,
            namespace='http://www.opengroupware.us/oie',
            attribute='originLabel',
            value=filename.replace('\\', '_').replace('/', '_'),
        )

        # XATTR Values
        if self._xattr_values:
            for key, value in self._xattr_values.items():
                self._ctx.property_manager.set_property(
                    entity=process,
                    namespace='http://www.opengroupware.us/oie',
                    attribute=key,
                    value=value,
                )

        self.log_message(
            message=(
                'Created OGo#{0} [Process] of OGo#{1} [Route: "{2}"] '
                'for processing archive content named "{3}".'
                .format(
                    process.object_id,
                    route.object_id,
                    route.name,
                    filename,
                )
            ),
            category='debug',
        )

        BLOBManager.Close(input_handle)

        return process

    def _yield_input_handles_and_name(self):
        '''
        Yield tupes of handle & name from the input message
        '''

        # ZIP files must be this size or larger or else it will be
        # assumed to be empty.
        MIN_ZIPFILE_SIZE = 23

        def get_archive_size(rfile):
            rfile.seek(0, os.SEEK_END)  # go to end
            rfile_size = rfile.tell()  # get current offset
            rfile.seek(0, os.SEEK_SET)  # rewind
            return rfile_size

        rfile_size = get_archive_size(self.rfile)

        if self._unpack_archives:

            if self.input_mimetype in ('application/zip', ):

                """ZIP FILE"""

                if rfile_size < MIN_ZIPFILE_SIZE:
                    """
                    ZIP file is too small, it won't work, bail out.

                    HACK: The Python zipfile module is buggy in relation to
                    empty archives; this short-circuit hacks our way out of
                    that mess. Some of this is fixed in Python 2.7.1; use that
                    version or later if you can.
                    """
                    return

                # Process contents of ZipFile

                zfile = zipfile.ZipFile(self.rfile, 'r', )
                for zipinfo in zfile.infolist():
                    zhandle = zfile.open(zipinfo, 'r')
                    yield zhandle, zipinfo.filename
                zfile.close()
                return

            if self.input_mimetype in (
                'application/tar', 'application/x-tar', 'applicaton/x-gtar',
                'multipart/x-tar',
            ):
                tfile = tarfile.TarFile(
                    fileobj=self.rfile,
                )
                for tinfo in tfile:
                    if tinfo.isfile():
                        yield tfile.extractfile(tinfo), tinfo.name
                tfile.close()
                return

        """
        Default, return just the input message and its label
        NOTE: it is not mandatory that an action have an input_message, so
        we need to short-circuit around that condition.  However a message
        will always have [internally] an input and output streak [aka rfile
        and wfile - they might must be scratch files if there is no
        corresponding message].  As a messgae is not required to have a label
        this should not be a problem for conforming actions.
        """
        if self.input_message:
            yield self.rfile, self.input_message.label
        else:
            yield self.rfile, None
        return

    def do_action(self):
        '''
        Create the new process and place it in a queued state
        '''
        route = self._ctx.run_command(
            'route::get',
            name=self._route_name,
            locks_enabled=False,
            )
        if not route:
            raise CoilsException(
                'Unable to marshall route named "{0}"'.format(
                    self._route_name,
                )
            )

        processes_created = list()

        for handle, name, in self._yield_input_handles_and_name():
            processes_created.append(
                self._queue_process(route, handle, name, )
            )

        self.wfile.write(
            ','.join(
                [unicode(process.object_id) for process in processes_created]
            )
        )

    def parse_action_parameters(self):
        '''
        Process the action parameters: routeName, priority, & 'inheritXATTRs'
        '''
        self._route_name = self.action_parameters.get('routeName', None)
        if (self._route_name is None):
            raise CoilsException('No such route to queue process.')

        self._priority = int(
            self.action_parameters.get('priority', self.process.priority)
        )

        self._inherit_xattrs = True
        if self.action_parameters.get('inheritXATTRs', 'YES').upper() == 'NO':
            self._inherit_xattrs = False

        self._unpack_archives = (
            True if self.action_parameters.get(
                'unpackArchives', 'NO'
            ).upper() == 'YES' else False
        )

        #
        # Take XATTR values out of action parameters
        #

        self._xattr_values = {}
        for key, value, in self.action_parameters.items():
            if not key.startswith('xattr_'):
                continue
            self._xattr_values[key] = self.process_label_substitutions(
                value
            )
