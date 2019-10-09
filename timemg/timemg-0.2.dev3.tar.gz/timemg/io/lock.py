#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import fcntl

def lock_path(file_path):
    # TODO: test or rewrite this !!!
    # Ensure a single instance of an application is opening a file (TODO: check whether it works on MacOS and Windows!)

    fd = open(file_path + ".lock", "w")

    try:
        # LOCK_EX = acquire an exclusive lock on fd
        # LOCK_NB = make a nonblocking request
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print("Acquire an exclusive lock on ", file_path)
    except IOError:
        print(file_path + ".lock" + " is locked ; another instance is running. Exit.", file=sys.stderr)
        sys.exit(1)


def unlock_path(file_path):
    # TODO: test or rewrite this !!!

    fd = open(file_path + ".lock", "w")

    try:
        # LOCK_UN = unlock fd
        fcntl.flock(fd, fcntl.LOCK_UN)
        print("Unlock " + file_path)
    except IOError:
        print("Cannot unlock " + file_path, file=sys.stderr)
        sys.exit(1)

