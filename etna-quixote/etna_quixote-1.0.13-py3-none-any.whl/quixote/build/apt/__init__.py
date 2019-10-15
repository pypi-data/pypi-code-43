import quixote.build.shell as shell
from shlex import quote


def add_repository(source: str) -> str:
    """
    Add a repository to APT

    :param source:          a string describing the repository to add (see man apt-add-add-repository(8) for details)
    """
    return shell.command(f"apt-add-repository -y {quote(source)}")


def remove_repository(source: str) -> str:
    """
    Remove a repository from APT

    :param source:          a string describing the repository to remove (see man apt-add-add-repository(8) for details)
    """
    return shell.command(f"apt-add-repository -y -r {quote(source)}")


def update() -> str:
    """
    Update the list of packages used by APT
    """
    return shell.command("apt-get update")


def install(*args: str) -> str:
    """
    Install some packages using APT

    :param args:            the packages to install
    """
    return shell.command("apt-get install -y " + ' '.join(args), env={"DEBIAN_FRONTEND": "noninteractive"})


def remove(*args: str) -> str:
    """
    Remove some packages using APT

    :param args:            the packages to remove
    """
    return shell.command("apt-get remove -y " + ' '.join(args), env={"DEBIAN_FRONTEND": "noninteractive"})


def autoremove(*args: str) -> str:
    """
    Remove some packages using APT, also removing unused dependencies

    :param args:            the packages to remove
    """
    return shell.command("apt-get autoremove -y " + ' '.join(args), env={"DEBIAN_FRONTEND": "noninteractive"})


def purge(*args: str) -> str:
    """
    Remove some packages using APT, also removing their configuration files

    :param args:            the packages to purge
    """
    return shell.command("apt-get autoremove -y " + ' '.join(args), env={"DEBIAN_FRONTEND": "noninteractive"})


def upgrade() -> str:
    """
    Upgrade the packages installed using APT
    """
    return shell.command("apt-get upgrade -y", env={"DEBIAN_FRONTEND": "noninteractive"})
