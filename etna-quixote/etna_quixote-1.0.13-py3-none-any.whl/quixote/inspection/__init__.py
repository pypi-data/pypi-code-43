from typing import Any, Dict, List, Union, Type, Optional, Mapping
from textwrap import dedent
from contextlib import contextmanager
import os
import signal
import subprocess

_inspection_result = {"requirements": [], "assertion_failure": None, "points": 0}


def _reset_inspection_result():
    global _inspection_result
    _inspection_result = {"requirements": [], "assertion_failure": None, "points": 0}


def get_inspection_result() -> Dict[str, Any]:
    """
    Retrieve the current inspection result

    :return:                        a dictionary describing the current inspection result
    """
    return _inspection_result


@contextmanager
def new_inspection_result(**kwargs: Any) -> Dict[str, Any]:
    """
    Create a new inspection result for the duration of a with-block

    :param kwargs:                  entries to initialize the inspection result with
    :return:                        the inspection result
    """
    try:
        global _inspection_result
        _inspection_result = {**_inspection_result, **kwargs}
        yield get_inspection_result()
    finally:
        _reset_inspection_result()


class KOError(Exception):
    """
    Exception class representing a step failure caused by the student
    """
    pass


class InternalError(Exception):
    """
    Exception class representing a step failure caused by an internal error
    """
    pass


class TimeoutError(Exception):
    """
    Exception class representing an error related to a timeout when executing a process
    """

    def __init__(self, cause: Exception):
        self.__cause__ = cause

    def __str__(self):
        cmd = self.__cause__.cmd if isinstance(self.__cause__.cmd, str) else " ".join(self.__cause__.cmd)
        return dedent(f"""
        process '{cmd}' did not terminate before a timeout of {self.__cause__.timeout} seconds expired
        stdout: {self.__cause__.output}
        stderr: {self.__cause__.stderr}
        """)


class CompletedProcess:
    """
    Class representing a completed process, and providing access to its arguments, its output, and its return code
    """

    def __init__(self, completed_subprocess: subprocess.CompletedProcess):
        self.args: Union[str, List[str]] = completed_subprocess.args
        self.raw_stdout: bytes = completed_subprocess.stdout
        self.raw_stderr: bytes = completed_subprocess.stderr
        self._stdout: Optional[str] = None
        self._stderr: Optional[str] = None
        self.return_code: int = completed_subprocess.returncode

    def __bool__(self):
        return self.return_code == 0

    def __repr__(self):
        return f"CompletedProcess(\n" + \
               ",\n".join(f"    {name}={value!r}" for name, value in self.__dict__.items()) + \
               "\n)"

    @staticmethod
    def _decode_output(raw_output: bytes, encoding: str = "utf-8"):
        if raw_output is not None:
            return raw_output.decode(encoding)
        return None

    def check_decode(self, message: str, *, error_kind: Type = KOError, encoding: str = "utf-8"):
        """
        Check whether the output of the process can be decoded according to a given encoding

        :param message:         message in case of failure to explain the reason of said failure
        :param error_kind:      exception to raise if the check failed
        :param encoding:        encoding to use to decode the data
        """
        try:
            self._stdout = self._decode_output(self.raw_stdout, encoding)
        except UnicodeDecodeError as e:
            raise error_kind(f"{message}: {str(e)} (while decoding stdout)")
        try:
            self._stderr = self._decode_output(self.raw_stderr, encoding)
        except UnicodeDecodeError as e:
            raise error_kind(f"{message}: {str(e)} (while decoding stderr)")
        return self

    @property
    def stdout(self) -> str:
        if self._stdout is None:
            self._stdout = self._decode_output(self.raw_stdout)
        return self._stdout

    @property
    def stderr(self) -> str:
        if self._stderr is None:
            self._stderr = self._decode_output(self.raw_stderr)
        return self._stderr

    def check(
            self,
            message: str,
            error_kind: Type = KOError,
            allowed_status: Union[int, List[int]] = 0,
            stdout: bool = True,
            stderr: bool = True
    ):
        """
        Check whether the execution of the process failed

        :param message:         message in case of failure to explain the reason of said failure
        :param allowed_status:  status or list of statuses that are considered successful
        :param error_kind:      exception to raise if the check failed
        :param stdout:          if True add the output of the process as a detail for the exception
        :param stderr:          if True add the error output of the process to the exception message
        """
        if isinstance(allowed_status, int):
            allowed_status = [allowed_status]
        if self.return_code not in allowed_status:
            message += f"\nexit code: {self.return_code}"
            if stdout:
                if self.raw_stdout is not None:
                    try:
                        message += "\nstdout:\n" + self.stdout
                    except UnicodeDecodeError:
                        message += "\nstdout (raw bytes):\n" + repr(self.raw_stdout)
                else:
                    message += "\nstdout is empty"
            if stderr:
                if self.raw_stderr is not None:
                    try:
                        message += "\nstderr:\n" + self.stderr
                    except UnicodeDecodeError:
                        message += "\nstderr (raw bytes):\n" + repr(self.raw_stderr)
                else:
                    message += "\nstderr is empty"
            raise error_kind(message)
        return self

    def expect(
            self,
            message: str,
            allowed_status: Union[int, List[int]] = 0,
            nb_points: int = 1,
            stdout: bool = True,
            stderr: bool = True
    ):
        """
        Check whether the execution of the process failed

        :param message:         message in case of failure to explain the reason of said failure
        :param allowed_status:  status or list of statuses that are considered successful
        :param nb_points:       the number of points granted by the expectation if it passes
        :param stdout:          if True add the output of the process as a detail for the exception
        :param stderr:          if True add the error output of the process to the exception message
        """
        if isinstance(allowed_status, int):
            allowed_status = [allowed_status]
        message += f"\nexit code: {self.return_code}"
        if stdout:
            message += ("\nstdout:\n" + self.stdout) if self.stdout is not None else "\nstdout is empty"
        if stderr:
            message += ("\nstderr:\n" + self.stderr) if self.stderr is not None else "\nstderr is empty"
        get_inspection_result()["requirements"].append((self.return_code in allowed_status, message, nb_points))
        return self


def _run(*args, **kwargs) -> CompletedProcess:
    """
    Run a subprocess

    This is a wrapper for subprocess.run() and all the arguments are forwarded to it
    See the documentation of subprocess.run() for the list of all the possible arguments
    :raise quixote.inspection.TimeoutError: if the timeout argument is not None and expires before the child process terminates
    """
    try:
        return CompletedProcess(subprocess.run(*args, **kwargs))
    except subprocess.TimeoutExpired as e:
        raise TimeoutError(e)


def _run_with_new_session(
        cmd: str, timeout: int = None,
        force_kill_on_timout: bool = False,
        env: Mapping[str, str] = None
):
    proc = subprocess.Popen(
        ["bash", "-c", cmd],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        start_new_session=True,
        env=env
    )
    try:
        out, err = proc.communicate(timeout=timeout)
        return CompletedProcess(subprocess.CompletedProcess(proc.args, proc.returncode, out, err))
    except subprocess.TimeoutExpired as e:
        os.killpg(proc.pid, signal.SIGTERM)
        if force_kill_on_timout:
            os.killpg(proc.pid, signal.SIGKILL)  # Kill again, harder (in case some processes don't exit gracefully)
        proc.communicate()
        raise TimeoutError(e)
