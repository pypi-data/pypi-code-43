import subprocess

from subprocess import PIPE
import platform


class Control:
    def __init__(self, address='localhost', port=4040):
        if (platform.system().find("MINGW") != -1) or (platform.system() == "Windows"):
            self._control_name = "dv-control.exe"
        else:
            self._control_name = "dv-control"

        self._address = address
        self._port = str(port)

    def _communicate(self, command):
        proc = subprocess.Popen([self._control_name, '-i', self._address, '-p', self._port, '-s'] + command.split(' '), stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        error = stderr.decode('utf-8').strip() if stderr is not None else ''
        out = stdout.decode('utf-8').strip() if stdout is not None else ''
        exit_code = proc.returncode

        if exit_code != 0:
            raise RuntimeError('Could not perform action. exit code %d' % exit_code)

        if error.lower().startswith('error'):
            raise RuntimeError('Command "%s" failed with "%s"' % (command, error))
        return out

    def put(self, path, parameter, value_type, value):
        if value_type == 'bool':
            value = str(value).lower()
        self._communicate('put %s %s %s %s' % (path, parameter, value_type, str(value)))

    def set(self, path, parameter, value_type, value):
        self.put(path, parameter, value_type, value)

    def get(self, path, parameter, value_type):
        output = self._communicate('get %s %s %s' % (path, parameter, value_type))
        vt = value_type.lower()
        if vt == 'int' or vt == 'long':
            return int(output)
        elif vt == 'float' or vt == 'double':
            return float(output)
        elif vt == 'bool':
            return output == 'true'
        return output

    def add_module(self, module_name, module_library):
        self._communicate('add_module %s %s' % (module_name, module_library))

    def remove_module(self, module_name):
        self._communicate('remove_module %s' % module_name)

    def node_exists(self, path):
        output = self._communicate('node_exists %s' % path)
        return output == 'true'

    def attribute_exists(self, path, parameter, value_type):
        output = self._communicate('attr_exists %s %s %s' % (path, parameter, value_type))
        return output == 'true'

    def get_children(self, path):
        output = self._communicate('get_children %s' % path)
        return [] if output == '' else output.strip().split('|')
