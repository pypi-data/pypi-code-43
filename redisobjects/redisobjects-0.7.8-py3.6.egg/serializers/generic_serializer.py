class GenericSerializer:
    def __init__(self, mapping_function):
        self.mapping_function = mapping_function

    def serialize(self, value):
        return str(value)

    def deserialize(self, value):
        return self.mapping_function(value)
