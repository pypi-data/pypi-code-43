from typing import Union, List
from os import path
from quixote.build.utils import setup_function
from quixote.build import GeneratorType
from quixote import get_context
from shlex import quote


@setup_function
def command(cmd: str, env={}) -> str:
    """
    Execute a shell command

    :param cmd:                 the command to execute
    :param env:                 the additional environment to use for this command execution
    """
    env = ' '.join(name + "=" + quote(value) for name, value in env.items())
    if get_context()["generator"] == GeneratorType.DOCKER:
        return f"RUN {env} {cmd}"
    else:
        return f"{env} {cmd}"


@setup_function
def set_env(**kwargs) -> str:
    """
    Set environment variables

    :param kwargs:              a dictionary with variable names as keys and their values as values
    """
    to_set = ' '.join(name + "=" + quote(value) for name, value in kwargs.items())
    if get_context()["generator"] == GeneratorType.DOCKER:
        return f"ENV {to_set}"
    else:
        return f"export {to_set}"


@setup_function
def change_work_directory(path: str) -> str:
    """
    Change the current working directory

    :param path:                the path to the new working directory
    """
    if get_context()["generator"] == GeneratorType.DOCKER:
        return f"WORKDIR {path}"
    else:
        return f"cd {path}"


def add_user(username: str, home_dir=None, groups=None, create_home_dir=False, shell=None) -> str:
    """
    Create a user

    :param username:            the username of the new user
    :param home_dir:            the path to the directory to use as home directory for the new user
    :param groups:              the groups to which the new user should be added
    :param create_home_dir:     True if a home directory should be created for the user (if it does not exist)
    :param shell:               the path to the executable to set as shell for the new user
    """
    cmd = "useradd " + username
    if home_dir is not None:
        cmd += " --home-dir " + home_dir
    if groups is not None:
        cmd += " --groups " + ','.join(groups)
    if create_home_dir is True:
        cmd += " --create-home"
    if shell is not None:
        cmd += " --shell " + shell
    return command(cmd)


def change_user_passwd(username: str, new_password: str) -> str:
    """
    Change the password for a given user

    :param username:            the username of the user
    :param new_password:        the new password
    """
    cmd = f"echo {username}:{new_password} | chpasswd"
    return command(cmd)


def _dirname(p: str):
    if p[-1] == '/':
        return path.dirname(path.dirname(p))
    return path.dirname(p)


@setup_function
def add_file(src: Union[str, List[str]], dest: str):
    """
    Add some files to the setup

    :param src: a single or list of files to add
    :param dest: the path at which to put the files (must be a directory if multiples files are provided in src)
    """
    resources_path = get_context()["resources_path"]
    if type(src) is str:
        src = path.realpath(src)
        if path.commonprefix([src, resources_path]) != resources_path:
            raise PermissionError(f"Source file should be in {resources_path}")
        src = path.relpath(src, _dirname(resources_path))
        if get_context()["generator"] == GeneratorType.DOCKER:
            return f"COPY {src} {dest}"
        else:
            return f"cp -r {src} {dest}"
    else:
        src = list(map(path.realpath, src))
        if path.commonprefix(src + [resources_path]) != resources_path:
            raise PermissionError(f"Source files should be in {resources_path}")
        src = map(lambda p: path.relpath(p, _dirname(resources_path)), src)
        if get_context()["generator"] == GeneratorType.DOCKER:
            return f"COPY {' '.join(src)} {dest}"
        else:
            return f"cp -rt {dest} {' '.join(src)}"
