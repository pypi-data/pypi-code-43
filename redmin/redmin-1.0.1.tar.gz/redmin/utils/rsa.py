import base64

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5


def generate_public_private_key():
    rsa = RSA.generate(2048, Random.new().read)
    private_key = rsa.exportKey()
    public_key = rsa.publickey().exportKey()
    return private_key, public_key


def encrypt(message, public_key):
    rsakey = RSA.importKey(public_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(bytes(message.encode("utf8"))))
    return cipher_text


def decrypt(cipher_text, private_key):
    rsakey = RSA.importKey(private_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    sentinel = {}
    text = cipher.decrypt(base64.b64decode(cipher_text), sentinel=sentinel)
    return str(text, "utf8")


def sign(message, private_key):
    rsakey = RSA.importKey(private_key)
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(message.encode("utf8"))
    signature = base64.b64encode(signer.sign(digest))
    return signature


def verify_sign(message, signature, public_key):
    rsakey = RSA.importKey(public_key)
    verifier = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(message.encode("utf8"))
    return verifier.verify(digest, base64.b64decode(signature))


def main():
    with open(r'D:\app\luo-video\key\priv.pem', 'rb+') as f:
        private_key = f.read()

    with open(r'D:\app\luo-video\key\pub.pem', 'rb+') as f:
        public_key = f.read()

    message = "hpPEbBjenqRrNTQwvErznOBf5DbPKubi"
    cipher = Cipher_pkcs1_v1_5.new(RSA.importKey(public_key))
    cipher_text = cipher.encrypt(bytes(message.encode("utf8")))
    result = cipher_text.hex()
    print("加密后:", result)

    cipher = Cipher_pkcs1_v1_5.new(RSA.importKey(private_key))
    print("解密数据:", cipher.decrypt(bytes.fromhex(result), {}))
    with open(r'/tmp/code.txt', 'w') as f:
        f.write(result)

    with open(r'/tmp/code.txt', 'r') as f:
        file_content = f.read()

    print("解密数据载入的数据:", cipher.decrypt(bytes.fromhex(file_content), {}))

    with open(r'D:\app\luo-video\tmp\3a6ca2557344d16951c3457fde2035c46704fff41b4e2d4dd21db8e133da0385.key', 'r') as f:
        code = f.read()

    print("载入数据:", code)
    print("解密载入的数据:", cipher.decrypt(bytes.fromhex(code), {}))


if __name__ == "__main__":
    main()
