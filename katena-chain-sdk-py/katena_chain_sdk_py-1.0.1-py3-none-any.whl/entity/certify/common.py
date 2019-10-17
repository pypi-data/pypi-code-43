"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

NAMESPACE_CERTIFY = "certify"
TYPE_CERTIFICATE = "certificate"
TYPE_SECRET = "secret"
TYPE_RAW = "raw"
TYPE_ED25519 = "ed25519"
TYPE_NACL_BOX = "nacl_box"


def format_bcid(company_chain_id: str, uuid: str) -> str:
    """ Concatenates a company chain id and a uuid into a bcid. """
    return "{}-{}".format(company_chain_id, uuid)


def get_secret_sub_namespace() -> str:
    return "{}.{}".format(NAMESPACE_CERTIFY, TYPE_SECRET)


def get_type_secret_nacl_box_v1() -> str:
    return "{}.{}.{}".format(get_secret_sub_namespace(), TYPE_NACL_BOX, "v1")


def get_certificate_sub_namespace() -> str:
    return "{}.{}".format(NAMESPACE_CERTIFY, TYPE_CERTIFICATE)


def get_type_certificate_raw_v1() -> str:
    return "{}.{}.{}".format(get_certificate_sub_namespace(), TYPE_RAW, "v1")


def get_type_certificate_ed25519_v1() -> str:
    return "{}.{}.{}".format(get_certificate_sub_namespace(), TYPE_ED25519, "v1")
