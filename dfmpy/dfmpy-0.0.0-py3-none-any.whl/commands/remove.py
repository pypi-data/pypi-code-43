# TODO docs

from logging import getLogger
from pathlib import Path

from dfmpy.utils.config import get_config
from dfmpy.utils.files import get_installed_paths
from dfmpy.utils.files import path_is_directory
from dfmpy.utils.files import path_is_file
from dfmpy.utils.files import path_is_symlink
from dfmpy.utils.interactive import ask_to

# TODO docs
LOG = getLogger()


def __remove_empty_parents(file_path, root_names):
    # TODO docs
    # TODO unit test
    root_paths = [Path(r) for r in root_names]
    for p in file_path.parents:
        if p in root_paths:
            # Exit this loop to finish quickly since we hit a root.
            break
        elif not list(p.iterdir()):
            # Directory is empty, delete it.
            p.rmdir()
            LOG.warning('Unlinked empty directory: %s', p)
        else:
            # Exit early since we hit a non-empty directory.
            LOG.debug('Parent directory not empty, not unlinking: %s', p)
            break


def unlink_path(path, force, interactive, roots=None):
    # TODO docs
    # TODO unit test
    if not roots:
        roots = ('',)

    if ask_to(f'Unlink path: {path}', force, interactive):
        if path_is_directory(path):
            path.rmdir()
            LOG.warning('Removed directory: %s', path)
        elif path_is_file(path):
            path.unlink()
            LOG.warning('Removed file: %s', path)
        elif path_is_symlink(path):
            path.unlink()
            LOG.warning('Removed symlink: %s', path)
        else:
            path.unlink()
            LOG.error('Removed unknown file type: %s', path)
        __remove_empty_parents(path, roots)

    else:
        LOG.info('Simulated unlink: %s -> %s', str(path), path.resolve())


def remove(cli):
    # TODO docs
    # TODO unit test

    install_dir = get_config().install_dir
    repo_dir = get_config().repository

    installed_paths = get_installed_paths(install_dir, repo_dir)

    if not cli.force:
        LOG.error("Must use '-f' to force removal of dotfiles.")

    for file in installed_paths:
        unlink_path(file,
                    cli.force,
                    cli.interactive,
                    tuple([install_dir, repo_dir]),
                    )
