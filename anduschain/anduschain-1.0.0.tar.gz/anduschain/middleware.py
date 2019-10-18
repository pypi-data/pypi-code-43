from eth_account import (
    Account,
)
from eth_utils.toolz import (
    compose,
)
from web3._utils.rpc_abi import (
    apply_abi_formatters_to_dict,
)
from web3._utils.transactions import (
    fill_nonce,
    fill_transaction_defaults,
)
from web3.middleware.abi import (
    STANDARD_NORMALIZERS
)
from web3.middleware.signing import (
    gen_normalized_accounts
)
from eth_utils.toolz import (
    assoc,
    curry,
    merge,
)
from .singners import (
    sign_transaction
)


TRANSACTION_PARAMS_ABIS = {
    'type': 'uint',
    'data': 'bytes',
    'from': 'address',
    'gas': 'uint',
    'gasPrice': 'uint',
    'nonce': 'uint',
    'to': 'address',
    'value': 'uint',
}

TRANSACTION_DEFAULTS = {
    'type': 0,
    'value': 0,
    'data': b'',
    'gas': lambda web3, tx: web3.eth.estimateGas(tx),
    'gasPrice': 23809523805524,
    # 'chainId': lambda web3, tx: web3.net.version,
}

@curry
def fill_nonce(web3, transaction):
    if 'from' in transaction and 'nonce' not in transaction:
        return assoc(
            transaction,
            'nonce',
            web3.eth.getTransactionCount(
                transaction['from'],
                block_identifier='pending'))
    else:
        return transaction


@curry
def fill_transaction_defaults(web3, transaction):
    """
    if web3 is None, fill as much as possible while offline
    """
    defaults = {}
    for key, default_getter in TRANSACTION_DEFAULTS.items():
        if key not in transaction:
            if callable(default_getter):
                if web3 is not None:
                    default_val = default_getter(web3, transaction)
                else:
                    raise ValueError("You must specify %s in the transaction" % key)
            else:
                default_val = default_getter
            defaults[key] = default_val
    return merge(defaults, transaction)


def format_transaction(transaction):
    """Format transaction so that it can be used correctly in the signing middleware.

    Converts bytes to hex strings and other types that can be passed to the underlying layers.
    Also has the effect of normalizing 'from' for easier comparisons.
    """
    return apply_abi_formatters_to_dict(STANDARD_NORMALIZERS, TRANSACTION_PARAMS_ABIS, transaction)


def construct_sign_and_send_raw_middleware(private_key_or_account):
    """Capture transactions sign and send as raw transactions
    Keyword arguments:
    private_key_or_account -- A single private key or a tuple,
    list or set of private keys. Keys can be any of the following formats:
      - An eth_account.LocalAccount object
      - An eth_keys.PrivateKey object
      - A raw private key as a hex string or byte string
    """

    accounts = gen_normalized_accounts(private_key_or_account)

    def sign_and_send_raw_middleware(make_request, w3):
        format_and_fill_tx = compose(
            format_transaction,
            fill_transaction_defaults(w3),
            fill_nonce(w3))

        def middleware(method, params):
            if method != "eth_sendTransaction":
                return make_request(method, params)
            else:
                transaction = format_and_fill_tx(params[0])

            if 'from' not in transaction:
                return make_request(method, params)
            elif transaction.get('from') not in accounts:
                return make_request(method, params)

            account = accounts[transaction['from']]
            raw_tx = sign_transaction(account, transaction).rawTransaction
            return make_request(
                "eth_sendRawTransaction",
                [raw_tx])

        return middleware

    return sign_and_send_raw_middleware
