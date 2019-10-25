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
# THE SOFTWARE
#
from coils.core import \
    Attachment, \
    BLOBManager, \
    Command, \
    AccessForbiddenException, \
    OGO_ROLE_SYSTEM_ADMIN
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


class ExpireAttachments(Command, AttachmentCommand):
    """
    Delete attachments which have expired.

    This command may only be performed by a context holding the System
    Administrator roll, otherwise and AccessForbiddenException will be
    raised.  The "overkeep" parameter may specify a number of seconds -
    this value allows attachments a grace-period where they will be retained
    by the system [although invisible to attachment::get] for the specified
    number of seconds after their expiration.  Expiration is a UTC timestamp.
    Return value is the number of attachments expired.
    """
    __domain__ = "attachment"
    __operation__ = "expire"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.overkeep = int(params.get('overkeep', 0))

    def check_run_permissions(self):
        if self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN):
            return
        raise AccessForbiddenException(
            'Context lacks administrative role; cannot expire attachments.'
        )

    def run(self):

        expires_time = self._ctx.get_timestamp() - self.overkeep

        query = (
            self._ctx.db_session().
            query(Attachment).
            filter(Attachment.expiration < expires_time)
        )

        attachments = query.all()

        counter = 0

        for attachment in attachments:
            BLOBManager.Delete(self.attachment_text_path(attachment))
            self._ctx.db_session().delete(attachment)
            counter += 1

        self.log.info(
            '{0} attachments deleted due to expiration'.format(counter, )
        )

        self.set_result(counter)
