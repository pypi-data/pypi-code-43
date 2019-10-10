from pathlib import Path
import os
import json
import eventlet
import collections
import shutil

featurize_dir = Path() / '.featurize_experiments'

if not os.path.isdir(featurize_dir):
    os.mkdir(featurize_dir)


def tail(file_path, callback, internal=1):
    current = open(file_path, 'r')
    curino = os.fstat(current.fileno()).st_ino
    while True:
        while True:
            buf = current.read(1024)
            if buf == "":
                break
            callback(buf)
        try:
            if os.stat(file_path).st_ino != curino:
                new = open(file_path, "r")
                current.close()
                current = new
                curino = os.fstat(current.fileno()).st_ino
                continue
        except IOError:
            pass
        eventlet.sleep(internal)


def server_file(file_name, experiment=''):
    if not isinstance(experiment, str):
        experiment = experiment.name

    experiment_dir = Path.home() / '.minetorch_server' / experiment

    try:
        os.makedirs(experiment_dir)
    except FileExistsError:
        pass

    _file = experiment_dir / file_name
    if not os.path.isfile(_file):
        _file.touch()

    return _file.resolve()


def runtime_file(file_name, experiment=''):
    if not isinstance(experiment, str):
        experiment = experiment.name

    experiment_dir = Path.home() / '.minetorch' / experiment
    _file = experiment_dir / file_name

    try:
        os.makedirs(_file.parent)
    except FileExistsError:
        pass

    if not os.path.isfile(_file):
        _file.touch()

    return _file.resolve()


def dict_merge(dct, merge_dct):
    for k, _ in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def update_json_file(file, object):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    dict_merge(data, object)
    with open(file, 'w') as f:
        json.dump(data, f)


def read_json_file(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


__all__ = ['tail', 'server_file', 'runtime_file', 'dict_merge']
