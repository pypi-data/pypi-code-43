import json

class JsonSerializer:
    def serialize(self, value):
        return json.dumps(value)

    def deserialize(self, value):
        return json.loads(value)
