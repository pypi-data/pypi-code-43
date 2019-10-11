import quixote.build.shell as shell
import quixote.build.apt as apt


def install_docker_cli():
    """
    Install the docker CLI
    """

    apt.update()
    apt.install(
        "apt-transport-https",
        "ca-certificates",
        "curl",
        "gnupg-agent",
        "software-properties-common"
    )
    shell.command("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -")
    shell.command("apt-key fingerprint 0EBFCD88")
    # TODO: find a way not to hardcode this:
    apt.add_repository("deb https://download.docker.com/linux/debian buster stable")
    apt.update()
    apt.install("docker-ce-cli")
