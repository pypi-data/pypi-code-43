import json

from .jelm_class import Jelm


def read_json_dump(dump: str) -> Jelm:

    return Jelm(**json.loads(dump))
