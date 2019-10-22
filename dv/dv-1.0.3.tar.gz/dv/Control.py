import subprocess

import re
from subprocess import PIPE, STDOUT
import platform


class Control:
    IGNORED_ERRORS = ['ERROR on GET_CHILDREN: Node has no children.']

    def __init__(self, address='localhost', port=4040):
        if (platform.system().find("MINGW") != -1) or (platform.system() == "Windows"):
            control_name = "dv-control.exe"
        else:
            control_name = "dv-control"
        self._control = subprocess.Popen([control_name, '-i', address, '-p', str(port)], stdin=PIPE, stdout=PIPE, stderr=STDOUT, bufsize=-1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def _communicate(self, command):
        enc_command = command.encode('utf-8')
        self._control.stdin.write(enc_command)
        self._control.stdin.flush()
        ret_val = self._control.stdout.readline().decode('utf8').strip().rstrip()
        if ret_val.lower().startswith('error'):
            if ret_val in self.IGNORED_ERRORS:
                return ''
            else:
                raise RuntimeError('Command "%s" failed with "%s"' % (enc_command, ret_val))
        return ret_val

    def put(self, path, parameter, value_type, value):
        if value_type == 'bool':
            value = str(value).lower()
        self._communicate('put %s %s %s %s\n' % (path, parameter, value_type, str(value)))

    def get(self, path, parameter, value_type):
        output = self._communicate('get %s %s %s\n' % (path, parameter, value_type))
        match = re.match(r'^GET: ?(.*)$', output)
        if not match:
            raise ValueError("Could not extract value from output value %s" % output)
        value_str = match.group(1)
        vt = value_type.lower()
        if vt == 'int' or vt == 'long':
            return int(value_str)
        elif vt == 'float' or vt == 'double':
            return float(value_str)
        elif vt == 'bool':
            return value_str == 'true'
        return value_str

    def add_module(self, module_name, module_library):
        self._communicate('add_module %s %s\n' % (module_name, module_library))

    def remove_module(self, module_name):
        self._communicate('remove_module %s\n' % module_name)

    def node_exists(self, path):
        output = self._communicate('node_exists %s\n' % path)
        match = re.match(r'^NODE_EXISTS: (.*)$', output)
        if not match:
            raise ValueError("Could not extract value from output value %s" % output)
        return match.group(1) == 'true'

    def attribute_exists(self, path, parameter, value_type):
        output = self._communicate('attr_exists %s %s %s\n' % (path, parameter, value_type))
        match = re.match(r'^ATTR_EXISTS: (.*)$', output)
        if not match:
            raise ValueError("Could not extract value from output value %s" % output)
        return match.group(1) == 'true'

    def get_children(self, path):
        output = self._communicate('get_children %s\n' % path)
        return output.strip().split('|')

    def close(self):
        self._control.terminate()
