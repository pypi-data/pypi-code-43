#
# Copyright (c) 2017
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
import traceback
from coils.core import GPG, CoilsException
from coils.core.logic import ActionCommand


class GPGEncryptAction(ActionCommand):
    __domain__ = 'action'
    __operation__ = 'gpg-encrypt'
    __aliases__ = ['gpgEncrypt', 'gpgEncryptAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/pdf'

    def do_action(self):

        """initialize GPG object"""
        gpg = GPG(self._ctx)
        try:
            status, fingerprints, notices, = gpg.initialize(self._key_store_uri)
            for notice in notices:
                self.log_message(notice[1], category=notice[0], )
            if not status:
                raise CoilsException('Failure to marshall GPG environment')
        except Exception as exc:
            self._ctx.log.exception(exc)
            gpg.close()
            raise CoilsException('Exception initializing GPG context')

        """perform GPG encrypption"""
        try:
            if self._gpg_signatur:
                # with signature
                status, notices, = gpg.encrypt(
                    rfile=self.rfile,
                    wfile=self.wfile,
                    recipients=self._gpg_recipients,
                    sign_as=self._gpg_signatur,
                    passphrase=self._gpg_passphrase,
                )
            else:
                # without signature
                status, notices, = gpg.encrypt(
                    rfile=self.rfile,
                    wfile=self.wfile,
                    recipients=self._gpg_recipients,
                )
            for notice in notices:
                self.log_message(notice[1], category=notice[0], )
            if not status:
                raise CoilsException('GPG encryption of message failed')
        except Exception as exc:
            self._ctx.log.exception(exc)
            self.log_message(
                'exception during GPG encryption:\n{0}'
                .format(traceback.format_exc(), ),
                category='warn',
            )
            raise exc
        finally:
            # close the gpg object for security purposes
            gpg.close()

    def parse_action_parameters(self):

        # TODO: default keystore to user home project, someday?
        self._key_store_uri = (
            self.process_label_substitutions(
                self.action_parameters.get('keyStoreURI', None),
            )
        )

        self._gpg_recipients = (
            self.process_label_substitutions(
                self.action_parameters.get('gpgRecipientID', None),
            )
        )
        # TODO: error if no recipients?

        self._gpg_signatur = (
            self.process_label_substitutions(
                self.action_parameters.get('gpgSignatureID', None),
            )
        )

        self._gpg_passphrase = (
            self.process_label_substitutions(
                self.action_parameters.get('gpgPassphrase', None),
            )
        )

    def do_epilogue(self):
        pass
