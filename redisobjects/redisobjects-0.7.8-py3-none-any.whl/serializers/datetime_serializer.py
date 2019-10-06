from datetime import datetime

class DateTimeSerializer:
    def serialize(self, dt):
        return None if dt is None else dt.timestamp()

    def deserialize(self, value):
        return None if value is None else datetime.fromtimestamp(value)
