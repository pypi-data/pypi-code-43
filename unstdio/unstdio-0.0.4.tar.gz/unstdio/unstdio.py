import io
import sys
from .tee import Tee
import threading
from unstdio.handlers import Inp, Out, Err


class Environment(object):
    def __init__(
        self,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    ):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr


class Unstdio(object):
    rlock = threading.RLock()

    def __init__(
        self, stdin=None, stdout=None, stderr=None
    ):

        if stdin is None:
            self.stdin = Inp()
        else:
            self.stdin = stdin
        if stdout is None:
            self.stdout = Out()
        else:
            self.stdout = stdout
        if stderr is None:
            self.stderr = Err()
        else:
            self.stderr = stderr
        self.old_stdin = sys.stdin
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

    def __enter__(self):
        if Unstdio.rlock.acquire():
            sys.stdin = self.stdin
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            return Environment(
                self.stdin, self.stdout, self.stderr
            )

    def __exit__(self, *args):
        sys.stdin = self.old_stdin
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        Unstdio.rlock.release()
