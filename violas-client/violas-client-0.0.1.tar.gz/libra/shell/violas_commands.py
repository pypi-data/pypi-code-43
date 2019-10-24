from libra.cli.command import *
from canoser import Uint64

class ViolasCommand(Command):
    def get_aliases(self):
        return ["violas", "v"]

    def get_description(self):
        return "Violas operations"

    def execute(self, client, params):
        commands = [
            ViolasCommandPublishModule(),
            ViolasCommandInit(),
            ViolasCommandMint(),
            ViolasCommandTransfer(),
            ViolasCommandGetBalance()
        ]
        self.subcommand_execute(params[0], commands, client, params[1:])

class ViolasCommandGetBalance(Command):
    def get_aliases(self):
        return ["balance", "b"]

    def get_params_help(self):
        return "<account_ref_id>|<account_address> <module_ref_id>|<module_address>"

    def get_description(self):
        return "Get the current violas balance of an account"

    def execute(self, client, params):
        balance = client.get_violas_balance(params[1],params[2])
        print(f"Balance is: {balance}")


class ViolasCommandPublishModule(Command):
    def get_aliases(self):
        return ["publish", "publishb", "p", "pb"]

    def get_params_help(self):
        return "<account_ref_id>|<account_address>"

    def get_description(self):
        return "Publish violas module on-chain"

    def execute(self, client, params):
        print(">> Publishing module")
        is_blocking = blocking_cmd(params[0])
        client.publish_violas_coin(params[1], is_blocking)
        if is_blocking:
            print("Finished publishing!")
        else:
            print("Publish request submitted")

class ViolasCommandInit(Command):
    def get_aliases(self):
        return ["init", "initb", "i", "ib"]

    def get_params_help(self):
        return "<account_ref_id>|<account_address> <module_ref_id>|<module_address>"

    def get_description(self):
        return "Init violas module on-chain"

    def execute(self, client, params):
        print(">> Initing module")
        is_blocking = blocking_cmd(params[0])
        client.init_violas_coin(params[1], params[2], is_blocking)
        if is_blocking:
            print("Finished initing!")
        else:
            print("init request submitted")

class ViolasCommandMint(Command):
    def get_aliases(self):
        return ["mint", "mintb", "m", "mb"]

    def get_params_help(self):
        return "<receiver_account_ref_id>|<receiver_account_address> <number_of_coins> <module_account_ref_id>|<module_account_address>"

    def get_description(self):
        return "Mint violas coins to the account. Suffix 'b' is for blocking"

    def execute(self, client, params):
        print(">> Minting coins")
        is_blocking = blocking_cmd(params[0])
        client.mint_violas_coins(params[1], params[2], params[3], is_blocking)
        if is_blocking:
            print("Finished minting!")
        else:
            print("Mint request submitted")

class ViolasCommandTransfer(Command):
    def get_aliases(self):
        return ["transfer", "transferb", "t", "tb"]

    def get_params_help(self):
        return ("\n\t<sender_account_address>|<sender_account_ref_id>"
         " <receiver_account_address>|<receiver_account_ref_id> <number_of_coins> <module_account_address>|<module_account_ref_id>"
         " [gas_unit_price_in_micro_libras (default=0)] [max_gas_amount_in_micro_libras (default 140000)]"
         " Suffix 'b' is for blocking. ")

    def get_description(self):
        return "Transfer coins (in libra) from account to another."

    def execute(self, client, params):
        if len(params) == 6:
            gas_unit_price_in_micro_libras = Uint64.int_safe(params[5])
        else:
            gas_unit_price_in_micro_libras = 0
        if len(params) == 7:
            max_gas_amount_in_micro_libras = Uint64.int_safe(params[6])
        else:
            max_gas_amount_in_micro_libras = 140_000
        print(">> Transferring")
        is_blocking = blocking_cmd(params[0])
        sequence_number = client.transfer_violas_coins(params[1], params[2], params[3], params[4],
            max_gas_amount_in_micro_libras, gas_unit_price_in_micro_libras, is_blocking)
        if is_blocking:
            print("Finished transaction!")
        else:
            print("Transaction submitted to validator")
        print(
            "To query for transaction status, run: query txn_acc_seq {} {} \
            <fetch_events=true|false>".format(
            params[1], sequence_number
            )
        )