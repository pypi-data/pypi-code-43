from collections import namedtuple
from functools import wraps
import os
from pathlib import Path

import click
from litezip import (
    parse_collection,
    parse_module
)

def noop(*args, **kwargs):
    pass  # pragma: no cover


def to_str_dict(collection_or_module):
    return {
        'id': str(collection_or_module.id),
        'file': str(collection_or_module.file),
        'resources': list(map(
            lambda resource: str(resource.data),
            collection_or_module.resources
        ))}


task_keys, task_default_values = zip(*{
    'before_action': noop,
    'module_action': noop,
    'collection_action': noop
}.items())
NebTask = namedtuple('NebTask', task_keys)
NebTask.__new__.__defaults__ = task_default_values


def execute_task_actions(content_dir, task):
    before_action, module_action, collection_action = task

    before_action()

    content_dir = Path(content_dir).resolve()
    ex = [lambda filepath: '.sha1sum' in filepath.name]
    for dirname, subdirs, filenames in os.walk(str(content_dir)):
        path = Path(dirname)
        if 'collection.xml' in filenames:
            collection = parse_collection(path, excludes=ex)
            action_params = to_str_dict(collection)
            collection_action(**action_params)
        elif 'index.cnxml' in filenames:
            module = parse_module(path, excludes=ex)
            action_params = to_str_dict(module)
            module_action(**action_params)


def neb_task(cli, name):
    def task_wrapper(task_func):
        @cli.command(name, help_section='neb-tasks')
        @click.argument('content_dir',
                        type=click.Path(exists=True, file_okay=False))
        @click.pass_context
        @wraps(task_func)
        def wrapper(ctx, content_dir, *args, **kwargs):
            try:
                result = task_func(*args, **kwargs)
                assert(type(result) == NebTask)
            except (TypeError, AssertionError):
                bad_type = type(result).__name__
                raise Exception(
                    'Task {} returns {} not NebTask'.format(name, bad_type))
            execute_task_actions(content_dir, result)
            return None
        return wrapper
    return task_wrapper
