#
# Copyright (c) 2018
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
import zipfile
from shutil import copyfileobj
from coils.foundation import BLOBManager
from coils.core import \
    CoilsException, \
    get_yaml_struct_from_project7000, \
    walk_ogo_uri_to_target, \
    Folder
from coils.core.logic import ActionCommand


def retrieved_aliased_property_index(context):

    prop_map = get_yaml_struct_from_project7000(
        context, '/PropertyAliases.yaml',
    )
    if not prop_map:
        return dict()
    return prop_map


class ZIPToFolderAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "zip-to-folder"
    __aliases__ = ['zipToFolder', 'zipToFolderAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def _yield_input_handles_name_and_size(self):
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
            yield zhandle, zipinfo.filename, zipinfo.file_size
        zfile.close()
        return

    def do_action(self):

        if not (self.input_mimetype in ('application/zip', )):
            raise CoilsException(
                'Input message is not a ZIP archive, check message MIMEtype'
            )

        if not self._folder_uri:
            raise CoilsException('No folderURI provided to action')

        folder = walk_ogo_uri_to_target(
            context=self._ctx,
            uri=self._folder_uri,
        )
        if not isinstance(folder, Folder):
            raise CoilsException('Target for storage is not a Folder')
        else:
            self.log_message(
                'Target is folder "{0}" OGo#{1}'
                .format(folder.name, folder.object_id, )
            )

        documents = list()

        for handle, object_name, size in self._yield_input_handles_name_and_size():  # noqa

            document = self._ctx.run_command(
                'folder::ls', id=folder.object_id, name=object_name,
            )

            # move the archive object to a 'real' temporary file
            sfile = BLOBManager.ScratchFile(encoding='binary')
            copyfileobj(handle, sfile)
            sfile.flush()
            """ Be paranoid: check we got what we expected """
            offset = sfile.tell()
            if not (offset == size):
                raise CoilsException(
                    'Scratch file for "{0}" differs in size from '
                    'archive object; {1} in archive vs {2}'
                    .format(object_name, size, offset, )
                )
            handle.close()  # end safety copy

            if document:
                '''
                A document at this path already exists, so we are updating it
                This will create a new revision of the document, provided the
                storage backend supports document versioning
                '''
                document = document[0]
                self._ctx.run_command(
                    'document::set',
                    object=document,
                    values={},
                    handle=sfile,
                )
            else:
                document = self._ctx.run_command(
                    'document::new',
                    name=object_name,
                    values={},
                    folder=folder,
                    handle=sfile,
                )
            # Update the abstract of the document
            if self._abstract:
                document.abstract = self._abstract
            # TODO: set a MIME-type via property
            documents.append(document)
            sfile.close()

        """
        Process XATTRs onto the new document
        """
        if self._pa_values:
            alias_map = retrieved_aliased_property_index(self._ctx)
            if not alias_map:
                self.log.warn('No Property Alias Map found')
            for document in documents:
                for key, value in self._pa_values.items():
                    if key in alias_map:
                        self._ctx.property_manager.set_property(
                            entity=document,
                            namespace=alias_map[key]['namespace'],
                            attribute=alias_map[key]['attribute'],
                            value=value,
                        )
                        self.log_message(
                            'Stored value from property alias "{0}" to object '
                            'property {{{1}}}{2}'
                            .format(
                                key,
                                alias_map[key]['namespace'],
                                alias_map[key]['attribute'],
                            ),
                            category='debug'
                        )
                    else:
                        self.log_message(
                            'Property alias for key "{0}" does not resolve '
                            'provided value has been discarded'
                            .format(key, ),
                            category='info'
                        )

        """
        if the process has a process-task then link the document to the task.
        """
        if self.process.task_id:
            task = self._ctx.run_command(
                'task::get', id=self.process.task_id,
            )
            if task:
                for document in documents:
                    self._ctx.link_manager.link(
                        task, document, label=self._filename,
                    )

        """
        Additional meta-data
        """
        for document in documents:
            self._ctx.property_manager.set_property(
                entity=document,
                namespace='http://www.opengroupware.us/oie',
                attribute='sourceMessageLabel',
                value=self.input_message.label,
            )

            self._ctx.property_manager.set_property(
                entity=document,
                namespace='http://www.opengroupware.us/oie',
                attribute='sourceProcessid',
                value=self.process.object_id,
            )

            if self.process.route:
                self._ctx.property_manager.set_property(
                    entity=document,
                    namespace='http://www.opengroupware.us/oie',
                    attribute='sourceRouteId',
                    value=self.process.route.object_id,
                )
                self._ctx.property_manager.set_property(
                    entity=document,
                    namespace='http://www.opengroupware.us/oie',
                    attribute='sourceRouteName',
                    value=self.process.route.name,
                )

        """
        Log comment
        """
        for document in documents:
            self._ctx.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message=(
                    'Document created/updated from ZIP archive by '
                    'OGo#{0} [Process]'.format(self.process.object_id, )
                ),
                version=document.version,
            )

        # generate an output message

    def parse_action_parameters(self):
        """
        Action parameters: folderURI, abstract, pa_*
        """

        self._folder_uri = None
        folder_uri = self.action_parameters.get('folderURI', None)
        if folder_uri:
            folder_uri = folder_uri.strip()
            self._folder_uri = self.process_label_substitutions(folder_uri)
            self._folder_uri = self._folder_uri.strip('/')

        self._abstract = self.process_label_substitutions(
            self.action_parameters.get('abstract', None)
        )

        #
        # Take XATTR values out of action parameters
        #
        self._pa_values = dict()
        for key, value, in self.action_parameters.items():
            if not key.startswith('pa_'):
                continue
            self._pa_values[key[3:]] = self.process_label_substitutions(
                value
            )

    def do_epilogue(self):
        pass
