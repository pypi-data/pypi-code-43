# -*- coding: utf-8 -*-
"""
Copyright (c) 2018 beyond-blockchain.org.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys
import os
import platform

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography import x509
import cryptography

current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, "../.."))


def _convert_binary_to_bigint(bindat):
    bn = BACKEND_KP.private_key_obj._backend._ffi.NULL
    bn_ptr = BACKEND_KP.private_key_obj._backend._lib.BN_bin2bn(bindat, len(bindat), bn)
    return BACKEND_KP.private_key_obj._backend._bn_to_int(bn_ptr)


class KeyType:
    NOT_INITIALIZED = 0
    ECDSA_SECP256k1 = 1
    ECDSA_P256v1 = 2


class KeyPairPy:
    POINT_CONVERSION_COMPRESSED = 2     # same as enum point_conversion_form_t in openssl/crypto/ec.h
    POINT_CONVERSION_UNCOMPRESSED = 4   # same as enum point_conversion_form_t in openssl/crypto/ec.h

    """Key pair container"""
    def __init__(self, curvetype=KeyType.ECDSA_P256v1, compression=False, privkey=None, pubkey=None):
        self.curvetype = curvetype
        self.private_key_len = None
        self.private_key = None

        self.private_key_obj = None
        self.public_key_obj = None
        self.public_key_len = None
        self.public_key = None
        if compression:
            self.key_compression = KeyPairPy.POINT_CONVERSION_COMPRESSED
        else:
            self.key_compression = KeyPairPy.POINT_CONVERSION_UNCOMPRESSED

        if privkey is not None:
            self.mk_keyobj_from_private_key(privkey)
        if pubkey is not None:
            self._mk_keyobj_from_public_key(pubkey)
            self.public_key_len = len(pubkey)
            self.public_key = pubkey

    def _get_naive_private_key_bytes(self):
        if self.private_key_obj is None:
            return
        if self.private_key_obj.curve.name == ec.SECP256R1().name:
            self.curvetype = KeyType.ECDSA_P256v1
        elif self.private_key_obj.curve.name == ec.SECP256K1().name:
            self.curvetype = KeyType.ECDSA_SECP256k1
        else:
            return
        bn = self.private_key_obj._backend._lib.EC_KEY_get0_private_key(self.private_key_obj._ec_key)
        bn_num_bytes = self.private_key_obj._backend._lib.BN_num_bytes(bn)
        bin_ptr = self.private_key_obj._backend._ffi.new("unsigned char[]", bn_num_bytes)
        bin_len = self.private_key_obj._backend._lib.BN_bn2bin(bn, bin_ptr)
        self.private_key = bytes(bin_ptr)
        self.private_key_len = bin_len

    def _get_naive_public_key_bytes(self):
        if self.public_key_obj is None:
            return
        if self.key_compression == KeyPairPy.POINT_CONVERSION_COMPRESSED:
            self.public_key = self.public_key_obj.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.CompressedPoint)
        else:
            self.public_key = self.public_key_obj.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        self.public_key_len = len(self.public_key)

    def _mk_keyobj_from_public_key(self, pubkey):
        if self.curvetype == KeyType.ECDSA_P256v1:
            self.public_key_obj = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), pubkey)
        elif self.curvetype == KeyType.ECDSA_SECP256k1:
            self.public_key_obj = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), pubkey)
        else:
            return

    def generate(self):
        """Generate a new key pair"""
        if self.curvetype == KeyType.ECDSA_P256v1:
            self.private_key_obj = ec.generate_private_key(ec.SECP256R1(), default_backend())
        elif self.curvetype == KeyType.ECDSA_SECP256k1:
            self.private_key_obj = ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key_obj = self.private_key_obj.public_key()
        self._get_naive_private_key_bytes()
        self._get_naive_public_key_bytes()

    def mk_keyobj_from_private_key(self, privkey):
        """Make a keypair object from the binary data of private key"""
        bn = BACKEND_KP.private_key_obj._backend._ffi.NULL
        bn_ptr = BACKEND_KP.private_key_obj._backend._lib.BN_bin2bn(privkey, len(privkey), bn)
        secret_val = BACKEND_KP.private_key_obj._backend._bn_to_int(bn_ptr)

        if self.curvetype == KeyType.ECDSA_P256v1:
            self.private_key_obj = ec.derive_private_key(secret_val, ec.SECP256R1(), default_backend())
        elif self.curvetype == KeyType.ECDSA_SECP256k1:
            self.private_key_obj = ec.derive_private_key(secret_val, ec.SECP256K1(), default_backend())
        self._get_naive_private_key_bytes()
        self.public_key_obj = self.private_key_obj.public_key()
        self._get_naive_public_key_bytes()

    def mk_keyobj_from_private_key_der(self, derdat):
        """Make a keypair object from the private key in DER format"""
        self.private_key_obj = serialization.load_der_private_key(derdat, password=None, backend=default_backend())
        self._get_naive_private_key_bytes()
        self.public_key_obj = self.private_key_obj.public_key()
        self._get_naive_public_key_bytes()

    def mk_keyobj_from_private_key_pem(self, pemdat_string):
        """Make a keypair object from the private key in PEM format"""
        if isinstance(pemdat_string, str):
            pemdat_string = pemdat_string.encode()
        self.private_key_obj = serialization.load_pem_private_key(pemdat_string, password=None, backend=default_backend())
        self._get_naive_private_key_bytes()
        self.public_key_obj = self.private_key_obj.public_key()
        self._get_naive_public_key_bytes()

    def import_publickey_cert_pem(self, cert_pemstring, privkey_pemstring=None):
        """Verify and import X509 public key certificate in pem format"""
        ## TODO: This method is not tested. It may have bugs.
        if isinstance(cert_pemstring, str):
            cert_pemstring = cert_pemstring.encode('utf-8')
        cert = x509.load_pem_x509_certificate(cert_pemstring, default_backend())
        fingerprint = cert.fingerprint(hashes.SHA256())

        if privkey_pemstring is not None:
            self.mk_keyobj_from_private_key_pem(privkey_pemstring)
            sig = self.private_key_obj.sign(fingerprint, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
            public_key = cert.public_key()
            result = public_key.verify(sig, fingerprint, ec.ECDSA(hashes.SHA256()))
            if not result:
                return False
            self.private_key_obj = public_key
            self._get_naive_private_key_bytes()

        self._get_naive_public_key_bytes()
        return True

    def to_binary(self, dat):
        byteval = bytearray()
        if self.public_key_len > 0:
            for i in range(self.public_key_len):
                byteval.append(dat % 256)
                dat = dat // 256
        else:
            while True:
                byteval.append(dat % 256)
                dat = dat // 256
                if dat == 0:
                    break
        return byteval

    def get_private_key_in_der(self):
        """Return private key in DER format"""
        serialized_private = self.private_key_obj.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        return serialized_private

    def get_public_key_in_der(self):
        """Return private key in DER format"""
        serialized_public = self.public_key_obj.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized_public

    def get_private_key_in_pem(self):
        """Return private key in PEM format"""
        serialized_private = self.private_key_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        return serialized_private

    def get_public_key_in_pem(self):
        """Return public key in PEM format"""
        serialized_public = self.public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized_public

    def sign(self, digest):
        """Sign to the given value

        Args:
            digest (bytes): given value
        Returns:
            bytes: signature
        """
        sig = self.private_key_obj.sign(digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        sig_rs = utils.decode_dss_signature(sig)
        sig_r = int.to_bytes(sig_rs[0], 32, "big")
        sig_s = int.to_bytes(sig_rs[1], 32, "big")
        return bytes(bytearray(sig_r)+bytearray(sig_s))

    def verify(self, digest, sig):
        """Verify the digest and the signature using the private key in this object"""
        sig_r = sig[:32]
        sig_s = sig[32:]
        signature = utils.encode_dss_signature(_convert_binary_to_bigint(sig_r), _convert_binary_to_bigint(sig_s))
        try:
            self.public_key_obj.verify(signature, digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        except cryptography.exceptions.InvalidSignature:
            return False
        return True


BACKEND_KP = KeyPairPy()
BACKEND_KP.generate()

try:
    directory, filename = os.path.split(os.path.realpath(__file__))
    if platform.system() == "Windows":
        if not os.path.exists(os.path.join(directory, "libbbcsig.dll")):
            raise Exception("DLL not exists")
    elif platform.system() == "Darwin":
        if not os.path.exists(os.path.join(directory, "libbbcsig.dylib")):
            raise Exception("DLL not exists")
    else:
        if not os.path.exists(os.path.join(directory, "libbbcsig.so")):
            raise Exception("DLL not exists")
    from bbclib.libs import bbclib_keypair_fast
    KeyPair = bbclib_keypair_fast.KeyPairFast
except:
    KeyPair = KeyPairPy

