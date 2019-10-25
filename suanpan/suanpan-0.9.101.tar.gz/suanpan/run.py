# coding=utf-8
from __future__ import absolute_import, print_function

import argparse
import contextlib
import copy
import sys

from suanpan.imports import imports
from suanpan.utils import env as spenv


def run(component, *args, **kwargs):
    if isinstance(component, str):
        component = imports(component)
    with env(**kwargs.pop("env", {})):
        return component(*args, **kwargs).start()


@contextlib.contextmanager
def env(**kwargs):
    old = copy.deepcopy(spenv.environ)
    spenv.update(kwargs)
    yield spenv.environ
    spenv.update(old)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    _args, _rest = parser.parse_known_args()

    sys.argv = sys.argv[:1]
    return run(_args.component, *_rest)


if __name__ == "__main__":
    cli()
