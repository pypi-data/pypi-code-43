from glob import glob
from itertools import chain
import re
from os.path import abspath, isdir
from os import rename
import sys

DEFAULTPKGNAME = "yourpackagename"


def do_replacements(
    text_replacements,
    directory_replacements,
    file_extensions,
    additional_files,
    ignore_files,
):

    path_iterator = chain(
        *[glob("**/*." + ext, recursive=True) for ext in file_extensions]
    )
    path_iterator = chain(path_iterator, additional_files)

    messages = []

    path_to_newlines = dict()
    dirs_to_rename = dict()

    for path in path_iterator:
        if abspath(path) in ignore_files:
            continue
        with open(path, "r") as f:
            lines = f.readlines()

        newlines = []
        for x1, x2 in text_replacements:

            pattern = re.compile(x1)
            for linenum, line in enumerate(lines):
                for m in pattern.finditer(line):
                    messages.append(
                        "{} {}:{} | to be replace '{}' with '{}'".format(
                            path, linenum, m.start(), x1, x2
                        )
                    )
                newlines.append(re.sub(x1, x2, line))
        path_to_newlines[abspath(path)] = newlines

    for x1, x2 in directory_replacements:
        if isdir(abspath(x1)):
            messages.append(
                "rename directory\t'{}'\n\t\tto\t'{}'".format(abspath(x1), abspath(x2))
            )
            dirs_to_rename[abspath(x1)] = abspath(x2)

    for msg in messages:
        print(msg)

    print()
    if any(path_to_newlines.values()):
        response = input("Rewrite files? (y|[n]): ")
        if response.lower() == "y":
            print("Rewriting files")
            for path, lines in path_to_newlines.items():
                with open(path, "w") as f:
                    f.writelines(lines)
            print("Renaming directories")
            for oldpath, newpath in dirs_to_rename.items():
                rename(oldpath, newpath)
            return True
        else:
            print("Canceled. No files written.")
            return False
    else:
        print("No replacements found.")
        return False


def initialize(pkgname, fromname=DEFAULTPKGNAME):
    text_replacements = [(fromname, pkgname)]
    file_extensions = ["py", "toml"]
    additional_files = ["Makefile"]
    ignore_files = [abspath(__file__)]
    if do_replacements(
        text_replacements,
        text_replacements,
        file_extensions,
        additional_files,
        ignore_files,
    ):
        print(
            "🐝 Don't forget to edit your package information in the pyproject.toml file!"
        )


if __name__ == "__main__":
    try:
        initialize(sys.argv[1], sys.argv[2])
    except:
        initialize(sys.argv[1])
