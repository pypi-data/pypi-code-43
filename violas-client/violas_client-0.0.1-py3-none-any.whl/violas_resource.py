from canoser import *
from libra.access_path import *
from libra.language_storage import StructTag

class ViolasResource(Struct):
    COIN_MODULE_NAME = "DToken";
    COIN_STRUCT_NAME = "T";

    _fields = [
        ('balance', Uint64)
    ]

    @classmethod
    def violas_resource_path(cls,address):
        return bytes(AccessPath.resource_access_vec(cls.violas_struct_tag(address),[]))

    @classmethod
    def violas_struct_tag(cls,address):
        return StructTag(
            hex_to_int_list(address),
            cls.COIN_MODULE_NAME,
            cls.COIN_STRUCT_NAME,
            []
    )