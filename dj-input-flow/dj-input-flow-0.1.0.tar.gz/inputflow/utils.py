from collections import OrderedDict


class Utils:
    @staticmethod
    def write_to_dict(dictionary, path, value):
        dictionary[path] = value
