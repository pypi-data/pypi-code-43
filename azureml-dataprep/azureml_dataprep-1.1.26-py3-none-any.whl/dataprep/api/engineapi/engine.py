# Copyright (c) Microsoft Corporation. All rights reserved.
"""Launch and exchange messages with the engine."""
import atexit
import json
import os
import subprocess
import sys
from threading import Thread, Event
from typing import Callable
from dotnetcore2 import runtime
from .typedefinitions import CustomEncoder
from ..errorhandlers import raise_engine_error, ExecutionError

from .._loggerfactory import session_id, instrumentation_key, _LoggerFactory


log = _LoggerFactory.get_logger('dprep.engine')


class CancellationToken:
    def __init__(self):
        self._callbacks = []
        self.is_canceled = False

    def register(self, callback):
        self._callbacks.append(callback)

    def cancel(self):
        self.is_canceled = True
        for cb in self._callbacks:
            cb()


class MessageChannel:
    """Channel for JSON messages to the local engine process."""
    def __init__(self, process_opener: Callable[[], subprocess.Popen]):
        self._process_opener = process_opener
        self._last_message_id = 0
        self._process = None
        self._relaunch_callback = None
        self._pending_messages = {}
        self._ensure_process()

        def process_responses():
            while True:
                try:
                    response = self._read_response()
                    pending_message = self._pending_messages[response['id']]
                    pending_message['response'] = response
                    pending_message['event'].set()
                except Exception:
                    for pending_message in self._pending_messages:
                        pending_message['event'].set()

        self._responses_thread = Thread(target=process_responses, daemon=True)
        self._responses_thread.start()

    def on_relaunch(self, callback: Callable[[], None]):
        self._relaunch_callback = callback

    def close(self):
        """Close the underlying process."""
        self._process.terminate()
        try:
            self._process.wait(10)
        except subprocess.TimeoutExpired:
            self._process.kill()

    def send_message(self, op_code: str, message: object, cancellation_token: CancellationToken = None) -> object:
        """Send a message to the engine, and wait for its response."""
        self._last_message_id += 1
        message_id = self._last_message_id
        is_done = False

        def cancel_message():
            if is_done:
                return

            self.send_message('CancelMessage', {'idToCancel': message_id})

        if cancellation_token is not None:
            cancellation_token.register(cancel_message)

        event = Event()
        self._pending_messages[message_id] = {'event': event, 'response': None}
        self._write_line(json.dumps({
            "messageId": message_id,
            "opCode": op_code,
            "data": message
        }, cls=CustomEncoder))

        event.wait()
        response = self._pending_messages.pop(message_id, None)['response']
        is_done = True

        def cancel_on_error():
            if cancellation_token is not None:
                cancellation_token.cancel()

        if response is None:
            cancel_on_error()
            raise ExecutionError({'errorData': {'errorMessage': 'An unknown error has occurred.'}})

        if 'error' in response:
            cancel_on_error()
            raise_engine_error(response['error'])
        else:
            return response['result']

    def _write_line(self, line: str):
        self._ensure_process()
        self._process.stdin.write(line.encode())
        self._process.stdin.write('\n'.encode())
        self._process.stdin.flush()

    def _read_response(self) -> dict:
        self._ensure_process()
        string = None
        while string is None:
            line = self._process.stdout.readline()
            string = line.decode()
            if len(string) == 0 or string[0] != '{':
                string = None

        parsed = None
        try:
            parsed = json.loads(string)
        finally:
            if parsed is None:  # Exception is being thrown
                print("Line read from engine could not be parsed as JSON. Line:")
                try:
                    print(string)
                except UnicodeEncodeError:
                    print(bytes(string, 'utf-8'))
        return parsed

    def _ensure_process(self):
        if self._process is None or self._process.poll() is not None:
            self._process = self._process_opener()
            for pending_message in self._pending_messages.values():
                pending_message['event'].set()

            self._pending_messages.clear()
            if self._relaunch_callback is not None:
                self._relaunch_callback()


def launch_engine() -> MessageChannel:
    """Launch the engine process and set up a MessageChannel."""
    engine_args = {
        'debug': 'false',
        'firstLaunch': 'false',
        'sessionId': session_id,
        'invokingPythonPath': sys.executable,
        'invokingPythonWorkingDirectory': os.path.join(os.getcwd(), ''),
        'instrumentationKey': '' if os.environ.get('DISABLE_DPREP_LOGGER') is not None else instrumentation_key
    }

    engine_path = _get_engine_path()
    dependencies_path = runtime.ensure_dependencies()
    dotnet_path = runtime.get_runtime_path()
    env = os.environ.copy()
    env['DOTNET_SYSTEM_GLOBALIZATION_INVARIANT'] = 'true'
    if dependencies_path is not None:
        env['LD_LIBRARY_PATH'] = dependencies_path
    _set_sslcert_path(env)

    def create_engine_process():
        return subprocess.Popen(
            [dotnet_path, engine_path, json.dumps(engine_args)],
            bufsize=5 * 1024 * 1024,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # Hide spurious dotnet errors (Vienna:45714) TODO: collect Errors
            env=env)
    channel = MessageChannel(create_engine_process)
    atexit.register(channel.close)
    return channel


def _get_engine_path():
    engine_dll = "Microsoft.DPrep.Execution.EngineHost.dll"
    current_folder = os.path.dirname(os.path.realpath(__file__))
    engine_path = os.path.join(current_folder, 'bin', engine_dll)
    return engine_path


def _set_sslcert_path(env):
    if sys.platform in ['win32', 'darwin']:
        return  # no need to set ssl cert path for Windows and macOS

    SSL_CERT_FILE = 'SSL_CERT_FILE'
    if SSL_CERT_FILE in env:
        return  # skip if user has set SSL_CERT_FILE

    try:
        import certifi
        cert_path = os.path.join(os.path.dirname(certifi.__file__), 'cacert.pem')
        if os.path.isfile(cert_path):
            env[SSL_CERT_FILE] = cert_path
    except Exception:
        pass  # keep going since the trusted cert is only missing for some distro of Linux
