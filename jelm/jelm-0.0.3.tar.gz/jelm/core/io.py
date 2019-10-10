import json

from .jelm_class import Jelm


def reads_json(dump: str) -> Jelm:

    return Jelm(**json.loads(dump))


def read_json(file_path: str) -> Jelm:

    with open(file_path) as fp:
        dump = fp.read()

    return reads_json(dump)
