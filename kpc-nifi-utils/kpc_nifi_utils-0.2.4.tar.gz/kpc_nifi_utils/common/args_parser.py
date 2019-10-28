import argparse

from kpc_nifi_utils.common.singleton import singleton


class Args:
    def __init__(self, *args):
        self._wrapper = ArgumentParserWrapper()
        for arg in args:
            if isinstance(arg, str):
                self._wrapper.add('--{}'.format(arg), type=str)

    def add(self, *args, **kwargs):
        if self._wrapper.is_parse():
            raise ValueError("Can not add args config when parser is already initiate")

        self._wrapper.add(*args, **kwargs)
        return self

    def get(self, key):
        if not self._wrapper.is_parse():
            raise ValueError(
                "Can not get args value because parser not initiate, calling initiate() and then try again")

        try:
            return vars(self._wrapper.get_args()).get(key, None)
        except Exception as e:
            print(e)

    def initiate(self):
        self._wrapper.parse()
        return self

    def print_help(self):
        print(self._wrapper.print_help())


@singleton
class ArgumentParserWrapper:
    def __init__(self):
        self._args = None
        self._parser = argparse.ArgumentParser()
        self._is_parse = False

    def add(self, *args, **kwargs):
        self._parser.add_argument(*args, **kwargs)
        return self

    def get_args(self):
        return self._args

    def parse(self):
        self._args = self._parser.parse_args()
        self._is_parse = True
        return self

    def is_parse(self):
        return self._is_parse

    def print_help(self):
        print(self._parser.format_help())
