#
# Copyright (c) 2015
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
from coils.core import NoSuchPathException
from coils.net import PathObject
from attachmentobject import AttachmentObject


class NamedAttachment(PathObject):
    """
    Return the AttachmentObject by name [webdav_uid] within the scope of
    the specified Entity.
    """

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        attachment = self.context.r_c(
            'attachment::get',
            object_id=self.entity.object_id,
            name=name,
        )
        if not attachment:
            raise NoSuchPathException(
                'Entity OGo#{0} [{1}] has not attachment named "{2}"'
                .format(
                    self.entity.object_id,
                    self.entity.__entityName__,
                    name,
                )
            )
        return AttachmentObject(
            self,
            name,
            entity=attachment,
            disposition=self.name,
            parameters=self.parameters,
            request=self.request,
            context=self.context,
        )

    def supports_DELETE(self):
        return True

    def do_DELETE(self, name):

        attachment = self.context.run_command(
            'attachment::get',
            object_id=self.entity.object_id,
            name=name,
        )
        if not attachment:
            raise NoSuchPathException(
                'Entity OGo#{0} [{1}] has not attachment named "{2}"'
                .format(
                    self.entity.object_id,
                    self.entity.__entityName__,
                    name,
                )
            )

        result = self.context.r_c(
            'attachment::delete',
            uuid=attachment.uuid,
        )

        self.context.commit()

        self.request.simple_response(204)
