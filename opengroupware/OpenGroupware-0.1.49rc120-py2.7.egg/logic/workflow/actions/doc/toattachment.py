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
from coils.core import CoilsException
from coils.core.logic import ActionCommand

"""
See https://sourceforge.net/p/coils/tickets/279/
  "MessageToAttachmentAction expiration should support date-time string. "
"""


class MessageToAttachmentAction(ActionCommand):
    """
    Store the contents of a workflow message to an entity attachment
    """
    __domain__ = "action"
    __operation__ = "message-to-attachment"
    __aliases__ = ['messageToAttachment', 'messageToAttachmentAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def _calculate_expiration(self, expiration):
        if expiration:
            try:
                if expiration.startswith('+'):
                    expiration = (
                        long(expiration[1:]) + self._ctx.get_timestamp()
                    )
                    return long(expiration)
                else:
                    return long(expiration)
            except:
                raise CoilsException(
                    'Unable to calculate Attachment expiration '
                    'from value "{0}"'
                    .format(self._expiration, )
                )
        return None

    def do_action(self):

        self._expiration = self._calculate_expiration(self._expiration)

        related_entity = self._ctx.type_manager.get_entity(self._related_id)
        if not related_entity:
            raise CoilsException(
                'Unable to marshall entity OGo#{0}'
                .format(self._related_id, )
            )

        attachment = self._ctx.run_command(
            'attachment::new',
            entity=related_entity,
            mimetype=self.input_mimetype,
            kind=self._kind_string,
            expiration=self._expiration,
            name=self._uid_name,
            handle=self.rfile,
        )

        self.wfile.write(attachment.uuid)

    def parse_action_parameters(self):

        self._related_id = long(
            self.process_label_substitutions(
                self.action_parameters.get('relatedId', None)
            )
        )

        self._kind_string = self.process_label_substitutions(
            self.action_parameters.get('kind', None)
        )

        self._uid_name = self.process_label_substitutions(
            self.action_parameters.get('name', None)
        )

        self._expiration = self.process_label_substitutions(
            self.action_parameters.get('expiration', None)
        )

    def do_epilogue(self):
        pass
