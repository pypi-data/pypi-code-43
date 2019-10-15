from quixote.build.shell import command


def install(*args: str, recursive=False):
    if recursive is True:
        return command("dpkg -R -i " + ' '.join(args))
    else:
        return command("dpkg -i " + ' '.join(args))


def remove(*args: str, pending=False):
    if pending is True:
        if len(args) > 0:
            raise ValueError("The 'pending' parameter cannot be used along with package names")
        return command("dpkg -r --pending")
    else:
        return command("dpkg -r " + ' '.join(args))
