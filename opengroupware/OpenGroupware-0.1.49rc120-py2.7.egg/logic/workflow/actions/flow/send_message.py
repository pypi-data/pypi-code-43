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
from coils.core import CoilsException
from coils.core.logic import ActionCommand


class SendMessageAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "send-message"
    __aliases__ = ['sendMessage', 'sendMessageAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):

        target_process = self._ctx.run_command(
            'process::get', id=self.target_process_id,
        )
        if not target_process:
            raise CoilsException(
                'Unable to marshall process OGo#{0}'
                .format(self.target_process_id, )
            )

        message = self._ctx.run_command(
            'message::new',
            process=target_process,
            label=self.target_message_label,
            mimetype=self.input_mimetype,
            signal=True,
            handle=self.rfile,
        )

        self.wfile.write(message.uuid)

        self.log_message(
            'Message UUID#{0} with label "{1}" sent to process OGo#{2}'
            .format(message.uuid, message.label, target_process.object_id, ),
            category='control',
        )

    def parse_action_parameters(self):

        self.target_process_id = self.process_label_substitutions(
            self.action_parameters.get('processId', None)
        )
        if not self.target_process_id:
            raise CoilsException(
                'No "processId" specified, this parameter is required.'
            )
        else:
            try:
                self.target_process_id = long(self.target_process_id)
            except:
                raise CoilsException(
                    'processId value must be an integer value.'
                )

        self.target_message_label = self.process_label_substitutions(
            self.action_parameters.get('label', None)
        )
        if not self.target_message_label:
            raise CoilsException(
                'No "label" specified, this parameter is required.'
            )
