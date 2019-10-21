from ehelply_bootstrapper.utils.connection_details import ConnectionDetails


class Driver:
    def __init__(self, connection_details: ConnectionDetails = None, dev_mode: bool = False, verbose: bool = False):
        self.connection_details = connection_details
        self.dev_mode = dev_mode
        self.verbose = verbose
        self.instance = None

    def init(self):
        if self.dev_mode:
            self.setup_dev()
            self.test()
        else:
            self.setup()

        return self

    def setup(self):
        pass

    def setup_dev(self):
        self.setup()

    def test(self):
        pass
