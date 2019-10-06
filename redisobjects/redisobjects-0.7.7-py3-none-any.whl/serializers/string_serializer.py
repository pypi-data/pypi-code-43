class StringSerializer:
    def serialize(self, s):
        return s.encode() if s is not None else None

    def deserialize(self, value):
        return value if value is None else value.decode()
