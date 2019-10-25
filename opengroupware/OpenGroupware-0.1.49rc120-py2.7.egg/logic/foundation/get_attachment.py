#
# Copyright (c) 2011, 2015
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
from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import desc
from coils.core import Attachment, Command, CoilsException
from coils.core.logic import GetCommand
from command import AttachmentCommand

"""
  Entity class Attachment
    uuid, string, primary key
    related_id, integer/objectId, entity to which attachment is realted
    kind, string
    mimetype, string, required
    created, datetime
    size, integer, size in octets
    expiration, integer, UTC timestamp
    context_id, integer/objectId, creator's context id
    webdav_uid, string, display name sorta kinda
    checksum, string, SHA512 storage checksum
    extra_data, PickleData, whatever
"""


class GetAttachment(GetCommand, AttachmentCommand):
    __domain__ = "attachment"
    __operation__ = "get"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self._name = None
        self._object_id = None
        self._uuid = params.get('uuid', None)

        if self._uuid is None:
            self._name = params.get('name', None)
            self._object_id = params.get('object_id', None)
            if not self._object_id:
                obj = params.get('object', None)
                if obj and hasattr(obj, 'object_id'):
                    self._object_id = obj.object_id

        if not (
            (self._uuid is not None) or
            (self._name is not None and self._object_id is not None)
        ):
            raise CoilsException(
                'attachment::get parameters do not identify an attachment.'
            )

    def run(self):

        self.set_single_result_mode()

        db = self._ctx.db_session()

        if self._uuid:
            query = db.query(Attachment).filter(
                and_(
                    Attachment.uuid == self._uuid,
                    or_(
                        Attachment.expiration > self._ctx.get_timestamp(),
                        Attachment.expiration == None
                    )
                )
            )
        else:
            query = db.query(Attachment).filter(
                and_(
                    Attachment.related_id == self._object_id,
                    Attachment.webdav_uid == self._name,
                    or_(
                        Attachment.expiration > self._ctx.get_timestamp(),
                        Attachment.expiration == None
                    )
                )
            ).order_by(desc(Attachment.created))

        self.set_return_value(query.all())
