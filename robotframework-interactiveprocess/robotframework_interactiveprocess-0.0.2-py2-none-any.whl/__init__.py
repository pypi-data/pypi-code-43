from .methodsprocess import MethodsProcess


class InteractiveProcess(object):
    def __init__(self):
        self.start = MethodsProcess()

    def new_process(self, command, shell):
        return self.start.start_command(command, shell)

    def add_command(self, command, shell, *args):
        return self.start.exec_bash(command, shell, *args)
