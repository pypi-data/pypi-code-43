class Batch:
    def __init__(self, batch_size: int = 16):
        self.batch_size: int = batch_size
        self.batch: list = []

    def get(self) -> list:
        return self.batch

    def _insert(self, item) -> bool:
        if self.size() == self.batch_size:
            return False
        self.batch.append(item)
        return True

    def size(self) -> int:
        return len(self.batch)

    def capacity(self) -> int:
        return self.batch_size - self.size()

    def _clear(self):
        self.batch = []
