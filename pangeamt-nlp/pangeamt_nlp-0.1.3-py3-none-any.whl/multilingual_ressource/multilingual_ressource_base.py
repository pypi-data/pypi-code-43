class MultilingualRessourceBase:
    def __init__(self):
        self._num_tus = None

    def read(self, reader):
        cls = self.__class__
        raise ValueError(f'`{cls}` sould implement a read method')

    def get_num_tus(self):
        return self._num_tus

