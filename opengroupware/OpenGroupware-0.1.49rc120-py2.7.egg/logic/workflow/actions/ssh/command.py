#
# Copyright (c) 2012, 2013, 2017, 2018
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
#
import os
# Justification for os import
#   We need to expand the path to the current user's home directory
#   in order to provide a reasonable default path to the SSH private
#   key
from io import UnsupportedOperation
from os.path import dirname, basename
from glob import fnmatch
import shutil
import paramiko
from coils.core import \
    CoilsException, \
    ServerDefaultsManager, \
    walk_ogo_uri_to_target, \
    Document


NO_PRIVATE_KEY_FOUND_MESSAGE = '''No path provided to SSH private key; the
 "OIESSHPrivateKeyPath" default was not set so the server attempted to find
 a filesystem object at ~/.ssh/id_dsa and then ~/.ssh/id_rsa but neither of
 these paths exist.  Either SSH is not configured for the OpenGroupware
 service user, the permissions are incorrect, or the administrator should
 explicitly set the path to the intended private key by establishing a value
 for the  "OIESSHPrivateKeyPath" default. '''

INCORRECT_PRIVATE_KEY_PATH = '''The "OIESSHPrivateKeyPath" default specifies
 a path to the SSH private key of "{0}", but this
 path does not exists or is not accessible.  Perhaps the value of the default
 is incorrect or filesystem permissions are incorrect.'''

UNABLE_TO_LOAD_PRIVATE_KEY = '''The SSH functions were unable to load the
 private key from the path "{0}" using the provided
 credentials although this path exists.  Double check credentials required
 to load the key or that this is a valid SSH private key.
 Exception raised was:
   {1}'''


class SSHAction(object):

    def initialize_client(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return ssh

    def path_to_default_private_key(self):
        sd = ServerDefaultsManager()
        key_path = sd.string_for_default('OIESSHPrivateKeyPath', value='', )
        if not key_path:
            key_path = os.path.expanduser('~/.ssh/id_dsa')
            if os.path.exists(key_path):
                return key_path
            key_path = os.path.expanduser('~/.ssh/id_rsa')
            if os.path.exists:
                return key_path
            raise CoilsException(NO_PRIVATE_KEY_FOUND_MESSAGE)
        else:
            if os.path.exists(key_path):
                return key_path
            raise CoilsException(INCORRECT_PRIVATE_KEY_PATH.format(key_path, ))

    def resolve_private_key(self):
        if not self._key_uri:
            return self.path_to_default_private_key(), None
        key_document = walk_ogo_uri_to_target(self._ctx, self._key_uri)
        if not key_document:
            raise CoilsException(
                'Unable to resolve URI specified for private key; URI = "{0}"'.
                format(self._key_uri)
            )
        if not isinstance(key_document, Document):
            raise CoilsException(
                'URI specified for private key did not resolve to a document;'
                'URI = "{0}"'.format(self._key_uri, )
            )
        handle = self._ctx.run_command(
            'document::get-handle',
            document=key_document,
        )
        if not handle:
            raise CoilsException(
                'Unable to marshall handle to private key file document URI'
                'which resolved to OGo#{0}'.format(key_document.object_id, )
            )
        return None, handle

    def initialize_private_key(
        self,
        path=None,
        handle=None,
        password=None,
        key_type='dss',
    ):
        try:

            if key_type == 'rsa':
                key_class = paramiko.RSAKey
            elif key_type in ('dss', 'dsa', ):
                key_class = paramiko.DSSKey
            else:
                raise CoilsException(
                    'unsupported SSH key type "{0}" requested'.
                    format(key_type, )
                )
            self.log_message(
                'key class is {0}'.format(key_class, ),
                category='debug',
            )
            if path:
                self.log_message(
                    'loading private key from "{0}"'.format(path, ),
                    category='debug',
                )
                private_key = \
                    key_class.from_private_key_file(
                        path,
                        password=password,
                    )
            else:
                self.log_message(
                    'loading private key from "{0}"'.format(handle, ),
                    category='debug',
                )
                private_key = \
                    key_class.from_private_key(
                        handle,
                        password=password,
                    )

        except Exception as exc:
            raise CoilsException(
                UNABLE_TO_LOAD_PRIVATE_KEY.format(path, exc),
                inner_exception=exc,
            )

        self.log_message(
            '{0} private key initialized: fingerprint {1}'.
            format(
                private_key.get_name(),
                ':'.join(
                    ['%02X' % ord(x) for x in private_key.get_fingerprint()]
                )
            ),
            category='info',
        )
        return private_key

    def initialize_transport(self, hostname, port=22):
        # TODO: Add exception handling
        transport = paramiko.Transport((hostname, port, ))
        transport.set_keepalive(30)
        transport.start_client()
        self.log_message(
            'transport initialized with {0}:{1}'
            .format(hostname, port, ),
            category='info',
        )
        self.log_message(
            'remote version is {0}'.format(transport.remote_version, ),
            category='debug',
        )
        return transport

    def authenticate(self, transport, username, private_key):
        # TODO: Add exception handling
        transport.auth_publickey(username, private_key)
        return transport.is_authenticated

    def run_command(
        self, transport, command, wfile, efile=None, truncate=True,
    ):
        # TODO: Add exception handling
        self.log_message(
            'Attempting to execute "{0}" on remote host'.
            format(command, ),
            category='debug',
        )
        channel = transport.open_session()
        self.log_message('Channel created', category='debug', )
        stdout = channel.makefile('rb')
        stderr = channel.makefile_stderr('rb')
        if truncate:
            wfile.seek(0)
            wfile.truncate()
            self.log_message('Output stream reset', category='debug', )
        # Channel will be automatically closed when command completes
        channel.exec_command(command)
        self.log_message('Command executed', category='debug', )
        shutil.copyfileobj(stdout, wfile)
        if efile:
            shutil.copyfileobj(stderr, efile)
        exit_status = channel.recv_exit_status()
        self.log_message(
            'Command exit status is: {0}/{1}'.
            format(
                exit_status,
                type(exit_status),
            ),
            category='debug',
        )
        if exit_status != 0:
            # A non-zero exit status indicates failure
            self.log_message('Command execution failed', category='info')
            raise CoilsException(
                'Execution of command "{0}" failed on host "{1}"'.
                format(command, self._hostname, )
            )
        else:
            self.log_message('Command execution completed.', category='info', )
        return True

    def match_files(self, transport, pattern):
        """
        sftp does not support wildcard search; this is a hack to have
        wildcard file matching when using sftp.
        WARNING: wildcards only supported in the filename portion of the
        path - wildcards are not supported in the path.
        """
        do_close = None  # will be determined based upon type of "transport"
        pattern = pattern.strip()  # take whitespace off the pattern
        folder_path = dirname(pattern)
        file_pattern = basename(pattern)
        if isinstance(transport, paramiko.transport.Transport):
            if not transport.is_authenticated():
                raise CoilsException(
                    'Paramiko Transport is not yet authenticated; cannot '
                    'marshall an SFTPClient instance'
                )
            ftp = transport.open_sftp_client()
            do_close = True  # Close the transport when we are done
        elif isinstance(transport, paramiko.sftp_client.SFTPClient):
            ftp = transport
            do_close = False  # Do not close the transport
        elif 'Mock' in str(transport.__class__):
            # HACK: this allows testing to work
            ftp = transport.open_sftp_client()
            do_close = False
        else:
            raise CoilsException(
                'Unexpected class as transport, {0}.  Transport must be '
                'either a Paramiko Transport or SFTPClient instance'
                .format(type(transport), )
            )
        result = list()
        for file_name in ftp.listdir(folder_path):
            if fnmatch.fnmatch(file_name, file_pattern):
                result.append(os.path.join(folder_path, file_name))
        if do_close:
            # this method created the transport, so close the transport
            ftp.close()
        return result

    def get_file(self, transport, path, wfile, truncate=True):
        # TODO: Add exception handling
        ftp = transport.open_sftp_client()
        rfile = ftp.open(path)
        if truncate:
            wfile.seek(0)
            wfile.truncate()
        shutil.copyfileobj(rfile, wfile)
        wfile.flush()
        rfile.close()
        ftp.close()

    def get_fileinfo(self, transport, path):
        """
        Get a FileInfo object about the object at the specified path; if no
        such path exists this method will return None.
        """

        class FileInfo(object):

            def __init__(self, fpath, finfo):
                self.size = finfo.st_size
                self.uid = finfo.st_uid
                self.path = fpath

        info = None
        ftp = transport.open_sftp_client()
        try:
            info = ftp.lstat(path)
        except IOError as exc:
            # IOError: [Errno 2] No such file
            if not exc.errno == 2:
                # only capture file-not-found
                raise exc
            info = None
        finally:
            ftp.close()
        if info:
            return FileInfo(path, info)
        return None

    def put_file(
        self, transport, path, rfile, truncate=True, close_after=True,
    ):
        """
        Create an SFTP transport and write the contents of rfile to the
        specified path.  By default the target file will be truncated prior
        to write; if the specified path already exists on the remote the
        existing file is opened [it is NOT replaced].  By default the method
        will close the transport and the target file after write, use
        close_after=False
        """
        # TODO: Add exception handling, what exceptions?
        ftp = transport.open_sftp_client()
        # Use file mode to control truncation
        self.log_message(
            'Attempting to open "{0}"'.format(path, ),
            category='debug',
        )
        if truncate:
            wfile = ftp.open(path, mode='w')
        else:
            wfile = ftp.open(path, mode='r+')
        seek_support = True
        try:
            rfile.seek(0)
        except UnsupportedOperation:
            seek_support = False
            pass
        shutil.copyfileobj(rfile, wfile)
        wfile.flush()
        if not seek_support:
            self.log_message(
                'Wrote {0} octets to path "{1}"'.format(wfile.tell(), path, ),
                category='debug',
            )
        else:
            self.log_message(
                'Wrote {0} octets to path "{1}", offset of input stream is {2}'
                .format(wfile.tell(), path, rfile.tell(), ),
                category='debug',
            )
        if close_after:
            rfile.close()
            wfile.close()
            ftp.close()
            return None, None
        else:
            return wfile, ftp

    def close_transport(self, transport):
        transport.close()

    def parse_action_parameters(self):
        self._hostname = self.action_parameters.get('hostname', None)
        self._hostport = self.action_parameters.get('port', 22)
        self._secret = self.action_parameters.get('passphrase', None)
        self._username = self.action_parameters.get('username', 'ogo')
        self._key_uri = self.action_parameters.get('keyURI', None)
        self._key_type = self.action_parameters.get('keyType', 'dss').lower()

        if not self._hostname:
            raise CoilsException(
                'No hostname specified for SSHAction derived action'
            )

        self._hostname = self.process_label_substitutions(self._hostname)
        self._hostport = int(self.process_label_substitutions(self._hostport))
