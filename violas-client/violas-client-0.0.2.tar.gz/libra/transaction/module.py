from canoser import Struct, Uint8
from libra.bytecode import bytecodes
from canoser.util import int_list_to_hex, bytes_to_hex, hex_to_int_list


class Module(Struct):
    _fields = [
        ('code', [Uint8])
    ]

    DEFAULT_MODULE_ADDRESS = "023f385e432f0d9c4cb35fc075637093d4506c35036011716177150478ddf287"

    @classmethod
    def gen_violas_publish_module(cls, module_address):
        if isinstance(module_address, bytes):
            module_address = bytes_to_hex(module_address)
        if isinstance(module_address, list):
            module_address = int_list_to_hex(module_address)
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_module"]).replace(
            cls.DEFAULT_MODULE_ADDRESS, module_address))
        return Module(code)
