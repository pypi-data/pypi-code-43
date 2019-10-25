#
# Copyright (c) 2016
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


class MessageToINBOXAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "message-to-inbox"
    __aliases__ = ['messageToINBOX', 'messageToINBOXAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def do_action(self):

        target = self._ctx.type_manager.get_entity(self._object_id)
        if not target:
            raise CoilsException(
                'Unable to marshall specified entity: OGo#{0}'
                .format(self._object_id, )
            )

        document = self._ctx.run_command(
            'document::inbox',
            target=target,
            filename=self._filename,
            mimetype=self.input_message.mimetype,
            stream=self.rfile,
            extras=self._extras,
        )

        self.log_message(
            'Message INBOXed to document OGo#{0} in '
            'OGo#{1} [Folder] / OGo#{2} [Project]'
            .format(
                document.object_id,
                document.folder_id,
                document.project_id,
            ),
            category='info',
        )
        self.wfile.write(unicode(document.object_id))

    def parse_action_parameters(self):

        self._object_id = self.process_label_substitutions(
            self.action_parameters.get(
                'objectId', str(self.process.object_id),
            )
        )
        try:
            self._object_id = int(self._object_id)
        except:
            raise CoilsException(
                'objectId is not an integer: "{0}"'.format(self._object_id, )
            )

        self._filename = self.process_label_substitutions(
            self.action_parameters.get(
                'filename',
                self.input_message.label,
            )
        )

        # Extras - INBOX hinting and additional properties

        self._extras = dict()
        inbox_kind = self.process_label_substitutions(
            self.action_parameters.get(
                'inboxKind',
                None,
            )
        )
        if inbox_kind:
            self._extras['projectKind'] = inbox_kind

        abstract = self.process_label_substitutions(
            self.action_parameters.get('abstract', None)
        )
        if abstract:
            self._extras.set('abstract', abstract)

        # Take XATTR values out of action parameters
        for key, value, in self.action_parameters.items():
            if not key.startswith('pa_'):
                continue
            self._extras['pa.{0}'.format(key[3:], )] = \
                self.process_label_substitutions(value)
