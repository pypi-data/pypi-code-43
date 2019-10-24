# TODO docs

from collections import OrderedDict
from functools import lru_cache
from logging import getLogger
from os import R_OK
from os import access
from pathlib import Path

from dfmpy.utils.config import get_config
from dfmpy.utils.config import get_ignore_globs

# TODO docs
LOG = getLogger()

# TODO docs
# The cache should never get larger than 2, one for $HOME and one for the repo
# dir.  There should be no need for a cache of any other directory.
__FILE_TREE_CACHE_SIZE = 2


# TODO use more generators, do not create lists/tuples/dicts! Is that plausible?


def __ignore(path):
    # TODO docs
    # TODO unit test
    for pattern in get_ignore_globs():
        if path.match(pattern):
            return True
    return False


def __no_permissions_to_stat(path):
    # TODO docs - the path must exist, but is not accessible.
    # TODO unit test
    # TODO is it possible to remove access() in favor or Path() methods?
    return path.exists() and not access(path, R_OK)


def __find_all_paths(dir_path):
    # TODO docs - returns all files and (directories with markers)
    # TODO unit test
    marker = get_config().marker
    if not dir_path.exists():
        return tuple()
    else:
        for path in dir_path.iterdir():
            if __ignore(path):
                LOG.debug('Ignoring: %s', path)

            elif __no_permissions_to_stat(path):
                LOG.error('No permissions to read: %s', path)

            elif path_is_directory(path):
                if marker in path.name:
                    LOG.debug('Found special directory: %s', path)
                    yield path
                else:
                    LOG.debug('Traversing down directory: %s', path)
                    yield from get_all_paths(path)

            elif path_is_file(path):
                LOG.debug('Found file: %s', path)
                yield path

            elif path_is_symlink(path):
                LOG.debug('Found symlink: %s', path)
                yield path

            else:
                LOG.error('Found unknown node type: %s', path)


def __suffixes():
    # TODO docs
    # TODO unit test
    # Order of precedence:
    #   file.txt##hostname
    #   file.txt##hostname.system
    #   file.txt##systemname
    #   file.txt
    marker = get_config().marker
    delimiter = get_config().delimiter
    hostname = get_config().hostname
    system_type = get_config().system
    return tuple([
        marker + hostname,
        marker + delimiter.join([hostname, system_type]),
        marker + system_type,
    ])


def __normalize_for_phantom_files(file_paths):
    # TODO docs - explain this shit!  explain why it's needed when determining expected files when there only exists a markered file (and not the equivalent non-marked file).
    # TODO use this with EXTREME caution, since it's a hack it causes too many side-effects in other places -- causing misleading bugs.
    # TODO unit test
    # TODO optimize this? so it does not iterate over the list many times! (eg use of "in" keyword).
    file_paths = list(file_paths)
    marker = get_config().marker
    for fp in file_paths:
        file_name = str(fp)
        if marker in file_name:
            marker_index = file_name.find(marker)
            phantom_file_name = file_name[:marker_index]
            phantom_file_path = Path(phantom_file_name)
            if phantom_file_path not in file_paths:
                file_paths.append(phantom_file_path)
    file_paths.sort()
    return tuple(file_paths)


def __normalize_repo_path(file_path):
    # TODO docs
    # TODO unit test
    file_name = str(file_path)
    for suffix in __suffixes():
        file_with_suffix = file_name + suffix
        if Path(file_with_suffix).exists():
            return Path(file_with_suffix)
    return Path(file_path)


@lru_cache(maxsize=__FILE_TREE_CACHE_SIZE)
def get_all_paths(dir_name):
    # TODO docs - returns the same as __find_all_paths()
    # TODO unit test
    paths = []
    paths.extend(__find_all_paths(Path(dir_name)))
    paths.sort()
    return tuple(paths)


@lru_cache(maxsize=__FILE_TREE_CACHE_SIZE)
def get_installed_paths(install_dir, repo_dir):
    # TODO docs
    # TODO unit test
    LOG.debug('Searching for installed paths under: %s', install_dir)
    installed_paths = get_all_paths(install_dir)
    installed_paths = [p for p in installed_paths if path_is_symlink(p)]
    installed_paths = [p for p in installed_paths
                       if str(p.resolve()).startswith(repo_dir)]
    mapping = OrderedDict()
    mapping.update([(p, Path(p.resolve())) for p in installed_paths])
    return mapping


@lru_cache(maxsize=__FILE_TREE_CACHE_SIZE)
def get_expected_paths(install_dir, repo_dir):
    # TODO docs
    # TODO unit test
    LOG.debug('Searching for expected paths under: %s', repo_dir)
    marker = get_config().marker
    repo_paths = get_all_paths(repo_dir)
    repo_paths = __normalize_for_phantom_files(repo_paths)
    repo_paths = [p for p in repo_paths if not __ignore(p)]
    repo_paths = [p for p in repo_paths if marker not in p.name]
    mapping = OrderedDict()
    for rp in repo_paths:
        installed_file = str(rp).replace(repo_dir, install_dir)
        installed_path = Path(installed_file)
        nrp = __normalize_repo_path(rp)
        if nrp.resolve().exists():
            mapping[installed_path] = nrp
    return mapping


def path_is_directory(path):
    # TODO docs - explain why path.is_dir() alone is not safe.
    # TODO unit test
    return path_exists(path) and path.is_dir() and not path.is_symlink()


def path_is_file(path):
    # TODO docs - explain why path.is_file() alone is not safe.
    # TODO unit test
    return path_exists(path) and path.is_file()


def path_is_symlink(path):
    # TODO docs - explain why path.is_symlink() alone is not safe.
    # TODO unit test
    return path_exists(path) and path.is_symlink()


def path_exists(path):
    # TODO docs - explain why path.exists() alone is not safe.
    # TODO unit test
    try:
        # Stat the path, but do not follow symlinks.
        path.lstat()
        return True
    except FileNotFoundError:
        return False
