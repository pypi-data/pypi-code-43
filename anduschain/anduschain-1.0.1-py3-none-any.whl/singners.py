from collections import (
    Mapping,
)
from eth_account._utils.signing import (
    sign_transaction_hash
)
from cytoolz import (
    dissoc,
    merge,
    partial,
    identity,
    pipe,
)
from eth_utils.curried import (
    keccak,
)
from eth_account.datastructures import (
    AttributeDict,
)
from hexbytes import (
    HexBytes,
)
from eth_account._utils.transactions import (
    chain_id_to_v,
    is_none,
    is_int_or_prefixed_hexstr,
    is_empty_or_checksum_address
)
from eth_rlp import (
    HashableRLP,
)
from eth_utils.curried import (
    apply_formatters_to_dict,
    apply_one_of_formatters,
    hexstr_if_str,
    is_bytes,
    is_string,
    to_bytes,
    to_int,
)
import rlp
from rlp.sedes import (
    Binary,
    big_endian_int,
    binary,
)

TRANSACTION_FORMATTERS = {
    'type': hexstr_if_str(to_int),
    'nonce': hexstr_if_str(to_int),
    'gasPrice': hexstr_if_str(to_int),
    'gas': hexstr_if_str(to_int),
    'to': apply_one_of_formatters((
        (is_string, hexstr_if_str(to_bytes)),
        (is_bytes, identity),
        (is_none, lambda val: b''),
    )),
    'value': hexstr_if_str(to_int),
    'data': hexstr_if_str(to_bytes),
    'v': hexstr_if_str(to_int),
    'r': hexstr_if_str(to_int),
    's': hexstr_if_str(to_int),
}

UNSIGNED_TRANSACTION_FIELDS = (
    ('type', big_endian_int),
    ('nonce', big_endian_int),
    ('gasPrice', big_endian_int),
    ('gas', big_endian_int),
    ('to', Binary.fixed_length(20, allow_empty=True)),
    ('value', big_endian_int),
    ('data', binary),
)

TRANSACTION_VALID_VALUES = {
    'type': is_int_or_prefixed_hexstr,
    'nonce': is_int_or_prefixed_hexstr,
    'gasPrice': is_int_or_prefixed_hexstr,
    'gas': is_int_or_prefixed_hexstr,
    'to': is_empty_or_checksum_address,
    'value': is_int_or_prefixed_hexstr,
    'data': lambda val: isinstance(val, (int, str, bytes, bytearray)),
    'chainId': lambda val: val is None or is_int_or_prefixed_hexstr(val),
}

ALLOWED_TRANSACTION_KEYS = {
    'type',
    'nonce',
    'gasPrice',
    'gas',
    'to',
    'value',
    'data',
    'chainId',  # set chainId to None if you want a transaction that can be replayed across networks
}

TRANSACTION_DEFAULTS = {
    'type': 0,
    'to': b'',
    'value': 0,
    'data': b'',
    'chainId': None,
}

class Transaction(HashableRLP):
    fields = UNSIGNED_TRANSACTION_FIELDS + (
        ('v', big_endian_int),
        ('r', big_endian_int),
        ('s', big_endian_int),
    )

class UnsignedTransaction(HashableRLP):
    fields = UNSIGNED_TRANSACTION_FIELDS

REQUIRED_TRANSACITON_KEYS = ALLOWED_TRANSACTION_KEYS.difference(TRANSACTION_DEFAULTS.keys())

def assert_valid_fields(transaction_dict):
    # check if any keys are missing
    missing_keys = REQUIRED_TRANSACITON_KEYS.difference(transaction_dict.keys())
    if missing_keys:
        raise TypeError("Transaction must include these fields: %r" % missing_keys)

    # check if any extra keys were specified
    superfluous_keys = set(transaction_dict.keys()).difference(ALLOWED_TRANSACTION_KEYS)
    if superfluous_keys:
        raise TypeError("Transaction must not include unrecognized fields: %r" % superfluous_keys)

    # check for valid types in each field
    valid_fields = apply_formatters_to_dict(TRANSACTION_VALID_VALUES, transaction_dict)
    if not all(valid_fields.values()):
        invalid = {key: transaction_dict[key] for key, valid in valid_fields.items() if not valid}
        raise TypeError("Transaction had invalid fields: %r" % invalid)

def serializable_unsigned_transaction_from_dict(transaction_dict):
    assert_valid_fields(transaction_dict)
    filled_transaction = pipe(
        transaction_dict,
        dict,
        partial(merge, TRANSACTION_DEFAULTS),
        chain_id_to_v,
        apply_formatters_to_dict(TRANSACTION_FORMATTERS),
    )

    if 'v' in filled_transaction:
        serializer = Transaction
    else:
        serializer = UnsignedTransaction

    return serializer.from_dict(filled_transaction)

def encode_transaction(unsigned_transaction, vrs):
    (v, r, s) = vrs
    chain_naive_transaction = dissoc(unsigned_transaction.as_dict(), 'v', 'r', 's')
    signed_transaction = Transaction(v=v, r=r, s=s, **chain_naive_transaction)
    return rlp.encode(signed_transaction)

def sign_transaction_dict(eth_key, transaction_dict):
    # generate RLP-serializable transaction, with defaults filled
    unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction_dict)
    transaction_hash = unsigned_transaction.hash()

    # detect chain
    if isinstance(unsigned_transaction, UnsignedTransaction):
        chain_id = None
    else:
        chain_id = unsigned_transaction.v

    # sign with private key
    (v, r, s) = sign_transaction_hash(eth_key, transaction_hash, chain_id)

    # serialize transaction with rlp
    encoded_transaction = encode_transaction(unsigned_transaction, vrs=(v, r, s))

    return (v, r, s, encoded_transaction)

def sign_transaction(account, transaction_dict):
    if not isinstance(transaction_dict, Mapping):
        raise TypeError("transaction_dict must be dict-like, got %r" % transaction_dict)

    # allow from field, *only* if it matches the private key
    if 'from' in transaction_dict:
        if transaction_dict['from'] == account.address:
            sanitized_transaction = dissoc(transaction_dict, 'from')
        else:
            raise TypeError("from field must match key's %s, but it was %s" % (
                account.address,
                transaction_dict['from'],
            ))
    else:
        sanitized_transaction = transaction_dict

    # sign transaction
    (
        v,
        r,
        s,
        rlp_encoded,
    ) = sign_transaction_dict(account._key_obj, sanitized_transaction)

    transaction_hash = keccak(rlp_encoded)

    return AttributeDict({
        'rawTransaction': HexBytes(rlp_encoded),
        'hash': HexBytes(transaction_hash),
        'r': r,
        's': s,
        'v': v,
    })
