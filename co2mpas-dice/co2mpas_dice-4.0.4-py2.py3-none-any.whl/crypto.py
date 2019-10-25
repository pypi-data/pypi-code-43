import io
import os
import zlib
import yaml
import json
import tarfile
import itertools
import os.path as osp
import schedula as sh


def load_RSA_keys(server_RSA_keys_path, passwords=None):
    """
    Loads the server RSA keys.

    :param server_RSA_keys_path:
        File path of server RSA keys.
    :type server_RSA_keys_path: str

    :param passwords:
        RSA keys passwords.
    :type passwords: dict

    :return:
        RSA keys.
    :rtype: dict
    """
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    keys, passwords = {}, passwords or {}
    with tarfile.open(server_RSA_keys_path, 'r') as tar:
        it = itertools.product(('public', 'private'), ('secret', 'server'))
        for i, j in it:
            try:
                with tar.extractfile(tar.getmember('%s/%s.pem' % (j, i))) as f:
                    if i == 'public':
                        key = serialization.load_pem_public_key(
                            f.read(), default_backend()
                        )
                    else:
                        key = serialization.load_pem_private_key(
                            f.read(), passwords.get(j), default_backend()
                        )
                    sh.get_nested_dicts(keys, i)[j] = key
            except (KeyError, ValueError, TypeError):
                pass
    return keys


def format_public_RSA_key(key):
    from cryptography.hazmat.primitives import serialization
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()


def get_RSA_keys():
    from co2mpas_dice.server.config import conf, _get_path
    p = {'server': conf['key']['password'].encode()}
    return load_RSA_keys(_get_path('server.co2mpas.keys', dir='keys'), p)


def make_hash(*data):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    for v in data:
        digest.update(v)
    return digest.finalize()


def _json_default(o):
    import lmfit
    import numpy as np

    if isinstance(o, np.ndarray):
        return {'__numpy__': o.tolist()}
    elif isinstance(o, np.generic):
        return o.item()
    elif isinstance(o, lmfit.Parameter):
        return {'__parameter__': o.__getstate__()}
    elif isinstance(o, bytes):
        return {'__bytes__': str(o)}
    raise TypeError("Object of type '%s' is not JSON serializable" %
                    o.__class__.__name__)


def _json_object_hook(dct):
    import lmfit
    import numpy as np
    if '__numpy__' in dct:
        return np.array(dct['__numpy__'])
    elif '__parameter__' in dct:
        _par = lmfit.Parameter()
        _par.__setstate__(dct['__parameter__'])
        return _par
    elif '__bytes__' in dct:
        return eval(dct['__bytes__'])
    return dct


def sign_data(key, *data):
    import json
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import utils
    from cryptography.hazmat.primitives.asymmetric import padding

    message = json.dumps(data, default=_json_default, sort_keys=True).encode()
    message = make_hash(message)
    return key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        utils.Prehashed(hashes.SHA256())
    ), message


def define_rsa_padding():
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )


def rsa_encrypt(rsa, plaintext):
    return rsa.encrypt(plaintext, define_rsa_padding())


def rsa_decrypt(rsa, plaintext):
    return rsa.decrypt(plaintext, define_rsa_padding())


def aes_cipher(key, iv, tag=None):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    return Cipher(algorithms.AES(key), modes.GCM(iv, tag), default_backend())


def aes_encrypt(plaintext, associated_data):
    # Generate a random 96-bit IV and 256-bit key.
    iv, key = os.urandom(12), os.urandom(32)
    encryptor = aes_cipher(key, iv).encryptor()

    # associated_data will be authenticated but not encrypted,
    # it must also be passed in on decryption.
    encryptor.authenticate_additional_data(associated_data)

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    data = encryptor.update(plaintext) + encryptor.finalize()

    return {'key': key, 'iv': iv, 'tag': encryptor.tag}, data


def verify_AES_key(private_RSA_keys, verify, encrypted):
    try:
        verify = rsa_decrypt(private_RSA_keys['server'], verify)
        return make_hash(encrypted['key'], encrypted['data']) == verify
    except ValueError:  # Wrong keys!
        return False


def random_password(size=64, chars=None):
    import random
    import string
    if not chars:
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    choice = random.SystemRandom().choice
    return ''.join(choice(chars) for _ in range(size))


def generate_keys(key_folder, passwords=None):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    keys = {'private': {}, 'public': {}}
    if passwords is None:
        passwords = dict(secret=random_password(), server=random_password())

    for k, p in sorted(passwords.items()):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        if p is None:
            encryption_alg = serialization.NoEncryption()
        else:
            encryption_alg = serialization.BestAvailableEncryption(p.encode())

        keys['private'][k] = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_alg
        )

        keys['public'][k] = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    it = (
        ('dice.co2mpas.keys', (('public', 'secret'), ('public', 'server'))),
        ('server.co2mpas.keys',
         (('public', 'secret'), ('public', 'server'), ('private', 'server'))),
        ('secret.co2mpas.keys',
         (itertools.product(('public', 'private'), ('secret', 'server'))))
    )

    for fpath, v in it:
        with tarfile.open(osp.join(key_folder, fpath), 'w') as tar:
            for k in v:
                obj = sh.get_nested_dicts(keys, *k)
                info = tarfile.TarInfo('%s.pem' % '/'.join(k[::-1]))
                info.size = len(obj)
                tar.addfile(info, io.BytesIO(obj))

    with open(osp.join(key_folder, 'secret.passwords'), 'w') as f:
        json.dump(passwords, f)

    with open(osp.join(key_folder, 'server.password'), 'w') as f:
        json.dump(passwords['server'], f)


def generate_sing_key(sign_key, password=None):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    if password is None:
        encrypt_alg = serialization.NoEncryption()
    else:
        encrypt_alg = serialization.BestAvailableEncryption(password.encode())

    key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encrypt_alg
    ).decode()
    os.makedirs(osp.dirname(sign_key), exist_ok=True)
    with open(sign_key, 'w') as file:
        json.dump({'key': key, 'password': password}, file, sort_keys=1)


def load_sign_key(sign_key, password=None):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    if password is None:
        password = os.environ.get('SIGN_KEY_PASSWORD', 'co2mpas') or None

    if not osp.isfile(sign_key):
        generate_sing_key(sign_key, password)

    with open(sign_key) as file:
        d = json.load(file)
    password = d.get('password', password)

    if isinstance(password, str):
        password = password.encode()

    return serialization.load_pem_private_key(
        d['key'].encode(), password, default_backend()
    )


def sign_ta_id(ta_id, sign_key, password=None):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import utils
    from cryptography.hazmat.primitives.asymmetric import padding

    key = load_sign_key(sign_key, password)

    ta_id.pop('signature', None)
    ta_id['pub_sign_key'] = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    message = json.dumps(ta_id, default=_json_default, sort_keys=True).encode()
    ta_id['signature'] = key.sign(
        make_hash(message),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        utils.Prehashed(hashes.SHA256())
    )
    return ta_id


def define_associated_data(public_RSA_keys):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    for k in ('secret', 'server'):
        digest.update(public_RSA_keys[k].public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    return digest.finalize()


def encrypt_data(data, path_keys):
    rsa = load_RSA_keys(path_keys)['public']
    plaintext = zlib.compress(yaml.dump(data, Dumper=yaml.CDumper).encode())
    key, data = aes_encrypt(plaintext, define_associated_data(rsa))
    key = rsa_encrypt(rsa['secret'], yaml.dump(
        key, Dumper=yaml.CDumper
    ).encode())
    verify = rsa_encrypt(rsa['server'], make_hash(key, data))
    return {'verify': verify, 'encrypted': {'key': key, 'data': data}}


def aes_decrypt(data, associated_data, key, iv, tag):
    decryptor = aes_cipher(key, iv, tag).decryptor()

    # We put associated_data back in or the tag will fail to verify
    # when we finalize the decryptor.
    decryptor.authenticate_additional_data(associated_data)

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    return decryptor.update(data) + decryptor.finalize()


def decrypt_data(encrypted_data, path_keys, passwords=None):
    verify, encrypted = encrypted_data['verify'], encrypted_data['encrypted']

    rsa = load_RSA_keys(path_keys, passwords)['private']
    assert verify_AES_key(rsa, verify, encrypted)
    kw = yaml.load(
        rsa_decrypt(rsa['secret'], encrypted['key']), Loader=yaml.CLoader
    )
    ad = define_associated_data({k: v.public_key() for k, v in rsa.items()})
    return yaml.load(
        zlib.decompress(
            aes_decrypt(encrypted['data'], ad, **kw)), Loader=yaml.CLoader
    )
