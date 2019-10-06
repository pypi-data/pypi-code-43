# -*- coding: utf-8 -*-
import json
import os
import sys

from os.path import dirname


def main():
    args = json.loads(sys.argv[1])

    collect_only = bool(args.get("collect-only", False))
    files = args.get("files", [])
    nodeids = args.get("nodeids", [])

    # Create the command line to launch
    run_test_path = os.environ["MERCURIAL_RUN_TESTS_PATH"]
    cmd = [
        run_test_path,
        "-l",
    ]

    if collect_only:
        cmd.append("--list-tests")

    if files:
        cmd.extend(files)
    elif nodeids:
        cmd.extend(nodeids)

    # Replace current process with the cmd
    print("CMD", cmd)
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["CUSTOM_TEST_RESULT"] = "mercurial_litf"
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
