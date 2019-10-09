from __future__ import print_function
import os
import sys
import signal
import re
import stat
import shutil
import shlex
import logging
import subprocess
from threading import Timer
import threading

from mcutk.exceptions import ProcessTimeout

PY = sys.version_info[0]

"""
This module provide some useful functions.
"""

def _readerthread(fh, buffer):
    while True:
        stdoutdata = fh.readline()
        if stdoutdata:
            sys.stdout.write(stdoutdata)
            sys.stdout.flush()
            buffer.append(stdoutdata)
        else:
            break


def run_command(cmd, cwd=None, shell=True, stdout=False, timeout=30, need_raise=False):
    """Run a command with a timeout timer and capture it's console output.

    This method wrapped subprocess.Popen, when you need to capture console output, just make
    sure **stdout** is True.

    Arguments:
        cmd -- {str or list} command string or list, like subprocess
        cwd -- {str} process work directory.
        shell -- {boolean} Use shell or not.
        stdout -- {boolean} Capture stdout and print it in real time, default: False.
        timeout -- {int} timeout seconds, default: 30(s)
        need_raise -- {boolean} a switch to disable raising ProcessTimeout exception,
                    just logging it as an error message, default: False.

    Returns:
        Tuple -- (returncode, output)
    """
    output = ""
    returncode, timer, error_message = None, None, None
    timer_result = {"is_timeout": False}

    logging.debug(cmd)

    if shell:
        # python documentation:
        # On Windows, The shell argument (which defaults to False) specifies whether to use the shell as the program to execute.
        # If shell is True, it is recommended to pass args as a string rather than as a sequence.
        if isinstance(cmd, list):
            cmd = " ".join(cmd)
    else:
        # Windows platform, convert cmd to list to will lead out the slash issue.
        if os.name == 'nt':
            if not isinstance(cmd, list):
                cmd = shlex.split(cmd)

    kwargs = {
        "stdout": subprocess.PIPE if stdout else None,
        "stderr": subprocess.STDOUT,
        "cwd": cwd,
        "shell": shell
    }

    if PY > 2:
        kwargs['encoding'] = 'utf8'

    try:
        process = subprocess.Popen(cmd, **kwargs)

        # start timer
        timer = Timer(timeout, _timeout_trigger, args=(process, timer_result, ))
        timer.start()

        if stdout:
            output = []
            stdout_thread = threading.Thread(target=_readerthread,
                args=(process.stdout, output))
            stdout_thread.setDaemon(True)
            stdout_thread.start()

            process.wait()
            stdout_thread.join()
            output = ''.join(output)
        else:
            output, error = process.communicate()

        returncode = process.returncode

        if returncode != 0:
            error_message = 'Error: {0}\n  exit code:  {1}\n'.format(cmd, process.pid)
            if output:
                error_message + '  console output: %s'%(output)
            logging.debug(error_message)

    except OSError as emsg:
        logging.exception(emsg)

    finally:
        if timer:
            timer.cancel()

        if timer_result['is_timeout']:
            msg = "process(pid %s) operation timeout"%process.pid
            if need_raise:
                raise ProcessTimeout(msg)
            else:
                logging.error(msg)

    return returncode, output



def _timeout_trigger(pro, result):
    """Timeout will kill the group processes.

    [Timeout will kill the group processes]

    Arguments:
        pro {Popen object} -- process
    """

    if os.name == "nt":
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=pro.pid))
    else:
        pro.kill()

    if isinstance(result, dict):
        result['is_timeout'] = True







def rmtree(path):
    """Remove directory tree. If failed , it will check the access and force
    to close unclosed handler, then try remove agagin.
    """
    try:
        shutil.rmtree(path)
    except Exception:
        # Is the error an access error ?
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)

        # Readonly on windows
        if os.name == "nt":
            subprocess.check_call(('attrib -R ' + path + '\\* /S').split())

        shutil.rmtree(path)




def onerrorHandler(func, path, exc_info):
    """Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)


def copydir(root_src_dir, root_dst_dir):
    """Copy directory to dst dir."""
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = os.path.normpath(src_dir.replace(root_src_dir, root_dst_dir, 1))
        print("copying %s"%dst_dir)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.normpath(os.path.join(src_dir, file_))
            dst_file = os.path.normpath(os.path.join(dst_dir, file_))
            if os.path.exists(dst_file):
                os.chmod(dst_file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # 0777
                os.remove(dst_file)
            shutil.copy(src_file, dst_file)


def change_folder_security_win(path):
    """
    Change folder security.
    Add full control for current login user.

    param path: the folder path.
    return bool, command exited code == 0, or not.


    https://stackoverflow.com/questions/2928738/how-to-grant-permission-to-users-for-a-directory-using-command-line-in-windows

    According do MS documentation:

    F = Full Control
    CI = Container Inherit - This flag indicates that subordinate containers will inherit this ACE.
    OI = Object Inherit - This flag indicates that subordinate files will inherit the ACE.
    /T = Apply recursively to existing files and sub-folders. (OI and CI only apply to new files and
    sub-folders). Credit: comment by @AlexSpence.
    For complete documentation, you may run "icacls" with no arguments or see the Microsoft documentation.

    """
    assert os.name == "nt"
    login_username = os.environ.get("USERNAME")
    path = os.path.normpath(path)
    return os.system('''icacls {0} /grant {1}:(OI)(CI)F /T'''.format(path, login_username))==0


