class KeyModifier:

    def __init__(self, key_name):
        self._key_name = key_name

    def __call__(self, obj):
        return obj[self._key_name]


class KeysModifier:

    def __init__(self, key_names):
        self._key_names = key_names

    def __call__(self, obj):
        return tuple(obj[key_name] for key_name in self._key_names)