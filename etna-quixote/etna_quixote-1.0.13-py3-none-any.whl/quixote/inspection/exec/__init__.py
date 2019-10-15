import shlex
from typing import List, Mapping, Union
import quixote.inspection as inspection


def command(
        cmd: Union[str, List[str]],
        timeout: int = None,
        env: Mapping[str, str] = None
) -> inspection.CompletedProcess:
    """
    Run a single executable. It is not run in a shell.

    :param cmd:         command to be executed
    :param timeout:     the timeout in seconds. If it expires, the child process will be killed and waited for. Then subprocess.TimeoutExpired exception will be raised after the child process has terminated
    :param env:         the environment to use when running the command
    :raise quixote.inspection.TimeoutError: if timeout is not None and expires before the child process terminates
    """
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    return inspection._run(cmd, capture_output=True, shell=False, timeout=timeout, env=env)


def bash(
        cmd: str,
        timeout: int = None,
        force_kill_on_timeout: bool = False,
        env: Mapping[str, str] = None
) -> inspection.CompletedProcess:
    """
    Run one or a sequence of commands using the Bash shell.

    :param cmd:                     commands to be executed
    :param timeout:                 the timeout in seconds. If it expires, the child process will be killed and waited for. Then subprocess.TimeoutExpired exception will be raised after the child process has terminated
    :param force_kill_on_timeout:   whether processes should be terminated or killed
    :param env:                     the environment to use when running the command
    :raise quixote.inspection.TimeoutError: if timeout is not None and expires before the child process terminates
    """
    if timeout is not None:
        return inspection._run_with_new_session(cmd, timeout, force_kill_on_timout=force_kill_on_timeout, env=env)
    else:
        return inspection._run(["bash", "-c", cmd], capture_output=True, shell=False, env=env)


def java(
        class_name: str,
        args: List[str] = [],
        timeout: int = None,
        options: List[str] = None,
        env: Mapping[str, str] = None
) -> inspection.CompletedProcess:
    """
    Launch a java class

    :param class_name:                  path of the Java class file to launch
    :param args:                        list of arguments to pass to the launched class
    :param timeout:                     time to wait before terminating the process
    :param options:                     list of shell options to be passed to java (see java man page for more info)
    :param env:                         environment to run the java command (by default use the current shell environment)
  
    :raise quixote.inspection.TimeoutError: if timeout is not None and expires before the child process terminates
    """
    options = options or []
    cmd = "java"
    return inspection._run([cmd, *options, class_name, *args], capture_output=True, timeout=timeout, env=env)


def javajar(
        jar_path: str,
        args: List[str] = [],
        timeout: int = None,
        options: List[str] = None,
        env: Mapping[str, str] = None
) -> inspection.CompletedProcess:
    """
    Launch a java archive

    :param jar_path:            path of the Java archive to launch
    :param args:                list of arguments to pass to the launched archive
    :param timeout:             time to wait before terminating the process
    :param options:             list of shell options to be passed to java (see java man page for more info)
    :param env:                 environment to run the java command (by default use the current shell environnment)

    :raise quixote.inspection.TimeoutError: if timeout is not None and expires before the child process terminates
    """
    options = options or []
    cmd = "java"
    return inspection._run([cmd, *options, "-jar", jar_path, *args], capture_output=True, timeout=timeout, env=env)
