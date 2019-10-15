# coding=utf-8
from __future__ import absolute_import, print_function

import argparse
import contextlib
import os
import sys

from suanpan.imports import imports


def run(component, *args, **kwargs):
    if isinstance(component, str):
        component = imports(component)
    with env(**kwargs.pop("env", {})):
        return component(*args, **kwargs).start()


@contextlib.contextmanager
def env(**kwargs):
    old = {key: os.environ.get(key) for key in kwargs}
    os.environ.update(kwargs)
    yield os.environ
    os.environ.update(old)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    _args, _rest = parser.parse_known_args()

    sys.argv = sys.argv[:1]
    return run(_args.component, *_rest)


if __name__ == "__main__":
    cli()
