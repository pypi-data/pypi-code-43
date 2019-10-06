import json

class JsonSerializer:
    def __init__(self, *, sort_keys=False):
        self.sort_keys = sort_keys

    def serialize(self, value):
        return json.dumps(value, sort_keys=self.sort_keys)

    def deserialize(self, value):
        return json.loads(value)
