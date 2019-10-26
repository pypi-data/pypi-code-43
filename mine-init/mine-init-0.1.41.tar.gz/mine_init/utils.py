"""
| Utilities for mine_init
"""
import os
import re
import subprocess
import email
import threading
import signal
import sys
import logging
from logging.handlers import BufferingHandler
from smtplib import SMTP, SMTPException
import yaml


JAVA_PARAMS = {
    'memory': os.getenv('JAVA_MEM', '4096m'),
    'fml_confirm': os.getenv('FML_CONFIRM', 'cancel')
}


class MakeFileHandler(logging.FileHandler):
    """
    | A file handler class that ensures the logging dir is precreated
    """
    def __init__(self, filename, mode='a', encoding=None, delay=0):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)


class BufferingSMTPHandler(BufferingHandler):
    """
    | A log handler that buffers messages into memory to deliver them as a single email.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, mail_server, mail_port, src_email, dest_email, capacity):
        BufferingHandler.__init__(self, capacity)
        self.mail_server = mail_server
        self.mail_port = mail_port
        self.src_email = src_email
        self.dest_email = dest_email
        self.subject = None
        self.description = None
        self.cc_list = None
        self.send = False

    def flush(self):
        if self.buffer and self.send:
            try:
                message = email.message.EmailMessage()
                message['Sender'] = self.src_email
                message['To'] = self.dest_email
                if self.cc_list:
                    message['Cc'] = ','.join(self.cc_list)
                message['Subject'] = self.subject
                body = self.description + '\r\n'
                for record in self.buffer:
                    log_line = self.format(record)
                    body = body + log_line + "\r\n"
                message.set_content(body)
                with SMTP(self.mail_server, self.mail_port) as smtp:
                    smtp.send_message(message)
            except SMTPException as error:
                self.handleError(error)
            self.buffer = []

    def send_email(self, subject, description, cc_list=None):
        """
        | Send email by calling flush after setting some last minute details.
        | :param subject: `string` Subject for outgoing email
        | :param description: `string` Opening paragraph for email
        | :param cc_list: `list` List of emails to CC for this
        | :return: `void`
        """
        self.send = True
        self.subject = subject
        self.description = description
        if cc_list:
            self.cc_list = cc_list
        self.flush()


class LogPipe(threading.Thread):
    """
    | Build a logging thread for subprocesses.
    """
    def __init__(self):
        """
        | Setup the object with a logger and a loglevel
        | and start the thread
        """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger('mine-init')
        self.daemon = False

        self.fdread, self.fdwrite = os.pipe()
        self.pipereader = os.fdopen(self.fdread)
        self.start()

    def fileno(self):
        """
        | Return the write file descriptor of the pipe
        """
        return self.fdwrite

    def run(self):
        """
        | Run the thread, logging everything.
        """
        for line in iter(self.pipereader.readline, ''):
            self.logger.info(line.strip('\n'))

        self.pipereader.close()

    def close(self):
        """
        | Close the write end of the pipe.
        """
        os.close(self.fdwrite)


class PropertyFileManager:
    """
    | Manages server.properties files.
    """
    def __init__(self, filename, properties):
        """
        | Finds and replaces properties lines in server.properties
        |
        | :param filename: File path to server.properties
        | :param properties: `dict` The properties to update
        """
        self.logger = logging.getLogger('mine-init')
        self.filename = filename
        self.properties = properties
        self.lines = ''

    def read(self):
        """
        | Loads the server.properties file into memory.
        """
        self.logger.info(
            'Opening server properties file at %s',
            self.filename
        )
        try:
            with open(self.filename, 'r') as file:
                self.lines = file.readlines()
        except FileNotFoundError:
            self.logger.warning(
                'Server properties file (%s) does not exist, creating from scratch...',
                self.filename
            )
            self.lines = []
        except PermissionError:
            self.logger.error('Error: We were not able to access %s, check file permissions or '
                              'escalate your privileges as necessary.', self.filename)

    def set_property(self, name, value):
        """
        | Updates a property in the file contents if it has changed.
        | :param name:
        | :param value:
        """
        rex = re.compile(r'^%s\s*=' % name)
        changed = False
        for index in range(len(self.lines)):
            line = self.lines[index]
            if rex.match(line):
                self.lines[index] = '%s = %s\n' % (name, value)
                self.logger.info('Server property %s updated to %s', name, value)
                changed = True
        if not changed:
            self.lines.append('%s = %s\n' % (name, value))

    def update_properties(self):
        """
        | Checks properties dictionary and feeds them to set_property()
        | :return: `boolean` True or false based on success.
        """

        for prop, value in self.properties.items():
            self.set_property(prop, value)

    def write(self):
        """
        | Saves the updated file contents to server.properties
        | :return: `void`
        """
        self.logger.info('Saving changes to %s', self.filename)
        try:
            with open(self.filename, 'w') as file:
                file.write(''.join(self.lines))
        except FileNotFoundError:
            self.logger.error('Error: Server properties file (%s) does not exist.', self.filename)
        except PermissionError:
            self.logger.error('Error: We were not able to access %s, check file permissions '
                              'or escalate your privileges as necessary.', self.filename)


class MOTDGenerator:
    """
    | An MOTD Generator.
    """
    def __init__(self):
        self.motd = False
        if os.environ.get('MOTD'):
            self.motd = str(os.environ.get('MOTD'))

    def generate(self):
        """
        | Check for the MOTD property and return, else auto-generate and return.
        | :return: `string` Message of the day.
        """

        if self.motd:
            return self.motd

        game_type = os.environ.get('PACK_NAME', os.environ.get('GAME_TYPE'.lower(), 'modded'))
        version = os.environ.get('VERSION', 'Unknown Minecraft Version')
        creator = os.environ.get('PACK_CREATOR', 'Routh.IO')
        host = os.environ.get('GAME_HOST', 'Routh.IO')

        return 'A %s %s Minecraft server by %s. Hosted by %s' % (game_type, version, creator, host)


class PackFileUpdater:
    """
    | Updates files in from a pack distribution to a server volume.
    """
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest
        self.logger = logging.getLogger('mine-init')

    def sync(self):
        """
        | Sync the /dist/pack/server directory with the /server directory.
        | :return: `boolean` This always returns true, for now.
        """
        try:
            logpipe = LogPipe()
            with subprocess.Popen(
                    'rm -rf '
                    'mods '
                    'scripts '
                    'libraries '
                    'forge*.jar '
                    'minecraft*.jar',
                    cwd=self.dest,
                    shell=True,
                    encoding="utf-8",
                    stdout=logpipe.fileno(),
                    stderr=logpipe.fileno(),
                    executable='/bin/bash'
                ) as result:
                result.wait()
                logpipe.close()
        except FileNotFoundError as not_found_error:
            self.logger.error(
                'Error accessing %s directory',
                not_found_error.filename
            )

        self.logger.info(
            'Syncing %s to %s',
            os.path.join(self.source, 'server/'),
            os.path.join(self.dest)
        )
        try:
            logpipe = LogPipe()
            with subprocess.Popen(
                    'rsync -av --ignore-existing %s %s'
                    % (
                        os.path.join(self.source, 'server/'),
                        os.path.join(self.dest)
                    ),
                    shell=True,
                    encoding="utf-8",
                    stdout=logpipe.fileno(),
                    stderr=logpipe.fileno(),
                    executable='/bin/bash'
                ) as result:
                result.wait()
                logpipe.close()
        except FileNotFoundError as not_found_error:
            self.logger.error(
                'Error accessing %s directory',
                not_found_error.filename
            )

        if os.path.exists(os.path.join(self.source, 'server/config/')):
            self.logger.info(
                'Syncing %s to %s',
                os.path.join(self.source, 'server/config/'),
                os.path.join(self.dest, 'config/')
            )
            try:
                logpipe = LogPipe()
                with subprocess.Popen(
                        'rsync -av %s %s'
                        % (
                            os.path.join(self.source, 'server/config/'),
                            os.path.join(self.dest, 'config/')
                        ),
                        shell=True,
                        encoding="utf-8",
                        stdout=logpipe.fileno(),
                        stderr=logpipe.fileno(),
                        executable='/bin/bash'
                    ) as result:
                    result.wait()
                result.wait()
                logpipe.close()
            except FileNotFoundError as not_found_error:
                self.logger.error(
                    'Error accessing %s directory',
                    not_found_error.filename
                )

        return True


class PackManager:
    """
    | Manages a Packmaker installation.
    """
    def __init__(self, build_dir, cache_dir):
        self.build_dir = build_dir
        self.cache_dir = cache_dir
        self.logger = logging.getLogger('mine-init')

    def install_pack(self):
        """
        | Spawns a subprocess to preinstall the Packmaker pack.
        |
        | :return: `boolean` True or False based on success.
        """
        try:
            logpipe = LogPipe()
            with subprocess.Popen(
                    'packmaker build-server '
                    '--cache-dir %s %s' % (self.cache_dir, ' '.join(self.build_dir)),
                    shell=True,
                    encoding="utf-8",
                    cwd=self.build_dir[0],
                    stdout=logpipe.fileno(),
                    stderr=logpipe.fileno(),
                    executable='/bin/bash'
                ) as result:
                result.wait()
                logpipe.close()
        except ModuleNotFoundError as pm_error:
            self.logger.error(
                'Packmaker has failed to declare one of it\'s dependencies. Please open a bug. '
                'See stack trace: \n\n %s',
                pm_error
            )
            return False
        return True


class JavaRunner:
    """
    | Launches the Minecraft server
    """
    def __init__(self, server_dir, pack_dir):
        self.server_dir = server_dir
        self.pack_dir = pack_dir
        self.logger = logging.getLogger('mine-init')
        self.pack_data = self.get_pack_data()
        self.logpipe = LogPipe()
        self.server = self.start_jvm()

    def get_pack_data(self):
        """
        | Gets the packs info from packmaker and returns it as a dict.
        | :return: `dict` Packmaker pack data
        """
        try:
            with subprocess.Popen(
                    'packmaker info -f yaml',
                    stdout=subprocess.PIPE,
                    shell=True,
                    encoding="utf-8",
                    cwd=self.pack_dir,
                    executable='/bin/bash'
                ) as result:
                result.wait()
                return yaml.load(result.stdout, Loader=yaml.FullLoader)
        except FileNotFoundError as not_found_error:
            self.logger.error(
                'Error accessing %s',
                not_found_error.filename
            )

    def signal_handler(self, _signal, _frame):
        """
        | document me please.
        """
        self.logger.warning('SIGINT Recieved, stopping children.')
        self.logger.info('Asking Minecraft to stop.')
        try:
            self.server.communicate(input='/stop', timeout=120)
            self.logpipe.close()
        except subprocess.TimeoutExpired:
            self.logger.critical(
                'Server is not stopping gracefully, we\'ve waited 2 minutes. Killing with fire...'
            )
            self.server.kill()
            self.server.communicate()
            self.logpipe.close()
        sys.exit(0)

    def start_jvm(self):
        """
        | Starts the minecraft server.
        | :return: Minecraft server process.

        """
        jvm_command = [
            'java',
            '-Xmx%s' % JAVA_PARAMS.get('memory'),
            '-Xms%s' % JAVA_PARAMS.get('memory'),
            '-XX:+UseG1GC',
            '-Dsun.rmi.dgc.server.gcInterval=2147483646',
            '-XX:+UnlockExperimentalVMOptions',
            '-XX:G1NewSizePercent=20',
            '-XX:G1ReservePercent=20',
            '-XX:MaxGCPauseMillis=50',
            '-XX:G1HeapRegionSize=32M',
            '-Dfml.queryResult=%s' % JAVA_PARAMS.get('fml_confirm'),
            '-jar',
            self.pack_data.get('forge_jarfile'),
            'nogui'
        ]

        self.logger.info('Launching Minecraft JVM with command: %s', ' '.join(jvm_command))

        return subprocess.Popen(
            ' '.join(jvm_command),
            stdout=self.logpipe.fileno(),
            stderr=self.logpipe.fileno(),
            stdin=subprocess.PIPE,
            shell=True,
            encoding="utf-8",
            cwd=self.server_dir,
            executable='/bin/bash'
        )

    def main(self):
        """
        | document me please.
        """
        signal.signal(signal.SIGINT, self.signal_handler)
        self.logger.info('Press Ctrl+C to exit')
        signal.pause()
