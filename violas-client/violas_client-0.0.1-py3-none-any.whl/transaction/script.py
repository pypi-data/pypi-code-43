from canoser import Struct, Uint8, bytes_to_int_list, hex_to_int_list
from libra.transaction.transaction_argument import TransactionArgument, normalize_public_key
from libra.bytecode import bytecodes
from libra.account_address import Address
from canoser.util import int_list_to_hex, bytes_to_hex


class Script(Struct):
    _fields = [
        ('code', [Uint8]),
        ('args', [TransactionArgument])
    ]

    DEFAULT_MODULE_ADDRESS = "023f385e432f0d9c4cb35fc075637093d4506c35036011716177150478ddf287"
    @classmethod
    def gen_transfer_script(cls, receiver_address,micro_libra):
        if isinstance(receiver_address, bytes):
            receiver_address = bytes_to_int_list(receiver_address)
        if isinstance(receiver_address, str):
            receiver_address = hex_to_int_list(receiver_address)
        code = bytecodes["peer_to_peer_transfer"]
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra)
            ]
        return Script(code, args)

    @classmethod
    def gen_mint_script(cls, receiver_address,micro_libra):
        receiver_address = Address.normalize_to_int_list(receiver_address)
        code = bytecodes["mint"]
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra)
            ]
        print("args = ",args)
        return Script(code, args)

    @classmethod
    def gen_create_account_script(cls, fresh_address):
        fresh_address = Address.normalize_to_int_list(fresh_address)
        code = bytecodes["create_account"]
        args = [
                TransactionArgument('Address', fresh_address),
                TransactionArgument('U64', 0)
            ]
        return Script(code, args)

    @classmethod
    def gen_rotate_auth_key_script(cls, public_key):
        key = normalize_public_key(public_key)
        code = bytecodes["rotate_authentication_key"]
        args = [
                TransactionArgument('ByteArray', key)
            ]
        return Script(code, args)

    @staticmethod
    def get_script_bytecode(script_name):
        return bytecodes[script_name]



    @classmethod
    def gen_violas_init_script(cls,module_address):
        if isinstance(module_address, bytes):
            module_address = bytes_to_hex(module_address)
        if isinstance(module_address, list):
            module_address = int_list_to_hex(module_address)

        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_init"]).replace(
            cls.DEFAULT_MODULE_ADDRESS, module_address))
        args = [
        ]
        return Script(code, args)


    @classmethod
    def gen_violas_mint_script(cls, receiver_address,micro_libra,module_address):
        receiver_address = Address.normalize_to_int_list(receiver_address)
        if isinstance(module_address, bytes):
            module_address = bytes_to_hex(module_address)
        if isinstance(module_address, list):
            module_address = int_list_to_hex(module_address)

        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_mint"]).replace(cls.DEFAULT_MODULE_ADDRESS, module_address))
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra)
            ]
        return Script(code, args)

    @classmethod
    def gen_violas_transfer_script(cls, receiver_address,micro_libra,module_address):
        receiver_address = Address.normalize_to_int_list(receiver_address)
        code = hex_to_int_list(int_list_to_hex(bytecodes["violas_transfer"]).replace(cls.DEFAULT_MODULE_ADDRESS, module_address))
        args = [
                TransactionArgument('Address', receiver_address),
                TransactionArgument('U64', micro_libra)
            ]
        return Script(code, args)