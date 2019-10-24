# TODO docs

from logging import getLogger

from dfmpy.commands.remove import unlink_path
from dfmpy.utils.config import get_config
from dfmpy.utils.files import get_expected_paths
from dfmpy.utils.files import get_installed_paths
from dfmpy.utils.files import path_is_file
from dfmpy.utils.files import path_is_symlink
from dfmpy.utils.interactive import ask_to

# TODO docs
LOG = getLogger()


def __mkdir_parents(symlink_path):
    # TODO docs
    # TODO unit test
    symlink_path.exists()
    if not symlink_path.parent.exists():
        LOG.warning('Making directory with parents: %s', symlink_path.parent)
        symlink_path.parent.mkdir(parents=True)


def __link_path(symlink_path, target_path, force, interactive):
    # TODO docs
    # TODO unit test
    if ask_to(f'Overwrite to link file: {symlink_path}', force, interactive):
        __mkdir_parents(symlink_path)
        symlink_path.symlink_to(target_path)
        LOG.warning('Symlinked: %s -> %s', symlink_path, target_path)
    else:
        LOG.info('Simulated symlink: %s -> %s', symlink_path, target_path)


def __sync_expected_paths(expected_paths, force, interactive):
    # TODO docs
    # TODO unit test
    LOG.info('Syncing files.')
    force_it_kwargs = {'force': True, 'interactive': False}
    for symlink_path, target_path in expected_paths.items():

        if path_is_symlink(symlink_path):
            if symlink_path.resolve() == target_path:
                # The symlink exists and points to the correct target.
                LOG.debug('No need to sync: %s -> %s',
                          symlink_path,
                          target_path)
            else:
                # If the symlink exists, but it points to the wrong target!
                sync_prompt = f'Sync broken link: {symlink_path}'
                if ask_to(sync_prompt, force, interactive):
                    unlink_path(symlink_path, **force_it_kwargs)
                    __link_path(symlink_path, target_path, **force_it_kwargs)

        elif path_is_file(symlink_path):
            sync_prompt = f'Replace existing file: {symlink_path}'
            if ask_to(sync_prompt, force, interactive):
                unlink_path(symlink_path, **force_it_kwargs)
                __link_path(symlink_path, target_path, **force_it_kwargs)

        else:
            # The file/link does not exist, so create it.
            __link_path(symlink_path, target_path, force, interactive)


def __remove_broken_files(installed_paths, force, interactive):
    # TODO docs
    # TODO unit test
    LOG.info('Checking for broken files.')
    for p in installed_paths:
        if not p.resolve().exists():
            unlink_path(p, force, interactive)


def sync(cli):
    # TODO docs
    # TODO unit test

    install_dir = get_config().install_dir
    repo_dir = get_config().repository

    expected_paths = get_expected_paths(install_dir, repo_dir)
    installed_paths = get_installed_paths(install_dir, repo_dir)

    if not cli.force:
        LOG.error("Must use '-f' to force overwriting of symlinked dotfiles.")

    __sync_expected_paths(expected_paths, cli.force, cli.interactive)
    __remove_broken_files(installed_paths, cli.force, cli.interactive)
