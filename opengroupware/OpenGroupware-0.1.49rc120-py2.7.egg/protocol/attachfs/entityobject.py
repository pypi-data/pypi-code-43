#
# Copyright (c) 2011, 2013, 2014, 2015, 2016
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
# THE SOFTWARE.
#
from coils.core import \
    Document, CoilsException, BLOBManager, \
    CoilsUnreachableCode, \
    NoSuchPathException
from coils.net import PathObject
from namedattachment import NamedAttachment


OGO_COILS_NAMESPACE = '57c7fc84-3cea-417d-af54-b659eb87a046'


class EntityObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        self.request = None
        self.parameters = None
        PathObject.__init__(self, parent, **params)

    def _put_photo_mode(self, name, scratch_file, mimetype):
        """
        handle and upload in photo mode

        :param name: The name of the file upload
        :param scratch_file: The stream file containing the contents
            of the upload
        :param mimetype: The content-type specified by the client
        """

        # TODO: should be check the filesize here?

        self.context.run_command(
            'contact::set-photo',
            handle=scratch_file,
            mimetype=mimetype,
            contact=self.entity,
        )

        # Respond to client
        self.context.commit()
        self.request.simple_response(
            201,
            mimetype=mimetype,
            headers={
                'X-OpenGroupware-Contact-Id': str(self.entity.object_id),
                'Content-Type': mimetype,
            },
        )

    def _put_file_mode(self, name, scratch_file, mimetype):
        '''
        Handle an upload in file (document) mode.

        :param name: The name of the file upload
        :param scratch_file: The stream file containing the contents
            of the upload
        :param mimetype: The content-type specified by the client
        '''

        document = self.context.run_command(
            'document::inbox',
            target=self.entity,
            filename=name,
            mimetype=mimetype,
            stream=scratch_file,
            extras=self.parameters,
        )

        self.context.commit()

        self.request.simple_response(
            201,
            mimetype=mimetype,
            headers={
                'X-OpenGroupware-Document-Id': str(document.object_id),
                'X-OpenGroupware-Folder-Id': str(document.folder_id),
                'Etag': '{0}:{1}'.format(
                    document.object_id,
                    document.version,
                ),
                'Content-Type': document.mimetype,
            },
        )

    def do_HEAD(self):
        mimetype = self.context.type_manager.get_mimetype(self.entity)
        headers = {
            'X-OpenGroupware-ObjectId': str(self.entity.object_id),
            'X-OpenGroupware-Version': str(self.entity.version),
            'Content-Type': mimetype,
        }

        if isinstance(self.entity, Document):
            """Add additional headers to document entity HEAD response"""
            headers.update({
                'X-OpenGroupware-Document-Id': str(self.entity.object_id),
                'X-OpenGroupware-Folder-Id': str(self.entity.folder_id),
                'X-OpenGroupware-Revision': str(self.entity.version_count),
                'X-OpenGroupware-Version': str(self.entity.version),
                'X-OpenGroupware-Checksum': str(self.entity.checksum),
                'X-OpenGroupware-Project-Id': str(self.entity.project_id),
                'X-OpenGroupware-Folder-Path': '/'.join(
                    self.entity.folder_name_path
                ),
            })
        self.request.simple_response(
            200,
            mimetype=mimetype,
            headers=headers,
        )

    def do_PUT(self, name):
        payload = self.request.get_request_payload()
        mimetype = self.request.headers.get(
            'Content-Type', 'application/octet-stream',
        )
        self.log.debug(
            'Attachment upload MIME type is "{0}"'.format(mimetype, ))
        scratch_file = BLOBManager.ScratchFile()
        scratch_file.write(payload)
        self.log.debug('Wrote {0}b to upload buffer'.
                       format(scratch_file.tell(), ))
        scratch_file.seek(0)
        attachment = None

        # Detect the mode for the operation; we fall through to the
        # default but allow an alternate to be specified via the URL
        # parameter "mode".  Currently mode "file" is supported to
        # easily allow the content of documents [files in projects] to
        # be updated and for documents [files in projects] to be
        # created.
        mode = None
        if 'mode' in self.parameters:
            mode = self.parameters['mode'][0].lower()
        else:
            mode = 'default'

        if mode == 'file':

            self.log.debug('AttachFS upload mode is file/document')
            self._put_file_mode(name, scratch_file, mimetype)
            return

        elif mode == 'photo':

            self.log.debug('AttachFS upload mode is photo')
            self._put_photo_mode(name, scratch_file, mimetype)
            return

        elif mode == 'default':
            #
            # Default AttachFS behavior
            #
            attachment = self.context.run_command(
                'attachment::new',
                handle=scratch_file,
                name=name,
                entity=self.entity,
                mimetype=mimetype,
            )
            self.context.commit()

            if attachment:
                self.request.simple_response(
                    201,
                    mimetype=mimetype,
                    headers={
                        'Etag': attachment.uuid,
                        'Content-Type': attachment.mimetype,
                    },
                )
                return

            else:
                # TODO; Can this happen without an exception having occurred?
                raise CoilsUnreachableCode(
                    'Attachment after attachment::new is NULL'
                )

        raise CoilsException(
            'Unrecognized mode "{0}" specified for AttachFS operation.'.
            format(mode, )
        )

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name in ('download', 'view', ):
            return NamedAttachment(
                self,
                name,
                entity=self.entity,
                request=self.request,
                parameters=self.parameters,
                context=self.context,
            )
        raise NoSuchPathException(
            'Specify "download" or "view" as subordinates to '
            'AttachFS EntityObject.\n To retrieve an attachment '
            'for an entity the correct path is: '
            '/attachfs/{entityObjectId}/download|view/{attachmentName}.\n'
            'To retrieve an attachment by UUID/GUID simply request: '
            '/attachfs/download|view/{UUID/GUID}\n'
        )
