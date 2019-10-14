"""
``qmenta.core.version`` provides a standard way of determining the version of
a QMENTA module, and to use this version as ``qmenta.modulename.__version__``.

The recommended way of using ``qmenta.core.version``, is to include the
following code in the ``setup.py`` of your Python module::

    from os import path
    from qmenta.core import version

    current_dir = path.dirname(path.abspath(__file__))
    spec_dir = path.dirname(current_dir)

    v = version.from_build_yaml_and_revfile(spec_dir)
    version.write(v, path.join(current_dir, 'qmenta/yourmodulename'))

This will read the ``build.yaml`` file from the current directory and extract
the release version from that. If a ``REVISION`` file also exists in the
current directory, the revision will be read from that file and appended to
the version returned by :py:func:`from_build_yaml_and_revfile()`.

It is recommended to use::

    git rev-list --count HEAD > REVISION

in your ``Jenkinsfile`` to set the revision number for internal development
releases, and to not create the ``REVISION`` file when creating a public
release.

In the call to ``setuptools.setup()``, pass the version::

    version=v

to have the module packaged with the correct version. Now, when building the
module wheel file, ``qmenta/yourmodulename/VERSION`` is written and the module
will be packaged with the proper version. Make sure that
``qmenta/yourmodulename/VERSION`` is included in your ``MANIFEST.in`` so that
it is available in the ``yourmodulename`` package.

To make the variable ``qmenta.yourmodulename.__version__`` available, include
the following code in ``qmenta/yourmodulename/__init__.py``::

    from qmenta.core import version
    from qmenta.core.errors import CannotReadFile

    try:
        __version__ = version.read(path.dirname(__file__))
    except CannotReadFile:
        # VERSION file was not created yet
        __version__ = '0.dev0'

Catching ``CannotReadFile`` is necessary because ``__init__.py`` is executed
when importing from ``qmenta.core``, which is done in ``setup.py`` before
the ``VERSION`` file is written.
"""

from os import path
import yaml

from .errors import (CannotReadFileError, CannotWriteFileError,
                     InvalidBuildSpecError)


def read(dirname: str) -> str:
    """
    Read the version from a file.

    Parameters
    ----------
    dirname : str
        The directory that contains the ``VERSION`` file

    Raises
    ------
    qmenta.core.errors.CannotReadFile
        When the input ``VERSION`` file cannot be read

    Returns
    -------
    str
        The version read from the file
    """
    filename = path.join(dirname, 'VERSION')
    try:
        with open(filename) as f:
            v = f.read()
    except IOError:
        raise CannotReadFileError('Cannot read file: {}'.format(filename))
    return v.strip()


def write(version: str, dirname: str) -> None:
    """
    Write the given version to the ``VERSION`` file in the specified directory.
    If the file exists, it will be overwritten.

    Parameters
    ----------
    version : str
        The version string to write to the file. Newline will be appended.
    dirname : str
        The directory in which the VERSION file will be written

    Raises
    ------
    qmenta.core.errors.CannotWriteFile
        When the ``VERSION`` file cannot be written
    """
    filename = path.join(dirname, 'VERSION')
    try:
        with open(filename, 'w') as f:
            f.write(version)
            # Without newline you don't see the version if we 'cat' the file
            # on Jenkins
            f.write('\n')
    except IOError:
        raise CannotWriteFileError(filename)


def from_build_yaml_and_revfile(dirname: str) -> str:
    """
    Create a version string composed of the release version specified in
    the ``build.yaml`` file and revision in the ``REVISION`` file that are
    located in the specified directory.

    Parameters
    ----------
    dirname : str
        The directory where the ``build.yaml`` and optional ``REVISION`` files
        are located. If the ``REVISION`` file exists, it must be a text file
        containing **only** the revision number.

    Raises
    ------
    qmenta.core.errors.CannotReadFile
        When the ``build.yaml`` file cannot be read
    qmenta.core.errors.InvalidBuildSpec
        When the ``build.yaml`` is not a proper YAML file or does not define
        a valid ``version``

    Returns
    -------
    str
        The composited version. Examples: '2.1' if there is no ``REVISION``
        file, or '2.1.dev333' if ``REVISION`` and contains revision '333'.
    """
    buildfile = path.join(dirname, 'build.yaml')
    try:
        with open(buildfile) as build_yaml:
            build_specs = yaml.load(build_yaml)
    except IOError:
        raise CannotReadFileError(
            'Cannot read build file: {}'.format(buildfile)
        )

    if not isinstance(build_specs, dict):
        raise InvalidBuildSpecError('Invalid yaml file: {}'.format(buildfile))

    try:
        release = str(build_specs['version'])
    except KeyError:
        raise InvalidBuildSpecError('No version in {}'.format(buildfile))

    if not release:
        raise InvalidBuildSpecError('Empty version in {}'.format(buildfile))

    revfile = path.join(dirname, 'REVISION')
    revision = ''
    try:
        with open(revfile) as f:
            revision = f.read().strip()
            # revision may be empty string
    except IOError:
        # No readable REVISION file
        pass

    v: str
    if revision:
        v = '.'.join([release, 'dev' + revision])
    else:
        v = release
    return v
