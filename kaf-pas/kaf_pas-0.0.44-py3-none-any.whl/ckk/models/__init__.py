def get_operations_from_trunsaction(data):
    transaction = data.get('transaction')
    if isinstance(transaction, dict):
        return transaction.get('operations')
    else:
        return None
