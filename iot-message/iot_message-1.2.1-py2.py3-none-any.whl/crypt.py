from Crypto.Cipher import AES
from Crypto.Hash import SHA, HMAC
import binascii
from Crypto import Random


staticiv = 'abcdef2345678901'
ivkey = '2345678901abcdef'
datakey ='0123456789abcdef'
passphrase = 'mypassphrase'


def decrypt(iv_encoded, data_encoded, _hash):
    encrypted_iv = binascii.unhexlify(iv_encoded)
    encrypted_data = binascii.unhexlify(data_encoded)

    iv_suite = AES.new(ivkey.encode(), AES.MODE_CBC, staticiv.encode())
    iv = iv_suite.decrypt(encrypted_iv)
    data_suite = AES.new(datakey.encode(), AES.MODE_CBC, iv)

    sensordata = data_suite.decrypt(encrypted_data).strip(b'\x00').decode('utf8')

    print("data |" +sensordata + "|")

    fullmessage = iv.decode('utf8') + sensordata
    hmac = HMAC.new(passphrase.encode(), fullmessage.encode(), SHA)
    computed_hash = hmac.hexdigest()

    try:
        hmac.verify(binascii.unhexlify(_hash))
    except Exception as e:
        print("hash?", computed_hash)
        print("!!!!!!!!!!!!!!!!!!", e)


def encrypt(ptext):
    text = _pad(16, ptext)
    iv = Random.new().read(AES.block_size)
    iv = binascii.hexlify(iv)[:16]
    print("iv ", iv)
    iv_suite = AES.new(ivkey.encode(), AES.MODE_CBC, staticiv.encode())
    encrypted_iv = iv_suite.encrypt(iv)

    data_suite = AES.new(datakey.encode(), AES.MODE_CBC, iv)
    encrypted_data = data_suite.encrypt(text.encode())

    fullmessage = iv.decode('utf8') + ptext
    hmac = HMAC.new(passphrase.encode(), fullmessage.encode(), SHA)
    computed_hash = hmac.hexdigest()

    return [
        binascii.hexlify(encrypted_iv),
        binascii.hexlify(encrypted_data),
        computed_hash
    ]


def _pad(l, s):
    return s + (l - len(s) % l) * chr(00)

q = encrypt("hello world")
print(q)
decrypt(*q)
print("------------------")
decrypt(
    "e85a45678c569c4d8a1f08fb04d1ff92",
    "4f72f7116f70e54f00a94f024e9d1f8a96014c645df691b4ed2234cf0975d40d",
    "3e4fb9422beee8391d66ff7b26555a0a8a1c4d14"
)

# print(encrypt("hello"))
