import os


class Counter:

    def __init__(self, **options):
        self.path = options.get('path', '.')
        self.count = options.get('count', True)
        self.size = options.get('size', False)
    
    def call(self):
        if self.count:
            return self.count(self.path)
        if self.size:
            return self.get_sizes(self.path)

    def count(self, path):
        return len(os.listdir(path))
    
    def get_sizes(self, path):
        raise Exception('This feature has not been implemented yet.')
