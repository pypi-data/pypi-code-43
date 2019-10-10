__all__ = ['Transaction', 'CreateTransactionException']


class CreateTransactionException(Exception):
    pass


class Transaction:
    def __init__(self, db: 'DB'):
        self.db = db

    def __enter__(self):
        pass

    def close(self, rollback=False):
        self.db.close_transaction(rollback)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_type is not None)
