"""
Command module allows executing ad hoc commands
"""
import os
import signal
import subprocess

class Command:
    def __init__(self, command_builder, *args, long_running=False, timeout=None, **kwargs):
        self.command_builder = command_builder
        self.long_running = long_running
        self.timeout = timeout
        self.args = args
        self.kwargs = kwargs
    
    def build_command(self, submission):
        return self.command_builder(submission, *self.args, **self.kwargs)

    def run(self, submission):
        command_str = self.build_command(submission)
        self.proc = subprocess.Popen(command_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
        shell=True, preexec_fn=os.setsid)
        out, err = None, None
        self.status = 'RUNNING'
        if not self.long_running:
            out, err = self.proc.communicate(timeout=self.timeout)
            self.status = 'FINISHED'
        return self.proc, out, err

    def kill(self):
        os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        out, errs = self.proc.communicate()
        return out, errs