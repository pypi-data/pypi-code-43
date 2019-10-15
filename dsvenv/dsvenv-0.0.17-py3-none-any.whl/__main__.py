from argparse import ArgumentParser
import glob
import os
import subprocess
import sys
import tempfile
import re
import warnings

from . import __version__


# specify the version of the pre-commit library to be used in pip install --upgrade
_pre_commit_version = 'pre-commit==1.*'
_dsbuild_version = '0.0.7'
_azure_yaml_file = 'azure.yml'

_python_version_regex = r'[ ]+python_version:.+([0-9]+)[.]([0-9]+)[.]([0-9]+)'
_dsvenv_version_regex = r'[ ]+dsvenv_version:.+([0-9]+)[.]([0-9]+)[.]([0-9]+)'

_VENV_BIN_SEARCH_DIRS = ['Scripts', 'bin']
_PRECOMMIT_EXECUTABLE = 'pre-commit'


def get_versions_from_azure_yaml():
    """
    Return Python and dsvenv version as defined by `azure.yml`.

    Parse the version of Python and dsvenv from the `azure.yml` file.
    If this file does not exist, the returned versions will be None.

    Returns:
        tuple(str or None, str or None):
            The version of python and the version of dsvenv.
    """
    azure_yaml_path = os.path.join(os.getcwd(), _azure_yaml_file)
    if not os.path.exists(azure_yaml_path):
        return None, None

    with open(azure_yaml_path) as fid:
        azure_yaml = fid.read()
    try:
        r = re.findall(_python_version_regex, azure_yaml)
        azure_python_version = '.'.join(r[0])
    except IndexError:
        azure_python_version = None
    try:
        r = re.findall(_dsvenv_version_regex, azure_yaml)
        azure_dsvenv_version = '.'.join(r[0])
    except IndexError:
        azure_dsvenv_version = None

    return azure_python_version, azure_dsvenv_version


def verify_environment(only_warning=True):
    """
    Perform a sanity check on the interpreter executing this script.

    Verify if the environment that is being used is based on the correct version of
    Python and `dsvenv`.

    Args:
        only_warning (bool):  Throw only a warning or a full error.
    """
    expected_python, expected_dsvenv = get_versions_from_azure_yaml()

    print('  Verifying environment...')

    this_python = '.'.join(
        [
            str(sys.version_info.major),
            str(sys.version_info.minor),
            str(sys.version_info.micro),
        ]
    )
    this_dsvenv = __version__

    if expected_python is not None and expected_python != this_python:
        msg = (
            f'The current python version ({this_python}) is not the same as the '
            f'version that was used during testing ({expected_python}).'
        )
        if only_warning:
            warnings.warn(msg)
        else:
            raise EnvironmentError(msg)

    if expected_dsvenv is not None and expected_dsvenv != this_dsvenv:
        msg = (
            f'The current dsvenv version ({this_dsvenv}) is not the same as '
            f'the version that was used during testing ({expected_dsvenv}).'
        )
        if only_warning:
            warnings.warn(msg)
        else:
            raise EnvironmentError(msg)


def get_venv_executable(venv_dir, executable, required=True):
    """
    Return the full path to an executable inside a given virtual environment.

    Args:
        venv_dir (str):  Path to the directory containing the virtual environment.
        executable (str):  Name of the executable.
        required (bool):  Whether to consider it a fatal error if the executable is not
                          found.

    Returns:
        str or None:  Full path to an executable inside the virtual environment. In case
                      it cannot be found, either an exception is raised or None is
                      returned, depending on whether the executable is required or not.

    Raises:
        FileNotFoundError:  When the executable is required and could not be found.

    # noqa: RST301
    """
    from distutils.spawn import find_executable

    search_path = [os.path.join(venv_dir, p) for p in _VENV_BIN_SEARCH_DIRS]
    venv_executable = find_executable(
        executable=executable, path=os.pathsep.join(search_path)
    )

    if required and not venv_executable:
        raise FileNotFoundError(
            f'The virtual environment executable could not be found'
        )

    return venv_executable


def get_venv_python(venv_dir, required=True):
    """
    Return the Python executable inside a given virtual environment.

    Args:
        venv_dir (str):  Path to the directory containing the virtual environment.
        required (bool):  Whether to consider it a fatal error if the executable is not
                          found.

    Returns:
        str or None:  Full path to the Python executable inside the virtual environment.
                      In case it cannot be found, either an exception is raised or None
                      is returned, depending on whether the executable is required or
                      not.

    Raises:
        FileNotFoundError:  When the executable is required and could not be found.
    """
    return get_venv_executable(
        venv_dir=venv_dir,
        executable=os.path.basename(sys.executable),
        required=required,
    )


def clear_venv(venv_dir):
    """
    Clear a virtual environment and restore it to a clean state.

    Note that this does not mean simply removing the entire folder, but rather
    uninstalls everything, leaving behind only those packages that are available in a
    fresh virtual environment (i.e., `pip` and `setuptools`).

    Args:
        venv_dir (str): Path to the directory containing the virtual environment.
    """
    vpython = get_venv_python(venv_dir, required=False)

    if not vpython:
        # Nothing to do.
        return

    # First get the list of all packages that should be uninstalled.
    reqs_file = tempfile.NamedTemporaryFile(delete=False, prefix='requirements.txt_')
    with reqs_file as fout:
        subprocess.check_call([vpython, '-m', 'pip', 'freeze'], stdout=fout)

    # Then actually remove them.
    subprocess.check_call(
        [vpython, '-m', 'pip', 'uninstall', '-r', reqs_file.name, '-y']
    )

    # Clean up.
    os.remove(reqs_file.name)


def ensure_venv(venv_dir, python_version='system'):
    """
    Ensure the presence of a virtual environment in a given directory.

    If it already exists, nothing will be done. If it does not exist, the environment
    will be created and it will be ensured that the available `pip` and `setuptools`
    packages are updated to the latest version.
    """
    if python_version != 'system':
        raise NotImplementedError('Only `system` Python version is supported.')

    if get_venv_python(venv_dir, required=False) is None:
        # Initialize the virtual environment.
        subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])

    vpython = get_venv_python(venv_dir)

    # Ensure recent versions of pip and setuptools.
    subprocess.check_call(
        [vpython, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools']
    )

    # Ensure correct version of dsbuild.
    subprocess.check_call([vpython, '-m', 'pip', 'install',
                           f'dsbuild=={_dsbuild_version}'])

    # verify the environment
    verify_environment()


def initialize_venv(venv_dir, reqs_file=None, extra_reqs=None):
    """
    Initialize a virtual environment.

    The environment is initialized using default Python version, based on a given
    requirements file.

    Args:
        venv_dir (str):  Path to a virtual environment.

        reqs_file (str or None):  Path to the requirements file to be installed.

        extra_reqs (None or list of str):  Paths to extra requirements files to be
                                           installed.

    Raises:
        ValueError:  If `reqs_file` or any of the files in `extra_reqs` does not exist.
    """
    if extra_reqs is None:
        extra_reqs = []
    reqs_files = ([reqs_file] if reqs_file is not None else []) + extra_reqs

    for f in reqs_files:
        if not os.path.exists(reqs_file):
            raise ValueError(f'Provided requirements file `{f}` does not exist.')

    # Ensure that at least a bare virtual environment exists.
    ensure_venv(venv_dir)

    # Install the main + extra requirements files.
    if reqs_files:
        cmd_args = [get_venv_python(venv_dir), '-m', 'pip', 'install']
        for f in reqs_files:
            cmd_args.extend(['-r', f])

        subprocess.check_call(cmd_args)


def install_pre_commit_hooks(venv_dir):
    # First install the `pre-commit` module in the virtual environment. If it is already
    # present, it will be upgraded the latest suitable version (today, this is `1.*`;
    # see the `_pre_commit_version` variable).
    try:
        subprocess.check_call(
            [
                get_venv_python(venv_dir),
                '-m',
                'pip',
                'install',
                '--upgrade',
                _pre_commit_version,
            ]
        )
    except FileNotFoundError as e:
        print(e)
        print('Make sure that at least a bare virtual environment is available!')
        sys.exit(1)

    # Then actually install the hooks.
    pre_commit_exec = get_venv_executable(
        venv_dir=venv_dir, executable=_PRECOMMIT_EXECUTABLE
    )
    subprocess.check_call([pre_commit_exec, 'install'])


def get_default_reqs_file():
    """
    Return the path to the default requirements file, if it exists. If not, return None.
    """
    reqs_file = os.path.join(os.getcwd(), 'requirements.txt')
    if not os.path.exists(reqs_file):
        reqs_file = None
    return reqs_file


def add_argument_requirements_file(parser):
    """
    Helper for `argparse` to deal with a requiements file.

    This helper function adds command line options to be able to provide a requirements
    file from command line.

    Args:
        parser (ArgumentParser):  ArgumentParser instance to which to add the options to
                                  accept a requirements file.
    """
    parser.add_argument(
        '--requirement',
        '-r',
        default=get_default_reqs_file(),
        help='Optional path to the requirements file to be used.',
    )


def get_available_modes():
    """
    Return the list of available modes.

    The resulting list is determined by checking for the presence of requirements files,
    based on the "main" requirements file (which could be provided on the command line).
    For instance, if the main requirements file is `requirements.txt`, the modes are
    defined by presence of files of the form `requirements-<mode>.txt`.
    """
    parser = ArgumentParser(add_help=False)
    add_argument_requirements_file(parser)
    args, _ = parser.parse_known_args()

    if not args.requirement:
        return []

    basename, ext = os.path.splitext(args.requirement)
    mode_reqs_files = glob.glob(f'{basename}-*{ext}')
    modes = [f[len(basename) + 1 : -len(ext)] for f in mode_reqs_files]
    return modes


def get_default_install_pre_commit_hooks():
    """
    Return the default behavior should be to install pre-commit hooks or not.

    In practice, this boils down to checking whether the associated config file
    (`.pre-commit-config.yaml`) exists or not.
    This function is a helper for setting up the ArgumentParser.
    """
    pre_commit_config_file = os.path.join(os.getcwd(), '.pre-commit-config.yaml')
    return os.path.exists(pre_commit_config_file)


def main():
    available_modes = get_available_modes()

    parser = ArgumentParser(
        description='Create and initialize a virtual environment based on a '
        'requirements file. If a `.pre-commit-config.yaml` is present, '
        'pre-commit hooks will be installed.'
    )
    parser.add_argument(
        'venv_dir',
        nargs='?',
        default=os.path.join(os.getcwd(), '.venv'),
        help='Directory containing the virtual environment.',
    )
    add_argument_requirements_file(parser)
    parser.add_argument(
        '--clear',
        '-c',
        default=False,
        action='store_true',
        help='If given, clear an already existing virtual environment before '
        'initializing it with the provided requirements.',
    )
    parser.add_argument(
        '--force-remove',
        default=False,
        action='store_true',
        help='If given, fully remove an already existing virtual environment before '
        'initializing it with the provided requirements.',
    )
    parser.add_argument(
        '--no-pre-commit',
        '--no-install-pre-commit-hooks',
        dest='install_pre_commit_hooks',
        default=get_default_install_pre_commit_hooks(),
        action='store_false',
        help='If given, pre-commit hooks will not be installed.',
    )
    parser.add_argument(
        '--extra-reqs',
        '-er',
        action='append',
        default=[],
        help='Optional path to the requirements file to be used.',
    )
    parser.add_argument(
        '--skip-setup-venv',
        default=False,
        action='store_true',
        help='If given, skip setting up the virtual environment. Can be useful if the '
        'objective is to only set up the pre-commit hooks.',
    )

    if available_modes:
        parser.add_argument(
            '--mode',
            '-m',
            choices=available_modes,
            default=None,
            required=len(available_modes) >= 2,
        )
    args = parser.parse_args()

    if hasattr(args, 'mode'):
        # Define the mode in case there is only one available.
        if len(available_modes) == 1:
            args.mode = available_modes[0]

        # Convert the mode to extra requirements files that should be taken into
        # account.
        if args.mode is not None:
            basename, ext = os.path.splitext(args.requirement)
            args.extra_reqs.append(f'{basename}-{args.mode}{ext}')

    if args.force_remove:
        # Let's open the discussion if somebody would like to actually fully remove the
        # venv dir:
        raise NotImplementedError('## Not implemented yet. Is it really needed?')
    elif args.clear:
        print(f"## Clearing venv at '{args.venv_dir}'...")
        clear_venv(venv_dir=args.venv_dir)

    if not args.skip_setup_venv:
        if args.requirement:
            print(
                f"## Initializing venv at '{args.venv_dir}'\n"
                f"   using requirements file '{args.requirement}'...\n"
            )
        else:
            print(f"## Ensuring venv at '{args.venv_dir}'...")

        initialize_venv(
            venv_dir=args.venv_dir,
            reqs_file=args.requirement,
            extra_reqs=args.extra_reqs,
        )

    print('## Virtual environment successfully initialized!\n')

    if args.install_pre_commit_hooks:
        print('## Installing pre-commit hooks...')
        install_pre_commit_hooks(venv_dir=args.venv_dir)
        print('## Pre-commit hooks successfully installed!')


if __name__ == '__main__':
    main()
