import uuid

class UUIDSerializer:
    def serialize(self, value):
        return str(value) if value is not None else None

    def deserialize(self, value):
        return None if value is None else uuid.UUID(value)
