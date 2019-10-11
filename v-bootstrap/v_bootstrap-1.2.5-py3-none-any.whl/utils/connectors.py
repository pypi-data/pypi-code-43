import sys
import time
import serial
import logging

import paramiko

from abc import ABCMeta, abstractmethod
from v_bootstrap.utils.errors import ConnectorError, ConnectorExecuteError

_DEFAULT_BAUDRATE = 115200
_DEFAULT_TIMEOUT = 10

_CREDENTIALS_PROMPT_USER = 'login'
_CREDENTIALS_PROMPT_PASS = 'Password'

logger = logging.getLogger(__name__)
logging.getLogger("paramiko").setLevel(logging.WARNING)


def _handle_response(func):
    """ Grabs the response and the exit code from raw_data. """

    def _call(self, cmd, **kwargs):
        ret = func(self, cmd, **kwargs)
        ret = ret.replace("\r", "")
        raw_data = ret.splitlines()
        response = ''
        exit_code = -1

        if len(raw_data) >= 3:
            # get valuable data from the response
            # omit cmd and a tail with an exit code
            response = '\n'.join(raw_data[1:-3])
            # get exit code
            try:
                exit_code = int(raw_data[-2])
            except ValueError:
                pass

        return ConnectorResponse(cmd, exit_code, response)

    return _call


class ConnectorResponse(object):
    def __init__(self, cmd, code, response):
        self.cmd = cmd
        self.exit_code = code
        self.data = response

    def __str__(self):
        return "Command: {}, Exit code: " \
               "{}\n{}".format(self.cmd, self.exit_code, self.data)


class Connector(object):
    __metaclass__ = ABCMeta

    def __init__(self, address, cred=None):
        self._address = address
        self._cred = cred

    @property
    def address(self):
        return self._address

    @property
    def auth(self):
        return self._cred

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass


class SerialConnector(Connector):
    def __init__(self, address, cred=None,
                 baudrate=_DEFAULT_BAUDRATE, timeout=_DEFAULT_TIMEOUT):
        super(SerialConnector, self).__init__(address, cred)
        self._baudrate = baudrate
        self._timeout = timeout
        self._user, self._pass = self.auth if self.auth else None, None
        self._console = None

    def connect(self):
        try:
            self._console = serial.Serial(self.address,
                                          baudrate=self._baudrate,
                                          timeout=self._timeout)
        except serial.SerialException as e:
            logger.debug(e)
            raise ConnectorError("Failed to connect "
                                 "to port {}".format(self.address))

        if self._console and self._console.is_open:
            logger.debug('Connected to port %s.', self.address)
            self._login()

    def _wait_for_boot(self, timeout=3):
        sys.stdout.write("waiting for device ready (this may take a while) ...\n")
        sys.stdout.flush()

        while True:
            time.sleep(timeout)
            r_count = self._console.in_waiting
            if r_count == 0:
                break
            self._console.read(r_count)

    def _login(self):
        self._wait_for_boot()

        if self._verify_login():
            logger.debug('Already signed in.')
            self._write('cd ~')
            return

        retry = 0
        logged = False
        while retry <= 10:
            retry += 1

            self._write('\n')

            input_str = self._read()
            if _CREDENTIALS_PROMPT_USER not in input_str:
                self._wait_for_boot(timeout=5)
                continue

            self._write('root')

            if self._verify_login():
                logger.debug("Logged in to board.")
                logged = True
                break

        if not logged:
            raise ConnectorError('Failed to login to board.')

        logger.debug('Successful logged in')
        logger.debug('Waiting for login script is finished...')
        self._wait_for_boot(timeout=8)
        self._write('cd ~')

    def _logout(self):
        self._write('exit')
        logger.debug('Logged out from board')

    def _verify_login(self):
        status = False
        self._console.write(b"\n")
        time.sleep(1)

        prompt = self._read()
        readed_len = len(prompt)
        if readed_len > 0 and ('>' == prompt[readed_len-1] or '#' == prompt[readed_len-1]):
            status = True

        return status

    def _read(self):
        response = ''
        r_count = self._console.in_waiting
        ret = self._console.read(r_count)

        if ret:
            response = ret.strip().decode()

        return response

    def _write(self, data):
        send_data = ''.join((data, '\n'))
        count = self._console.write(send_data.encode('utf-8'))

        return count

    def send(self, data):
        return self._write(data)

    def clear(self):
        return self._console.reset_input_buffer()

    @_handle_response
    def execute(self, cmd, debug=True):
        try:
            self.clear()
            cmd = '\n'.join((cmd, 'echo $?'))
            self._write(cmd)

            raw_data = ''
            while True:
                raw_data_chunk = self._read()
                if len(raw_data_chunk):
                    raw_data += raw_data_chunk

                    if debug:
                        logger.debug('RESPONSE chunk:\n' + raw_data_chunk.replace("\r", ""))

                f_pos = raw_data.find("dom0:~#")
                if f_pos >= 0:
                    s_pos = raw_data.find("dom0:~#", f_pos+3)
                if f_pos >= 0 and s_pos >= 0:
                    break
                else:
                    time.sleep(0.3)

        except serial.SerialException as e:
            logger.debug(e)
            raise ConnectorExecuteError('Failed to execute a remote command.')

        return raw_data

    @_handle_response
    def execute_script(self, cmd, debug=True):
        try:
            self.clear()
            self._write(cmd)

            raw_data = ''
            while True:
                raw_data_chunk = self._read()
                if len(raw_data_chunk):
                    raw_data += raw_data_chunk
                    if debug:
                        logger.debug('RESPONSE chunk:\n' + raw_data_chunk.replace("\r", ""))

                if "dom0:~#" in raw_data:
                    break
                else:
                    time.sleep(0.3)

            self._write("echo $?")
            raw_data_chunk = self._read()
            if len(raw_data_chunk):
                raw_data += raw_data_chunk
                if debug:
                    logger.debug('RESPONSE chunk:\n' + raw_data_chunk.replace("\r", ""))
        except serial.SerialException as e:
            logger.error(e)
            raise ConnectorExecuteError('Failed to execute a remote command.')

        return raw_data

    def close(self):
        self._console.close()


class SSHConnector(Connector):
    def __init__(self, address, port=22, cred=None):
        super(SSHConnector, self).__init__(address, cred)
        self._port = port
        self._client = None

    def connect(self):
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            cred = {}
            if self.auth is None:
                self._client.load_system_host_keys()
            else:
                cred['username'], cred['password'] = self.auth

            self._client.connect(self.address, port=self._port, **cred)
        except (OSError, paramiko.SSHException) as e:
            logger.debug(e)
            raise ConnectorExecuteError('Failed to connect to device.')

    def execute(self, cmd, debug=True):
        try:
            _, stdout, stderr = self._client.exec_command(cmd)
            response = stdout.read()
            exit_code = stdout.channel.recv_exit_status()

            if debug and exit_code and stderr:
                logger.debug(stderr.read())
        except paramiko.SSHException as e:
            logger.debug(e)
            raise ConnectorExecuteError('Failed to execute a remote command.')

        return ConnectorResponse(cmd, exit_code, response)

    def close(self):
        self._client.close()
