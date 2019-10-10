class ContextData(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data = {}

    def _find_and_set(self, key, value, d=None):
        if d is None:
            d = self._data

        parts = key.split('/')
        first_part = parts[0]

        if len(parts) < 2:
            d[first_part] = value
            return

        if first_part not in d:
            d[first_part] = {}

        return self._find_and_set("/".join(parts[1:]), value, d[first_part])

    def flat(self):
        for key, value in self.items():
            self._find_and_set(key, value)

        return self._data
