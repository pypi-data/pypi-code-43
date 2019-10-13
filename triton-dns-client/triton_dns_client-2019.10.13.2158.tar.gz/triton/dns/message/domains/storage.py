class DomainStorage:
    pass

    def __init__(self):
        self.storage = []

    def append(self, domain):
        self.storage.append(domain)

    def find(self, label):
        for x in self.storage:
            if x.label == label:
                return x
        return None

    def find_pos(self, pos):
        for x in self.storage:
            if x.pos == pos:
                return x
        return None

    def purge(self):
        self.storage = []
