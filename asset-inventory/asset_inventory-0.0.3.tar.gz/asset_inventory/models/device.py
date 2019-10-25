class Device:

    components = [
        'name',
        'size',
        'label',
        'uuid',
        'vendor',
        'ids',
        'model',
        'host',
        'partitions'
    ]

    def __init__(self, **kwargs):
        self.__dict__.update((key, None) for key in self.components)
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in self.components)

    def serialize(self):
        return {component: value for component, value in self.__dict__.items()}
