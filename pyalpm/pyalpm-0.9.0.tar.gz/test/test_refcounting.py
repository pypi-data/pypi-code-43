from gc import collect
from conftest import real_handle

def get_transaction():
    return real_handle.init_transaction()

def test_transaction_object():
    transaction = get_transaction()
    collect()
    transaction.prepare()
