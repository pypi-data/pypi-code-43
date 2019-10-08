class DataloaderManager(object):

    def _init(self):
        raise NotImplementedError

    def get_train_dl(self, phase='train'):
        raise NotImplementedError

    def get_dl(self, phase='valid'):
        raise NotImplementedError

    def get_valid_dl(self, phase='valid'):
        raise NotImplementedError

    def get_test_dl(self, phase='test'):
        raise NotImplementedError
