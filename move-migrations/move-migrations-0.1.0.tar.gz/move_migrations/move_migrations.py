#!/usr/bin/python3

"""
    This script tries to solve the following issue:
        team makes a new django migration in marmot
        team opens a PR
        time passes
        team rebase PR onto master
        team has to rename their migration files for them to be the latest
"""

import argparse
import os
import re
import sys
from argparse import Namespace
from glob import glob

import prompt
from move_migrations.move_migrations_utils import (
    clean_path,
    find_latest_migration,
    find_migrations_to_be_moved,
    get_new_name,
    move,
    name_to_dependence,
    update_dependence,
    update_latest_migrations_txt,
)


def make_args():
    print("Set prefixed migrations to be the latest.")
    path_to_migrations = prompt.string(
        prompt="Enter the path to your migration folder (default=./api/underwriter/migrations):",
        empty=True,
    )
    if path_to_migrations is None:
        path_to_migrations = "./api/underwriter/migrations"
    user_want_to_update_test_file = prompt.character(
        prompt="Would like to update marmot/api/underwriter/tests/latest_migration.txt? [y]/n",
        empty=True,
    )
    should_update_test = (
        user_want_to_update_test_file != "n" or user_want_to_update_test_file != "N"
    )
    prefix = prompt.string(
        prompt="Enter the prefix to be used to recognize migrations to be moved (default: MOVE)",
        empty=True,
    )
    if prefix is None:
        prefix = "MOVE"

    return Namespace(
        path_to_migrations=path_to_migrations,
        should_update_test=should_update_test,
        prefix=prefix,
    )


def main(args=None):
    if args is None:
        args = make_args()

    path_to_migrations = clean_path(args.path_to_migrations)
    prefix = args.prefix
    should_update_test = args.should_update_test

    latest_index, latest_migration_name = find_latest_migration(path_to_migrations)
    if latest_migration_name == "":
        print("Could not find the latest migrations; exiting.")
        return

    to_be_moved = find_migrations_to_be_moved(path_to_migrations, prefix)
    to_be_moved.sort()

    if len(to_be_moved) == 0:
        print(f"No migrations found with the prefix {prefix} in {path_to_migrations}!")
        return

    new_dependence = name_to_dependence(latest_migration_name)
    for i, migration in enumerate(to_be_moved):
        new_index = int(latest_index) + i + 1
        new_name = get_new_name(prefix, migration, new_index)
        new_migration = move(migration, path_to_migrations, new_name)
        update_dependence(new_migration, new_dependence)
        print(new_dependence + " -> " + new_name)
        new_dependence = name_to_dependence(new_name)

    if should_update_test:
        update_latest_migrations_txt(path_to_migrations, new_dependence)

    print("Done!")
    print(f"The latest migration to date is: \t{new_dependence}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set prefixed migrations to be the latest."
    )
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        required=True,
        dest="path_to_migrations",
        help="path to your migration folder (ie: marmot/api/underwriter/migrations)",
    )
    parser.add_argument(
        "--prefix",
        dest="prefix",
        required=False,
        default="MOVE",
        help="prefix to be used to recognize migrations to be moved (default: MOVE)",
    )
    parser.add_argument(
        "-t",
        "--update-test",
        type=bool,
        dest="should_update_test",
        required=False,
        default=False,
        help="set to True to update marmot/api/underwriter/tests/latest_migration.txt",
    )
    main(parser.parse_args())
