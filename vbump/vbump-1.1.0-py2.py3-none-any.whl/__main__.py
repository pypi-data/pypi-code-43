# /usr/bin/env python

import re
from argparse import ArgumentParser
from os import getcwd, path

VERSION_FILE = path.abspath(path.join(path.split(getcwd())[1], "__version__.py"))
SETUP_FILE = path.abspath(path.join(getcwd(), "setup.py"))


def get_args():
    parser = ArgumentParser(
        prog="vbump", description="Yet another Python version bumper"
    )
    level = parser.add_mutually_exclusive_group()
    level.add_argument("--patch", action="store_true", help="increment patch level")
    level.add_argument("--minor", action="store_true", help="increment minor level")
    level.add_argument("--major", action="store_true", help="increment major level")
    parser.add_argument(
        "--test", action="store_true", help="shows result of version bump with writing"
    )
    return parser.parse_args()


def parse_target(target):
    with open(target) as fp:
        version_contents = fp.read().strip()
    result = re.findall(r'VERSION ?= ?"(\d)\.(\d)\.(\d)"', version_contents, re.I)
    assert len(result) == 1, "%s does not match expected syntax" % target
    return [int(level) for level in result[0]]


def write_to_version_file(semver):
    with open(VERSION_FILE, "w") as fp:
        fp.write('VERSION = "%s"' % semver + "\n")


def write_to_setup_file(semver):
    with open(SETUP_FILE, "r") as fp:
        setup_contents = fp.read()
    updated_sutup_contents = re.sub(
        r'version ?= ?"\d\.\d\.\d"', 'version="%s"' % semver, setup_contents
    )
    with open(SETUP_FILE, "w") as fp:
        fp.write(updated_sutup_contents)


def main():
    args = get_args()

    # Determine target
    if path.exists(VERSION_FILE):
        target = VERSION_FILE
    elif path.exists(SETUP_FILE):
        target = SETUP_FILE
    else:
        raise FileNotFoundError("could not find __version__.py or setup.py")

    # Parse target
    major, minor, patch = parse_target(target)
    current_version = "%d.%d.%d" % (major, minor, patch)

    # Print current version if no bump level specified
    if not any((args.major, args.minor, args.patch)):
        print(current_version)
        return

    # Determine updated version
    current_version = "%d.%d.%d" % (major, minor, patch)
    print("Using %s" % target)
    if args.major:
        updated_version = "%d.%d.%d" % (major + 1, minor, patch)
    elif args.minor:
        updated_version = "%d.%d.%d" % (major, minor + 1, patch)
    elif args.patch:
        updated_version = "%d.%d.%d" % (major, minor, patch + 1)
    print("Updated version: %s => %s" % (current_version, updated_version))

    # Write updated version
    if not args.test:
        if target == VERSION_FILE:
            write_to_version_file(updated_version)
        else:
            write_to_setup_file(updated_version)


if __name__ == "__main__":
    main()
