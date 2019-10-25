#
# Copyright (c) 2017
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import os
import traceback
import gnupg
from coils.foundation import Document, BLOBManager
from utility import walk_ogo_uri_to_folder
from exception import CoilsException

GPG_MIMETYPES = ['application/pgp-keys', ]


class GPG(object):

    def __init__(self, context):
        self.context = context
        self.gpg = None
        sd = self.context.server_defaults_manager
        self.gpg_path = sd.string_for_default(
            'GNUPGBinaryPath', '/usr/bin/gpg',
        )
        sd = None

    def initialize(self, uri, ):
        log_lines = list()
        self.working_path = BLOBManager.CreateWorkingDirectory(self.context.login, )  # noqa
        log_lines.append((
            'debug',
            'GPG working directory: {0}'.format(self.working_path, )
        ))

        """sanity checks, this is secure data - so let's be paranoid"""
        if not os.path.exists(self.working_path):
            raise CoilsException('Expected working path does not exist!')
        if not os.path.isdir(self.working_path):
            raise CoilsException('Expected working path is not a directory!')
        try:
            sfile = open(os.path.join(self.working_path, 'write_test'), 'w')
            sfile.write('write test')
            sfile.close()
            sfile = None
        except Exception as exc:
            raise CoilsException(
                'Test indicates working path is not writable.'
            )
        log_lines.append(('debug', 'working directory appears to be sane'))

        """try to setup GPG environment"""
        try:
            self.context.log.debug(
                'GNUPG binary="{0}" homedir="{1}"'
                .format(self.gpg_path, self.working_path, )
            )
            self.gpg = gnupg.GPG(
                gpgbinary=self.gpg_path,
                gnupghome=self.working_path,
            )
            self.context.log.debug('GNUPG environment initialized')
        except Exception as exc:
            self.context.log.exception('GNUPG environment initialized')
            log_lines.append((
                'error',
                'failure to create GPG environment: {0}\n{1}'
                .format(exc, traceback.format_exc(), )
            ))
            return False, list(), log_lines
        log_lines.append(('debug', 'GPG started'))
        folder, tmp_ = walk_ogo_uri_to_folder(self.context, uri, )
        log_lines.append(('info', 'importing keys from "{0}"'.format(uri, )))
        if not folder:
            raise CoilsException()
        for document in self.context.r_c('folder::ls', folder=folder):
            if not isinstance(document, Document):
                continue
            try:
                mimetype = self.context.type_manager.get_mimetype(document)
                if mimetype not in GPG_MIMETYPES:
                    print('skipping non-key content')
                    continue
                log_lines.append((
                    'info',
                    'attempting to load keys from OGo#{0}: "{1}"'
                    .format(document.object_id, document.get_display_name(), )
                ))
                handle = self.context.r_c(
                    'document::get-handle', document=document,
                )
                if not handle:
                    log_lines.append((
                        'info',
                        'unable to marshall OGo#{0}'
                        .format(document.object_id, )
                    ))
                    continue
                key_data = handle.read()
                BLOBManager.Close(handle)
                result = self.gpg.import_keys(key_data)
                for fingerprint in result.fingerprints:
                    log_lines.append((
                        'info',
                        'imported key with fingerprint {0} from OGo#{1}'
                        .format(fingerprint, document.object_id, )
                    ))
            except Exception as exc:
                log_lines.append((
                    'warn',
                    'Failed to import key from document OGo#{0}'
                    .format(document.object_id, )
                ))
                log_lines.append((
                    'info', 'exception: {0}'.format(exc, )
                ))
        return True, result.fingerprints, log_lines

    def encrypt(
        self, rfile, wfile, recipients,
        sign_as=None,
        passphrase=None,
        armor=True,
    ):
        # TODO: check recipients are in key store
        log_lines = list()
        result = None
        if sign_as:
            log_lines.append((
                'info',
                'encrypting stream for recipient {0} signed as {1}'
                .format(recipients, sign_as, )
            ))
            result = self.gpg.encrypt_file(
                rfile, recipients,
                sign=sign_as,
                passphrase=passphrase,
                armor=armor,
                always_trust=True,
            )
        else:
            log_lines.append((
                'info', 'encrypting stream for recipient {0}'
                .format(recipients, )
            ))
            result = self.gpg.encrypt(
                rfile, recipients,
                armor=armor,
                always_trust=True,
            )

        if result.ok:
            log_lines.append(('info', 'encryption succeeded', ))
            wfile.write(result.data)
            return True, log_lines
        for record in result.stderr:
            log_lines.append(('debug', record, ))
        return False, log_lines

    def sign(
        self, rfile, wfile,
        sign_as=None,
        passphrase=None,
        armor=True,
    ):
        # TODO: check recipients are in key store
        log_lines = list()
        """
        pythong-gnupg 0.4.0
        sign_file(self, file, keyid=None, passphrase=None, clearsign=True,
                  detach=False, binary=False, output=None, extra_args=None):
        """
        try:
            sign = self.gpg.sign_file(
                rfile,
                keyid=sign_as,
                clearsign=False,
                passphrase=passphrase,
            )
            log_lines.append(('info', 'signing succeeded', ))
        except Exception as exc:
            log_lines.append(('debug', sign.stderr, ))
            log_lines.append(('error', exc, ))
            return False, log_lines
        else:
            wfile.write(sign.data)
        return True, log_lines

    def close(self):
        if not hasattr(self, 'working_path'):
            # perhaps the object was not initialized
            return
        BLOBManager.DeleteWorkingDirectory(self.working_path)
