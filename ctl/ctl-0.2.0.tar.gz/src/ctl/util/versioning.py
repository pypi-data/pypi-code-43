def version_tuple(version):
    print("VERSION", version)
    """ Returns a tuple from version string """
    return tuple(version.split("."))


def version_string(version):
    """ Returns a string from version tuple or list """
    return ".".join(["{}".format(v) for v in version])


def validate_semantic(version):
    if not isinstance(version, (list, tuple)):
        version = version_tuple(version)

    try:
        major, minor, patch, dev = version
    except ValueError:
        major, minor, patch = version

    return tuple([int(n) for n in version])


def bump_semantic(version, segment):
    version = list(validate_semantic(version))
    if segment == "major":
        return (version[0] + 1, 0, 0)
    elif segment == "minor":
        return (version[0], version[1] + 1, 0)
    elif segment == "patch":
        return (version[0], version[1], version[2] + 1)
    elif segment == "dev":
        try:
            return (version[0], version[1], version[2], version[3] + 1)
        except IndexError:
            return (version[0], version[1], version[2], 1)
