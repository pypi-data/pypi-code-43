import subprocess
from .error import ErrorProcess


class MethodsProcess(object):
    def __init__(self):
        self.pro = subprocess

    def start_command(self, command, shell):
        try:
            return self.pro.call(command, shell=shell)
        except ErrorProcess("Process error") as exc:
            raise exc

    def exec_bash(self, process, shell, *args):
        try:
            result = self.pro.Popen(process, shell=shell, stdin=self.pro.PIPE, stdout=self.pro.PIPE)

            for command in args:
                self._insert_command(result, command)

            stdIn, stdOut = result.communicate()
            return stdIn.decode("utf-8")
        except stdOut as exc:
            raise exc    


    def _insert_command(self, process, command):
        return process.stdin.write(command.encode())