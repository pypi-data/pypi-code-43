import argparse
import os
import re
import sys
from argparse import Namespace
from glob import glob

import prompt


def clean_path(path):
    """
        Strip a path of its last '/' if there is one
    """
    if path[-1] == "/":
        return path[:-1]
    return path


def name_to_dependence(name):
    return name.split(".py")[0]


def find_latest_migration(path_to_migrations):
    """
        Look for the latest migration in the provided 'path_to_migrations' and
        return its 'index' and 'full_name'. This assumes that migrations are
        named as "0123_name_of_migration.py". If the latest migration is
        called:
            '0999_latest.py'
        this will return:
            tuple('0999', '0999_latest.py')
    """
    migrations = glob(path_to_migrations + "/[0-9]*.py")
    migrations.sort()

    if len(migrations) == 0:
        print(f"Could not find any migrations in {path_to_migrations}")
        return 0, ""

    full_name: str = migrations[-1].split("/")[-1]
    index: str = full_name.split("_")[0]

    return index, full_name


def find_migrations_to_be_moved(path_to_migrations, prefix):
    """
        Return the list of migrations in the provided 'path_to_migrations' prefixed by the
        provided 'prefix'.
    """
    return glob(path_to_migrations + "/" + prefix + "*.py")


def get_new_name(prefix, migration, new_index):
    """
        From the migration prefixed by 'prefix', change the index of the provided 'migration
        using the provided 'new_index'. Example:
            get_new_name('MOVE', 'path-to-migrations/0999_migration.py', 1666) ->  '1666_migration.py'

    """
    parsed = migration.split(prefix)
    current_name = parsed[-1]
    new_name = "{:04d}".format(new_index) + "_" + "_".join(current_name.split("_")[1:])
    return new_name


def move(migration, path_to_migrations, new_name):
    new_path = path_to_migrations + "/" + new_name
    os.rename(migration, new_path)
    return new_path


def update_dependence(new_migration, new_dependence):
    s: str
    with open(new_migration, "r") as f:
        s = f.read()
        s = re.sub(
            "\('underwriter', '.*'\)", "('underwriter', '" + new_dependence + "')", s
        )

    with open(new_migration, "w") as f:
        f.write(s)


def update_latest_migrations_txt(path_to_migrations, latest_migration):
    path_to_test_file = "/".join(
        [*path_to_migrations.split("/")[:-1], "tests/latest_migration.txt"]
    )
    with open(path_to_test_file, "w") as f:
        f.write(latest_migration)
