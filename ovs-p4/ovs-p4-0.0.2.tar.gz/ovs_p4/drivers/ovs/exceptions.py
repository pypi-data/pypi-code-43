
class LoadFilterProgException(Exception):

    def __init__(self, error):
        super(LoadFilterProgException, self).__init__()
        self.message = "LoadFilterProgException: %s" % error
