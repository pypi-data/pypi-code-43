"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

import typing
from marshmallow import types
from katena_chain_sdk_py.entity.certify.common import get_type_certificate_raw_v1, get_type_certificate_ed25519_v1, \
    get_type_secret_nacl_box_v1
from katena_chain_sdk_py.serializer.base_schema import BaseSchema
from katena_chain_sdk_py.entity.certify.certificate import CertificateRawV1Schema, CertificateEd25519V1Schema
from katena_chain_sdk_py.entity.certify.secret import SecretNaclBoxV1Schema


def get_available_types() -> typing.Dict[str, BaseSchema]:
    return {
        get_type_certificate_raw_v1(): CertificateRawV1Schema(),
        get_type_certificate_ed25519_v1(): CertificateEd25519V1Schema(),
        get_type_secret_nacl_box_v1(): SecretNaclBoxV1Schema(),
    }


class TxDataSchema(BaseSchema):
    """ TxDataSchema allows to serialize and deserialize TxData. """

    def dump(self, obj: typing.Any, *, many: bool = None) -> dict:
        if hasattr(obj, "get_type"):
            available_types = get_available_types()
            obj_type = obj.get_type()
            if obj_type in available_types:
                return {
                    'type': obj_type,
                    'value': available_types[obj_type].dump(obj, many=many)
                }
        return super().dump(obj, many=many)

    def load(
            self,
            data: typing.Mapping,
            *,
            many: bool = None,
            partial: typing.Union[bool, types.StrSequenceOrSet] = None,
            unknown: str = None
    ) -> typing.Any:
        available_types = get_available_types()
        if "type" in data and "value" in data:
            obj_type = data["type"]
            if obj_type in available_types:
                return available_types[obj_type].load(data["value"], many=many, partial=partial, unknown=unknown)
        return super().load(data, many=many, partial=partial, unknown=unknown)
