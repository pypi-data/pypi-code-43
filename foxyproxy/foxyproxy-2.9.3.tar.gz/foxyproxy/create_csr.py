#!/usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection
from __future__ import unicode_literals

import binascii
import logging

from cryptography import x509
# noinspection PyProtectedMember
from cryptography.hazmat.backends.openssl.encode_asn1 import _encode_name_gc, _EXTENSION_ENCODE_HANDLERS
# noinspection PyProtectedMember
from cryptography.hazmat.backends.openssl.x509 import _CertificateSigningRequest

log = logging.getLogger(__name__)


# noinspection PyProtectedMember
def create_csr_info(csr, public_key, algorithm, backend):
    """

    :param csr:
    :param public_key:
    :param algorithm:
    :param backend:
    :return:
    """
    # Resolve the signature algorithm.
    evp_md = backend._lib.EVP_get_digestbyname(
        algorithm.name.encode('ascii')
    )
    backend.openssl_assert(evp_md != backend._ffi.NULL)

    # Create an empty request.
    x509_req = backend._lib.X509_REQ_new()
    backend.openssl_assert(x509_req != backend._ffi.NULL)
    x509_req = backend._ffi.gc(x509_req, backend._lib.X509_REQ_free)

    # Set x509 version.
    res = backend._lib.X509_REQ_set_version(x509_req, x509.Version.v1.value)
    backend.openssl_assert(res == 1)

    # Set subject name.
    res = backend._lib.X509_REQ_set_subject_name(
        x509_req, _encode_name_gc(backend, csr._subject_name)
    )
    backend.openssl_assert(res == 1)

    # Set subject public key.
    res = backend._lib.X509_REQ_set_pubkey(
        x509_req, public_key._evp_pkey
    )
    backend.openssl_assert(res == 1)

    # Add extensions.
    sk_extension = backend._lib.sk_X509_EXTENSION_new_null()
    backend.openssl_assert(sk_extension != backend._ffi.NULL)
    sk_extension = backend._ffi.gc(
        sk_extension, backend._lib.sk_X509_EXTENSION_free
    )
    # gc is not necessary for CSRs, as sk_X509_EXTENSION_free
    # will release all the X509_EXTENSIONs.
    backend._create_x509_extensions(
        extensions=csr._extensions,
        handlers=_EXTENSION_ENCODE_HANDLERS,
        x509_obj=sk_extension,
        add_func=backend._lib.sk_X509_EXTENSION_insert,
        gc=False
    )
    res = backend._lib.X509_REQ_add_extensions(x509_req, sk_extension)
    backend.openssl_assert(res == 1)

    return _CertificateSigningRequest(backend, x509_req)


def create_csr_signed(csr, signature):
    """
    Returns a CSR in hex encoding.

    :param csr: the initial CSR
    :type csr: _CertificateSigningRequest
    :param signature:
    :type signature: hexencoded signature
    :return:
    """

    wrapping = binascii.hexlify(csr.tbs_certrequest_bytes)
    wrapping = wrapping + '300D06092A864886F70D01010B0500'  # OID for sha256with RSA

    # create signature length encoding
    signature = "00" + signature
    sig_len = len(signature) // 2
    len_str = "%X" % sig_len
    if len(len_str) % 2 == 1:
        len_str = "0" + len_str
    if sig_len > 127:
        l_l = "8%X" % (len(len_str) // 2)
        len_str = l_l + len_str
    encoded_signature = '03' + len_str + signature

    wrapping = wrapping + encoded_signature

    # and a final sequence wrapping the whole structure
    all_len = len(wrapping) // 2
    len_str = "%X" % all_len
    if len(len_str) % 2 == 1:
        len_str = "0" + len_str
    if all_len > 127:
        l_l = "8%X" % (1 + sig_len // 256)
        len_str = l_l + len_str

    csr_hex = '30' + len_str + wrapping

    return csr_hex
