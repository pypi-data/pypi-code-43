import json
import sys

from kpc_nifi_utils.common.singleton import singleton


@singleton
class Command:
    def send(self, *args, **kwargs):
        print(*args, file=sys.stdout, **kwargs)

    def receive(self):
        try:
            return json.load(sys.stdin)
        except Exception as e:
            print(e)
            return None


class Sender:
    def __init__(self):
        self._command = Command()
        self._config = {}
        self._data = {}

    def config_set(self, key, value):
        self._config[key] = value
        return self

    def data_set(self, key, value):
        self._data[key] = value
        return self

    def configs_set(self, config: dict):
        self._config.update(config)
        return self

    def datum_set(self, datum: dict):
        self._data.update(datum)
        return self

    def send(self):
        self._command.send(self.__str__())

    def __str__(self):
        return json.dumps({'config': self._config, 'data': self._data})


class Receiver:
    def __init__(self):
        self._command = Command()
        self._config = None
        self._data = None
        self._receiver = None

    def receive(self):
        self._receiver = Command().receive()

        try:
            self._config = self._receiver['config']
        except Exception as e:
            print(e)

        try:
            self._data = self._receiver['data']
        except Exception as e:
            print(e)

    def config_get(self):
        if self._config is not None:
            return self._config

        return None

    def config_get_by_key(self, key):
        if self._config is not None:
            try:
                return self._config[key]
            except Exception as e:
                print(e)
                return None

    def data_get(self):
        if self._data is not None:
            return self._data

        return None

    def data_get_by_key(self, key):
        if self._data is not None:
            try:
                return self._data[key]
            except Exception as e:
                print(e)
                return None

    def receiver_get(self):
        if self._receiver is not None:
            return self._receiver

        return None

    def receiver_get_by_key(self, key):
        if self._receiver is not None:
            try:
                return self._receiver[key]
            except Exception as e:
                print(e)
                return None
