from uuid import UUID

import pytest

from azureml.studio.common.credential import CredentialDescriptor, Cipher


def test_illegal_input_will_raise():
    with pytest.raises(ValueError):
        CredentialDescriptor.parse_from_str('')
    with pytest.raises(ValueError):
        CredentialDescriptor.parse_from_str('only_key')


def test_single_key_parts():
    obj = CredentialDescriptor.parse_from_str('key,value1')
    assert obj.credential_type == 'key'
    assert len(obj.credential_key_parts) == 1
    assert obj.credential_key_parts[0] == 'value1'


def test_multiple_key_parts():
    obj = CredentialDescriptor.parse_from_str('key,value1,value2,value3')
    assert obj.credential_type == 'key'
    assert len(obj.credential_key_parts) == 3
    assert obj.credential_key_parts[0] == 'value1'
    assert obj.credential_key_parts[1] == 'value2'
    assert obj.credential_key_parts[2] == 'value3'


@pytest.mark.parametrize('cipher_text, plain_text', [
    ("2clcUKGYLeI6H+RF7cYNaQ==", ""),
    ("4MLU6axzmhr0oD7lDEottg==", "h"),
    ("cWR9vLfO0WYUGPbT6R85Og==", "hello world"),
    ("67spdAVIR2XafIfa6Ih/Zw==", "hello world 12"),
    ("vCSJ0epx2XKgmJR/l5x2pQ==", "123456789abcdef"),
    ("TROeXH3xgH6Z1QLEFhsqfk1t8ecKxMhdCpj2scEFieo=", "0123456789abcdef"),
])
def test_decrypt(cipher_text, plain_text):
    uuid = UUID('4e1b0fe6aded4b3fa36f39b8862b9004')
    c = Cipher(uuid)

    decrypted = c.decrypt(cipher_text)
    assert decrypted == plain_text
