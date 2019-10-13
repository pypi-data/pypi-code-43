#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import getcwd
from pathlib import Path

from funity import *


def main():
    cache_dir = Path(getcwd()) / 'editor.cache'
    editors = UnityEditor.find_in(cache=str(cache_dir))

    print(editors)


if __name__ == '__main__':
    main()
