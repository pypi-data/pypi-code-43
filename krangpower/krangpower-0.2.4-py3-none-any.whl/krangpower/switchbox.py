class SwitchBox(dict):

    def __init__(self):
        super().__init__()
        self.links = dict()

    def __setitem__(self, key, value):
        if key not in self.keys():
            raise KeyError('Add the switch first')

        super().__setitem__(key, bool(value))

        if bool(value) == False:
            for k in self.links[key]['under']:
                self[k] = False
        else:
            for k in self.links[key]['over']:
                self[k] = True

    def _check_keys(self, key1, key2):
        try:
            self.get(key1)
            self.get(key2)
        except KeyError:
            raise KeyError

    def add(self, key):
        if key not in self.links.keys():
            super().__setitem__(key, None)
            self.links[key] = {'under': set(),
                               'over': set()}
        else:
            raise KeyError('Switch already present')

    def link_2under1(self, key1, key2, hard=True):
        self._check_keys(key1, key2)
        self.links[key1]['under'].add(key2)
        if hard:
            self.links[key2]['over'].add(key1)

    def link_2over1(self, key1, key2, hard=True):
        """when key1 becomes True, key2 becomes True.
        IF HARD, when key2 becomes False, key1 becomes False.

        1 ---> 2;
        IF HARD, NOT 2 ---> NOT 1

                ...KEY2
              KEY1'''

        """
        self._check_keys(key1, key2)
        self.links[key1]['over'].add(key2)
        if hard:
            self.links[key2]['under'].add(key1)

    def link_total(self, key1, key2, hard=True):
        self.link_2over1(key1, key2, hard=hard)
        self.link_2under1(key1, key2, hard=hard)