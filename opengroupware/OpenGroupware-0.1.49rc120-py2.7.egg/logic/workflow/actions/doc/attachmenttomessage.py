#
# Copyright (c) 2015
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
import shutil
from coils.core import \
    CoilsException, \
    BLOBManager
from coils.core.logic import ActionCommand


class AttachmentToMessageAction(ActionCommand):
    """
    Copy the contents of an attachment to a message, retaining the MIME type.
    """
    __domain__ = "action"
    __operation__ = "attachment-to-message"
    __aliases__ = ['attachmentToMessage', 'attachmentToMessageAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._mimetype

    def do_action(self):

        if not self._attachment_uuid:
            # Attachment by name
            entity = self._ctx.type_manager.get_entity(self._related_id)
            if not entity:
                raise CoilsException(
                    'Unable to marshall related entity OGo#{0}'
                    .format(self._related_id, )
                )
            attachment = self._ctx.run_command(
                'attachment::get',
                object_id=entity.object_id,
                name=self._attachment_name,
            )
            if not attachment:
                raise CoilsException(
                    'OGo#{0} has not attachment named "{1}"'
                    .format(entity.object_id, self._attachment_name, )
                )
        else:
            # Attachment by UUID
            attachment = self._ctx.run_command(
                'attachment::get',
                uuid=self._attachment_uuid,
            )
            if not attachment:
                raise CoilsException(
                    'Unable to marshall attachment UUID "{0}"'
                    .format(self._attachment_uuid, )
                )

        handle = self._ctx.run_command(
            'attachment::get-handle',
            attachment=attachment,
        )

        if not handle:
            raise CoilsException(
                'Unable to open contents of attachment "{0}" '
                '[name: "{1}" related-to OGo#{2}]'
                .format(
                    attachment.uuid,
                    attachment.webdav_uid,
                    attachment.related_id,
                )
            )

        # Copy attachment content and MIME type to message
        shutil.copyfileobj(handle, self.wfile)
        self._mimetype = attachment.mimetype

        # Close Document
        BLOBManager.Close(handle)

        # Dereference attachment entity
        attachment = None

    def parse_action_parameters(self):

        # default is to retrieve the attachment by UUID
        self._attachment_uuid = self.process_label_substitutions(
            self.action_parameters.get('attachmentUUID', None, )
        )
        if not self._attachment_uuid:
            # As attachment UUID was not specified lets try to find by name
            self._related_id = long(
                self.process_label_substitutions(
                    self.action_parameters.get('relatedId', None, )
                )
            )
            self._attachment_name = self.process_label_substitutions(
                self.action_parameters.get('name', None, )
            )
