#
# Copyright (c) 2017, 2018
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
import zipfile
from smtplib import SMTPRecipientsRefused
from email.Utils import COMMASPACE
from email.generator import Generator
from coils.core import BLOBManager
from .command import MailAction


class SendMailMessagesAction(MailAction):
    __domain__ = "action"
    __operation__ = "send-mail-messsages"
    __aliases__ = ['sendMailMessages', 'sendMailMessagesAction', ]

    def __init__(self):
        MailAction.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/zip'

    def _add_meta_data_to_message(self, message):
        if self.process.task_id:
            message['X-Opengroupware-Regarding'] = str(
                self.process.task_id
            )
        else:
            message['X-Opengroupware-Regarding'] = str(self.pid)
        message['X-Opengroupware-Process-Id'] = str(self.pid)
        message['X-Opengroupware-Context'] = (
            '{0}[{1}]'.format(
                self._ctx.get_login(), self._ctx.account_id,
            )
        )

    def do_action(self):

        zfile = zipfile.ZipFile(
            self.wfile, 'a', compression=zipfile.ZIP_DEFLATED,
        )

        all_counter = 0
        sent_counter = 0
        error_counter = 0

        if self._target_address:
            self.log_message(
                'messages will be sent to "{0}"'.format(self._target_address),
                category='info',
            )
        else:
            self.log_message(
                'messages will be sent to the recipients within the envelope',
                category='info',
            )

        for handle, object_name, in self._yield_input_handles_and_name():

            all_counter += 1
            if not (all_counter % 20):
                # gong every 20 messages
                self.gong()

            try:
                message = self._get_message_from_input(handle)
            except Exception as exc:
                self.log_message(
                    'Unable to parse message from object named "{0}".'
                    .format(object_name, ),
                    category='debug',
                )
                self.log_exception(exc)
                continue
            message_id = message.get('message-id')

            self.log_message(
                'Message "{0}" read from object named "{1}".'
                .format(message_id, object_name, ),
                category='debug',
            )

            if not self._target_address:
                addresses = self._get_addresses_from_message(message)
                if not addresses:
                    self.log_message(
                        'Message "{0}" contains no recipients, skipped.',
                        category='warn',
                    )
                    continue

                self.log_message(
                    'Message "{0}" has {1} recipients: {2}.'
                    .format(
                        message_id, len(addresses), COMMASPACE.join(addresses),
                    ), category='debug',
                )
            else:
                addresses = [self._target_address, ]

            if self._add_meta_data_headers:
                self._add_meta_data_to_message(message)

            # From: HACK
            from_address = None
            if self._from_address:
                from_address = self._from_address
                # From: address rewritten via directive "overwriteFromAddress"
                if 'from' in message:
                    message.replace_header('from', from_address)
                else:
                    message.add_header('from', from_address)
                # Return-Path:
                if 'Return-Path' in message:
                    message.replace_header('Return-Path', from_address)
                else:
                    message.add_header('Return-Path', from_address)
                # Reply-To
                if 'Reply-To' in message:
                    message.replace_header('Reply-To', from_address)
                # Sender
                if 'Sender' in message:
                    message.replace_header('Sender', from_address)
            elif 'from' in message:
                from_address = message['from']
            else:
                from_address = (
                    self._ctx.server_defaults_manager.string_for_default(
                        'SMTPSenderAddress',
                        'server_not_configured@example.com',
                    )
                )

            # To: HACK
            if self._to_address:
                # From: address rewritten via directive "overwriteFromAddress"
                if 'to' in message:
                    message.replace_header('to', self._to_address)
                else:
                    message.add_header('to', self._to_address)
                # strip Cc: header
                if 'cc' in message:
                    del message['cc']

            try:
                self.send_smtp_message(
                    from_address=from_address,
                    to_addresses=addresses,
                    message=message,
                )
                sent_counter += 1
            except SMTPRecipientsRefused:
                self.log_message(
                    'Message "{0}" rejected due to recipients (SMTP/501)'
                    .format(message_id, ), category='debug',
                )
                error_counter += 1
            else:
                self.log_message(
                    'Message "{0}" sent.'.format(message_id, ),
                    category='debug',
                )

            sfile = BLOBManager.ScratchFile(require_named_file=True, )
            g = Generator(sfile, mangle_from_=False, maxheaderlen=255, )
            g.flatten(message)
            sfile.flush()
            sfile.seek(0)
            message = None
            zfile.write(sfile.name, arcname='{0}.mbox'.format(message_id, ))
            BLOBManager.Close(sfile)

        zfile.close()
        self.wfile.flush()
        self.log_message('ZIP document closed and flushed', category='debug', )

        self.log_message(
            'Sent {0} messages; {1} messages refused due to errors'
            .format(sent_counter, error_counter, ),
            category='info',
        )

    def parse_action_parameters(self):

        self._add_meta_data_headers = True if self.action_parameters.get(
            'addMetadataHeaders', 'NO'
        ).upper() == 'YES' else False

        self._target_address = self.process_label_substitutions(
            self.action_parameters.get(
                'targetSMTPAddress', None,
            )
        )

        self._from_address = self.process_label_substitutions(
            self.action_parameters.get(
                'overwriteFromAddress', None,
            )
        )

        self._to_address = self.process_label_substitutions(
            self.action_parameters.get(
                'overwriteToAddress', None,
            )
        )

    def do_epilogue(self):
        pass
