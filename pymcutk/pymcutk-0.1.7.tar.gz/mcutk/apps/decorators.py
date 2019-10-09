from __future__ import print_function
import os
import glob
import logging
import shlex
import subprocess

from mcutk.util import run_command
from mcutk.exceptions import ProcessTimeout, InstallError
from mcutk.apps.idebase import Result, DEFAULT_MCUTK_WORKSPACE



def build(func):
    """This function is Decorator and it a will start a new process to exectue the commands which
    comes from APP.build_project. When the process finished, it will return the build results.

    Default timeout: 1800 seconds

    Returns:
        mcutk.apps.BuildResult object.

    Notice:
        For new IDE support, you'd better to add this decorator on the function APP.build_project.
    """
    def wraper(*args, **kwargs):
        output = None
        timeout = kwargs.pop('timeout') if 'timeout' in kwargs else 1800
        _toolchain, _project, _target, _logile = args

        if not kwargs.get('workspace'):
            kwargs['workspace'] = DEFAULT_MCUTK_WORKSPACE + "/" + _toolchain.name

        cmdline = func(*args, **kwargs)

        # shell=True: this can resolve windows backslash
        returncode = run_command(cmdline, shell=True, stdout=False, timeout=timeout, need_raise=True)[0]
        br = _toolchain.parse_build_result(returncode, _logile)

        output = _project.targetsinfo.get(_target)
        br.set_output(output)

        # errors
        if br.result not in (Result.Pass, Result.Warnings):
            return br

        workspace = kwargs.get('workspace')

        # For eclipse projects, output is located in workspace
        if _toolchain.name in ("mcux") and workspace:
            output_abs = os.path.join(workspace, output)
        else:
            # Assume output file is located project root
            output_abs = os.path.join(_project.prjdir, output)

        # File exists, return diectly
        if os.path.isfile(output_abs):
            br.set_output(output_abs)
            return br

        if not os.path.exists(output_abs):
            logging.warning("output is not exists: [%s]", output_abs)
            return br


        # Find files in output diectory
        valid_extension= ('.axf', '.elf', '.out', '.hex', '.bin', '.lib', '.a')
        for ext in valid_extension:
            try:
                file_path = glob.glob(output_abs + "/*"+ ext)[0]
                br.set_output(file_path)
                break
            except IndexError:
                pass
        else:
            logging.warning("unable to find output: [%s]", output_abs)

        return br

    return wraper








def appinstall(func):
    """Decorator for app installation
        1. Pre change file mode: 0777.
        2. Post check the path
    """
    def wraper(*args, **kwargs):
        installer = args[0]
        logging.info("Prepare to install: %s"%installer)
        os.chmod(installer, 0o777)
        path, version = func(*args, **kwargs)
        if not path or not os.path.exists(path):
            logging.error("Return path is not exists: %s", str(path))
            raise InstallError("Failed to install app!")
        return path, version

    return wraper


