# TODO docs

from logging import getLogger

from dfmpy.utils.config import get_config
from dfmpy.utils.files import get_expected_paths
from dfmpy.utils.files import get_installed_paths

# TODO docs
LOG = getLogger()


def __unique_key_for_value(items, find_value):
    # TODO docs
    # TODO unit test
    keys = tuple([key for key, value in items if value == find_value])
    if not keys:
        return None
    elif len(keys) != 1:
        raise LookupError(f'Multiple keys for value: {find_value} => {keys}')
    return keys[0]


def __get_broken_paths(expected_paths, installed_paths):
    # TODO docs - The installed file points to a non-existent file.
    # TODO unit test
    LOG.debug('Finding installed files that point to non-existent files.')
    for f in installed_paths:
        if not f.resolve().exists():
            yield f, f.resolve()


def __get_stale_paths(expected_paths, installed_paths):
    # TODO docs - The installed file resolves to the wrong repo file.
    # TODO unit test
    LOG.debug('Finding installed files that resolve to the wrong file.')
    for f in installed_paths:
        expected = __unique_key_for_value(expected_paths.items(), f.resolve())
        if f != expected:
            yield f, expected


def __get_not_installed_paths(expected_paths, installed_paths):
    # TODO docs - The expected file is not pointed to by an installed file.
    # TODO unit test
    LOG.debug('Finding expected files that are not installed.')
    installed_files_keys = installed_paths.keys()
    for f in expected_paths.keys():
        if f not in installed_files_keys:
            yield f, expected_paths[f]


def __get_proper_paths(expected_paths, installed_paths):
    # TODO docs - The expected file is properly installed.
    # TODO unit test
    # TODO this needs testing once "sync" is implemented!
    LOG.debug('Finding installed properly installed files.')
    installed_files_keys = installed_paths.keys()
    for f in expected_paths:
        if f in installed_files_keys:
            installed = installed_paths[f]
            if f.resolve() == installed.resolve():
                yield f, expected_paths[f]


def __print(logger, files, message, comparator_symbol):
    # TODO docs
    # TODO unit test
    if files:
        for idx, (left, right) in enumerate(files):
            if idx == 0:
                # Since "files" could be a generator, only log the message if we
                # can actually iterate over the items.  Thus only print for the
                # first element.
                logger(message)
            logger('%s %s %s', left, comparator_symbol, right)


def ls(cli):
    # TODO docs
    # TODO unit test
    # TODO add a "--tree" option to the this command

    install_dir = get_config().install_dir
    repo_dir = get_config().repository

    expected_paths = get_expected_paths(install_dir, repo_dir)
    installed_paths = get_installed_paths(install_dir, repo_dir)

    broken = __get_broken_paths(expected_paths, installed_paths)
    __print(LOG.critical, broken, 'Found broken files:', '?=')

    stale = __get_stale_paths(expected_paths, installed_paths)
    __print(LOG.error, stale, 'Found stale files:', '~=')

    not_installed = __get_not_installed_paths(expected_paths, installed_paths)
    __print(LOG.warning, not_installed, 'Found files not installed:', '!=')

    proper = __get_proper_paths(expected_paths, installed_paths)
    __print(LOG.info, proper, 'Found installed files:', '==')
