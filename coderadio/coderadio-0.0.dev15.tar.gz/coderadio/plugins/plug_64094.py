import json
import logging
import requests
import time

from collections import abc
from keyword import iskeyword

from notify import Notification


URL = "http://np.radioplayer.co.uk/qp/v3/onair?rpIds=340&nameSize=200&artistNameSize=200&descriptionSize=200"

logger = logging.getLogger(__name__)


class FrozenJson:
    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            if iskeyword(key):
                key += "_"
            elif str(key).isnumeric():
                key = "_" + key
            self.__data[key] = value

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return FrozenJson.build(self.__data[name])

    def __repr__(self):
        return "FrozenJson(%r)" % (self.__data)

    @classmethod
    def build(cls, obj):

        if isinstance(obj, abc.Mapping):
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj


def get_data(url):
    try:
        resp = requests.get(url)
        data = json.loads(resp.text[9:-1])
        return data
    except (requests.exceptions.RequestException, json.JSONDecodeError) as exc:
        logger.debug(exc)


def run():
    try:
        data = FrozenJson(get_data(URL))
        objs = []
        if data.results._340:
            for obj in data.results._340:
                objs.append(obj)
            service = objs[-1].serviceName
            artist = objs[-1].artistName
            song = objs[-1].name
            return service, artist, song
    except Exception as exc:
        logger.debug(exc)
        return "(*_*)", "(*_*)", "(*_*)"
