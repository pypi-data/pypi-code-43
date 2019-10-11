import quixote.build.shell as shell


def install(
        *args: str,
        from_file: str = None,
        target_directory: str = None,
        only_download_to: str = None,
        upgrade: bool = False,
        reinstall_on_upgrade: bool = False,
        root_dir: str = None
) -> str:
    """
    Install some packages using the pip command

    :param args:                    the packages to install
    :param from_file:               a file listing the packages to remove (see pip -r)
    :param target_directory:        the directory in which the packages should be installed (see pip -t)
    :param only_download_to:        the directory to which packages should be downloaded (see pip --download)
    :param upgrade:                 whether the packages should be upgraded (see pip -U)
    :param reinstall_on_upgrade:    whether the packages should be reinstalled when upgraded (see pip --force-reinstall)
    :param root_dir:                the alternate root directory in which the packages should be installed (see pip --root)
    """
    args = list(args)
    if from_file is not None:
        args.append(f"-r {from_file}")
    if target_directory is not None:
        args.append(f"-t {target_directory}")
    if only_download_to is not None:
        args.append(f"-d {only_download_to}")
    if upgrade is True:
        args.append("-U")
    if reinstall_on_upgrade is True:
        args.append("--force-reinstall")
    if root_dir is not None:
        args.append(f"--root {root_dir}")
    return shell.command("pip3 install " + ' '.join(args))


def uninstall(*args: str, from_file=None) -> str:
    """
    Uninstall some packages using the pip command

    :param args:                    the packages to uninstall
    :param from_file:               a file listing the packages to remove (see pip -r)
    """
    return shell.command("pip3 uninstall -y " + ' '.join(args) + f" -r {from_file}" if from_file is not None else "")
