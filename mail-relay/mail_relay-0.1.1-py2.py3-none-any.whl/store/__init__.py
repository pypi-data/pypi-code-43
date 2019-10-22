import os


DEFAULT_STORE_PATH = os.path.abspath(os.path.join(os.getcwd(), 'relay.sqlite'))

class Store(object):
    def __init__(self, path, version):
        self.path = path
        self.version = version

    # TODO: internalize handlers, easening store_path provision from consumers
