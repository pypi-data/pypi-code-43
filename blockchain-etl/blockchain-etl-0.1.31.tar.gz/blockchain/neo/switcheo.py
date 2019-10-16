import binascii
import datetime
import random
import requests
import re
from multiprocessing.dummy import Pool as ThreadPool
from octopus.platforms.NEO.explorer import NeoExplorerRPC
from octopus.platforms.NEO.disassembler import NeoDisassembler
from octopus.engine.explorer import RequestsConnectionError
from switcheo.switcheo_client import SwitcheoClient
from switcheo.neo.utils import create_offer_hash, neo_get_address_from_scripthash,\
    neo_get_scripthash_from_address, reverse_hex
from switcheo.Fixed8 import SwitcheoFixed8
from blockchain.neo.ingest import NeoIngest


class SwitcheoSmartContract(object):
    def __init__(self,
                 rpc_hostname='localhost',
                 rpc_port='10332',
                 rpc_tls=False,
                 contract_hash='91b83e96f2a7c4fdf0c1688441ec61986c7cae26',
                 mongodb_protocol='mongodb',
                 mongodb_user='switcheo',
                 mongodb_password='switcheo',
                 mongodb_hostname='localhost',
                 mongodb_port='27017',
                 mongodb_db='neo'
    ):
        self.neo_rpc_client = self.get_neo_node()
        # self.neo_rpc_client = NeoExplorerRPC(host=rpc_hostname, port=rpc_port, tls=rpc_tls)
        self.contract_hash = contract_hash
        self.function_params = []
        self.switcheo_transactions = []
        self.switcheo_fees = []
        self.switcheo_freezes = []
        self.deserialize_script = {
            'addToWhitelist': self.deserialize_add_to_whitelist,
            'announceCancel': self.deserialize_announce_withdraw,
            'announceWithdraw': self.deserialize_announce_withdraw,
            'approve': self.deserialize_approve,
            'cancelAtomicSwap': self.deserialize_cancel_atomic_swap,
            'cancelOffer': self.deserialize_cancel,
            'createAtomicSwap': self.deserialize_create_atomic_swap,
            'deploy': self.deserialize_deploy,
            'deposit': self.deserialize_deposit,
            'executeAtomicSwap': self.deserialize_execute_atomic_swap,
            'fillOffer': self.deserialize_fill_offer,
            'freezeTrading': self.deserialize_freeze_trading,
            'generate_tokens': self.deserizlize_generate_tokens,
            'initialize': self.deserialize_initialize,
            'makeOffer': self.deserialize_make_offer,
            'mintTokens': self.deserialize_mint_tokens,
            'removeFromWhitelist': self.deserialize_remove_from_whitelist,
            'setTakerFee': self.deserialize_set_taker_fee,
            'transfer': self.deserialize_transfer,
            'unfreezeTrading': self.deserialize_unfreeze_trading,
            'withdraw': self.deserialize_withdraw,
            'withdrawAssets': self.deserialize_withdraw_assets,
            'withdrawal': self.deserialize_withdrawal,
            'unlockAdvisor': self.deserialize_nkn_unlock_advisor,
            'disableTransfer': self.deserialize_nkn_disable_transfer,
            'inflation': self.deserialize_phx_inflation,
            'unlockTeam': self.deserialize_unlock_team,
            'passUnknown': self.deserialize_pass_unknown
        }
        self.neo_smart_contract_function_dict = {
            str(binascii.hexlify(b'deposit').decode('utf-8')): 'deposit',
            str(binascii.hexlify(b'depositFrom').decode('utf-8')): 'depositFrom',
            str(binascii.hexlify(b'onTokenTransfer').decode('utf-8')): 'onTokenTransfer',
            str(binascii.hexlify(b'makeOffer').decode('utf-8')): 'makeOffer',
            str(binascii.hexlify(b'fillOffer').decode('utf-8')): 'fillOffer',
            str(binascii.hexlify(b'cancelOffer').decode('utf-8')): 'cancelOffer',
            str(binascii.hexlify(b'withdraw').decode('utf-8')): 'withdraw',
            str(binascii.hexlify(b'announceCancel').decode('utf-8')): 'announceCancel',
            str(binascii.hexlify(b'announceWithdraw').decode('utf-8')): 'announceWithdraw',
            str(binascii.hexlify(b'transfer').decode('utf-8')): 'transfer',
            str(binascii.hexlify(b'mintTokens').decode('utf-8')): 'mintTokens',
            str(binascii.hexlify(b'addToWhitelist').decode('utf-8')): 'addToWhitelist',
            str(binascii.hexlify(b'initialize').decode('utf-8')): 'initialize',
            str(binascii.hexlify(b'setTakerFee').decode('utf-8')): 'setTakerFee',
            str(binascii.hexlify(b'approve').decode('utf-8')): 'approve',
            str(binascii.hexlify(b'withdrawal').decode('utf-8')): 'withdrawal',
            str(binascii.hexlify(b'withdrawAssets').decode('utf-8')): 'withdrawAssets',
            str(binascii.hexlify(b'freezeTrading').decode('utf-8')): 'freezeTrading',
            str(binascii.hexlify(b'unfreezeTrading').decode('utf-8')): 'unfreezeTrading',
            str(binascii.hexlify(b'removeFromWhitelist').decode('utf-8')): 'removeFromWhitelist',
            str(binascii.hexlify(b'deploy').decode('utf-8')): 'deploy',
            str(binascii.hexlify(b'generate_tokens').decode('utf-8')): 'generate_tokens',
            str(binascii.hexlify(b'createAtomicSwap').decode('utf-8')): 'createAtomicSwap',
            str(binascii.hexlify(b'executeAtomicSwap').decode('utf-8')): 'executeAtomicSwap',
            str(binascii.hexlify(b'cancelAtomicSwap').decode('utf-8')): 'cancelAtomicSwap',
            str(binascii.hexlify(b'unlockAdvisor').decode('utf-8')): 'unlockAdvisor',
            str(binascii.hexlify(b'disableTransfer').decode('utf-8')): 'disableTransfer',
            str(binascii.hexlify(b'inflation').decode('utf-8')): 'inflation',
            str(binascii.hexlify(b'unlockTeam').decode('utf-8')): 'unlockTeam',
            str(binascii.hexlify(b'passUnknown').decode('utf-8')): 'passUnknown'
        }
        self.offer_hash_functions = {
            'cancel': self.offer_hash_cancel,
            'makeOffer': self.offer_hash_make,
            'fillOffer': self.offer_hash_fill
        }
        self.address_functions = {
            'cancel': self.address_cancel,
            'deposit': self.address_deposit,
            'fillOffer': self.address_fill,
            'makeOffer': self.address_make,
            'withdrawal': self.address_withdrawal
        }
        self.address_transaction_dict = {
            'deposit': 'deposit_address',
            'fillOffer': 'taker_address',
            'makeOffer': 'maker_address',
            'withdrawal': 'withdraw_address'
        }
        self.sc = SwitcheoClient(switcheo_network='main')
        self.ni = NeoIngest(protocol=mongodb_protocol, username=mongodb_user, password=mongodb_password,
                            hostname=mongodb_hostname, port=mongodb_port, database=mongodb_db)
        self.neo_contract_list = self.get_neo_contract_list()
        self.neo_contract_dict = self.get_neo_contract_dict()
        self.neo_token_dict = self.get_neo_token_dict()
        self.neo_contract_key_list = ['APPCALL', 'TAILCALL']
        self.neo_address_list = [
            'ASH41gtWftHvhuYhZz1jj7ee7z9vp9D9wk',
            'AMAvaXFKtowxB5VpJ928QCSLZD9iMRnhbo'
        ]
        self.neo_trade_pair_list = self.sc.get_pairs()
        self.neo_trade_pair_list.append('ONT_NEO')
        self.neo_trade_pair_list.append('ONT_GAS')
        self.neo_trade_pair_list.append('ONT_SWTH')
        self.neo_trade_pair_list.append('SDT_NEO')
        self.neo_trade_pair_list.append('SDT_GAS')
        self.neo_trade_pair_list.append('SDT_SWTH')
        self.neo_trade_pair_list.append('RPX_NEO')
        self.neo_trade_pair_list.append('RPX_GAS')
        self.neo_trade_pair_list.append('RPX_SWTH')
        self.neo_trade_pair_list.append('IAM_NEO')
        self.neo_trade_pair_list.append('IAM_GAS')
        self.neo_trade_pair_list.append('IAM_SWTH')

    def _get(self, url, params=None):
        """Perform GET request"""
        r = requests.get(url=url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def is_trading_active(self):
        state_dict = {"00": False, "01": True}
        function_name = 'getState'
        response_script = self.get_neo_node().invokefunction(script_hash=self.contract_hash,
                                                             operation=function_name,
                                                             params=self.function_params)
        # response_script = self.neo_rpc_client.invokefunction(script_hash=self.contract_hash,
        #                                                      operation=function_name,
        #                                                      params=self.function_params)
        return state_dict[reverse_hex(response_script['stack'][0]['value'])]

    def get_neo_contract_list(self):
        contract_list = []
        neo_contracts = self.sc.get_contracts()['NEO']
        for key, value in neo_contracts.items():
            contract_list.append(value)
        return contract_list

    def get_neo_contract_dict(self):
        contract_dict = {}
        neo_contracts = self.sc.get_contracts()['NEO']
        for key, value in neo_contracts.items():
            contract_dict[value] = key
        return contract_dict

    def get_neo_token_dict(self):
        token_dict = {}
        neo_tokens = self.sc.get_token_details(show_inactive=True)
        for key, value in neo_tokens.items():
            token_dict[value['hash']] = key
            self.neo_contract_list.append(value['hash'])
            self.neo_contract_dict[value['hash']] = key
        return token_dict

    def get_neo_node(self):
        neo_node_list = []
        neo_node_max_height = 0
        for neo_nodes in self._get(url='https://api.neoscan.io/api/main_net/v1/get_all_nodes'):
            neo_node_dict = {}
            neo_node = neo_nodes['url'].split(':')
            neo_node_height = neo_nodes['height']
            if neo_node_max_height < neo_node_height:
                neo_node_max_height = neo_node_height
            neo_node_protocol = neo_node[0]
            neo_node_url = neo_node[1][2:]
            if not neo_node_url.endswith('neo.neonexchange.org') and not neo_node_url.endswith('neo.nash.io'):
                neo_node_port = neo_node[2]
            if neo_node_protocol == 'https':
                neo_node_rpc_tls = True
            elif neo_node_protocol == 'http':
                neo_node_rpc_tls = False
            else:
                exit(222)
            neo_node_dict['neo_node_url'] = neo_node_url
            neo_node_dict['neo_node_port'] = neo_node_port
            neo_node_dict['neo_node_tls'] = neo_node_rpc_tls
            neo_node_dict['neo_node_height'] = neo_node_height
            neo_node_list.append(neo_node_dict)

        neo_node_max_height_list = []
        for neo_node in neo_node_list:
            if neo_node['neo_node_height'] == neo_node_max_height and 'neo.org' not in neo_node['neo_node_url']\
                    and 'rustylogic.ddns.net' not in neo_node['neo_node_url']\
                    and not neo_node['neo_node_url'].endswith('neonexchange.org')\
                    and not neo_node['neo_node_url'].endswith('nash.io'):
                neo_node_max_height_list.append(neo_node)

        rand_int = random.randint(0, len(neo_node_max_height_list) - 1)
        print(neo_node_max_height_list[rand_int])
        return NeoExplorerRPC(host=neo_node_max_height_list[rand_int]['neo_node_url'],
                              port=neo_node_max_height_list[rand_int]['neo_node_port'],
                              tls=neo_node_max_height_list[rand_int]['neo_node_tls'])

    def get_neo_block_height(self):
        try:
            # return self.get_neo_node().getblockcount() - 1  # I believe this is required b/c the block needs at least 1 confirmation so you can't retrieve the most recent block.
            return self.neo_rpc_client.getblockcount() - 1  # I believe this is required b/c the block needs at least 1 confirmation so you can't retrieve the most recent block.
        except RequestsConnectionError:
            self.get_neo_block_height()
        except Exception as e:
            print("Generic Exception - " + str(e))
            self.get_neo_block_height()

    def get_neo_latest_block(self):
        # return self.get_neo_node().get_block_by_number(block_number=self.get_neo_block_height())
        return self.neo_rpc_client.get_block_by_number(block_number=self.get_neo_block_height())

    def get_neo_bulk_blocks(self, block_number_list):
        pool = ThreadPool(5)
        try:
            # block_list = pool.map(self.get_neo_node().get_block_by_number, block_number_list)
            block_list = pool.map(self.neo_rpc_client.get_block_by_number, block_number_list)
        except RequestsConnectionError:
            self.neo_rpc_client = self.get_neo_node()
            self.get_neo_bulk_blocks(block_number_list=block_number_list)
            block_list = []
        except Exception as e:
            print("Generic Exception - " + str(e))
            self.neo_rpc_client = self.get_neo_node()
            self.get_neo_bulk_blocks(block_number_list=block_number_list)
            block_list = []
        pool.close()
        pool.join()
        return block_list

    def chunk_list(self, input_list, chunk_size):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(input_list), chunk_size):
            yield input_list[i:i + chunk_size]

    def zero_pad_if_odd_length_string(self, input_string, output_size=None):
        input_string_length = len(input_string)
        if output_size is not None:
            output_string_length = output_size
            if output_string_length % 2 == 1:
                output_string_length = output_string_length + 1
        elif input_string_length % 2 == 1:
            output_string_length = input_string_length + 1
        else:
            output_string_length = input_string_length
        return input_string.rjust(output_string_length, '0')


    def deserialize_block(self, block):
        for transaction in block['tx']:
            self.deserialize_transaction(block, transaction)

    def deserialize_transaction(self, block, txn):
        is_pack = False
        is_switcheo = False
        contract_hash = None
        print(txn)
        if 'vout' in txn:
            for txn_vout in txn['vout']:
                if txn_vout['address'] in self.neo_address_list:
                    is_switcheo = True
        if 'script' in txn:
            disassemble_dict = {}
            script_disassembler = NeoDisassembler(bytecode=txn['script']).disassemble()
            # disassemble_length = len(script_disassembler)
            # if str(script_disassembler[disassemble_length - 1]).split()[0] in self.neo_contract_key_list:
            #     contract_hash = reverse_hex(str(script_disassembler[disassemble_length - 1]).split()[1][2:])
            # if contract_hash is None:
            for s in script_disassembler:
                if str(s).split()[0] in self.neo_contract_key_list and contract_hash is None:
                    contract_hash_pad = self.zero_pad_if_odd_length_string(str(s).split()[1][2:], output_size=40)
                    contract_hash = reverse_hex(contract_hash_pad)
            if contract_hash != '78e6d16b914fe15bc16150aeb11d0c2a8e532bdd':
                for disassemble in script_disassembler:
                    disassemble_list = str(disassemble).split()
                    if is_pack:
                        if 'function' not in disassemble_dict and disassemble_list[0].startswith('PUSHBYTES'):
                            disassemble_dict['function'] = disassemble_list[1][2:]
                        if 'contract' not in disassemble_dict and disassemble_list[0] in self.neo_contract_key_list:
                            disassemble_dict_contract = self.zero_pad_if_odd_length_string(disassemble_list[1][2:],
                                                                                           output_size=40)
                            disassemble_dict['contract'] = disassemble_dict_contract
                            if is_switcheo and disassemble_dict_contract in ['3fbc607c12c28736343224a4b4d8f513a5c27ca8', reverse_hex('ab38352559b8b203bde5fddfa0b07d8b2525e132')]:  # Custom Code for transfering MCT tokens.
                                disassemble_dict['function_name'] = self.neo_smart_contract_function_dict[
                                    disassemble_dict['function']]
                            if reverse_hex(disassemble_dict['contract']) in self.neo_contract_list and 'function' in disassemble_dict:
                                is_switcheo = True
                                try:
                                    disassemble_dict['function_name'] = self.neo_smart_contract_function_dict[
                                        disassemble_dict['function']]
                                except KeyError:
                                    if reverse_hex(disassemble_dict['contract']) in ["a32bcf5d7082f740a4007b16e812cf66a457c3d4", "91b83e96f2a7c4fdf0c1688441ec61986c7cae26"]:
                                        exit('Missing Switcheo Contract Function.')
                                    else:
                                        disassemble_dict['function_name'] = 'passUnknown'
                    if disassemble_list[0] == 'PACK':
                        is_pack = True
                if is_switcheo:
                    txn['contract_hash'] = contract_hash
                    try:
                        txn['contract_hash_version'] = self.neo_contract_dict[contract_hash]
                    except KeyError:
                        print(txn)
                        print(contract_hash)
                        exit('Key Error')
                    return self.deserialize_script[disassemble_dict['function_name']](block, txn, script_disassembler)

    def deserialize_pass_unknown(self, block, txn, script):
        pass

    def deserialize_nkn_unlock_advisor(self, block, txn, script):
        pass

    def deserialize_nkn_disable_transfer(self, block, txn, script):
        pass

    def deserialize_phx_inflation(self, block, txn, script):
        pass

    def deserialize_unlock_team(self, block, txn, script):
        pass

    def deserialize_add_to_whitelist(self, block, txn, script):
        pass

    def deserialize_announce_cancel(self, block, txn, script):
        pass

    def deserialize_announce_withdraw(self, block, txn, script):
        pass

    def deserialize_approve(self, block, txn, script):
        pass

    def deserialize_cancel_atomic_swap(self, block, txn, script):
        burn_cancel_fees_original = str(script[0])
        # burnTokens - Bool
        if burn_cancel_fees_original == 'PUSH1':
            burn_cancel_fees = True
        elif burn_cancel_fees_original == 'PUSH0':
            burn_cancel_fees = False

        cancel_fee_amount_original = str(script[1])
        if cancel_fee_amount_original.startswith('PUSH') and not cancel_fee_amount_original.startswith('PUSHBYTES'):
            cancel_fee_amount_original = cancel_fee_amount_original.split()[0]
            cancel_fee_amount = int(cancel_fee_amount_original[4:])
            cancel_fee_amount_fixed8 = SwitcheoFixed8(cancel_fee_amount).ToString()
        else:
            cancel_fee_amount_original = self.zero_pad_if_odd_length_string(cancel_fee_amount_original.split()[1][2:])
            cancel_fee_amount = int(reverse_hex(cancel_fee_amount_original), 16)
            cancel_fee_amount_fixed8 = SwitcheoFixed8(cancel_fee_amount).ToString()

        hash_of_secret_original = str(script[2])
        # hashOfSecret
        pad_length = int(hash_of_secret_original.split()[0][9:]) * 2
        hash_of_secret_original = self.zero_pad_if_odd_length_string(hash_of_secret_original.split()[1][2:],
                                                                     output_size=pad_length)
        hash_of_secret = reverse_hex(hash_of_secret_original)

        cancel_atomic_swap_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
            'switcheo_transaction_type': 'executeAtomicSwap',
            'burn_cancel_fees_original': burn_cancel_fees_original,
            'burn_cancel_fees': burn_cancel_fees,
            'cancel_fee_amount_original': cancel_fee_amount_original,
            'cancel_fee_amount': cancel_fee_amount,
            'cancel_fee_amount_fixed8': cancel_fee_amount_fixed8,
            'hash_of_secret_original': hash_of_secret_original,
            'hash_of_secret': hash_of_secret
        }
        return cancel_atomic_swap_dict

    def deserialize_cancel(self, block, txn, script):
        cancel_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'offer_hash_original': self.zero_pad_if_odd_length_string(str(script[0]).split()[1][2:]),
            'offer_hash': reverse_hex(str(script[0]).split()[1][2:]),
            'switcheo_transaction_type': 'cancel',
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
        }
        return cancel_dict

    def deserialize_create_atomic_swap(self, block, txn, script):
        burn_token_original = str(script[0])
        # burnTokens - Bool
        if burn_token_original == 'PUSH1':
            burn_token = True
        elif burn_token_original == 'PUSH0':
            burn_token = False

        fee_amount_original = str(script[1])
        # feeAmount
        if fee_amount_original.startswith('PUSH') and not fee_amount_original.startswith('PUSHBYTES'):
            fee_amount_original = fee_amount_original.split()[0]
            fee_amount = int(fee_amount_original[4:])
            fee_amount_fixed8 = SwitcheoFixed8(fee_amount).ToString()
        else:
            fee_amount_original = self.zero_pad_if_odd_length_string(fee_amount_original.split()[1][2:])
            fee_amount = int(reverse_hex(fee_amount_original), 16)
            fee_amount_fixed8 = SwitcheoFixed8(fee_amount).ToString()

        fee_asset_original = str(script[2])
        # feeAssetID
        pad_length = int(fee_asset_original.split()[0][9:]) * 2
        fee_asset_original = self.zero_pad_if_odd_length_string(fee_asset_original.split()[1][2:],
                                                                output_size=pad_length)
        fee_asset = reverse_hex(fee_asset_original)
        fee_asset_name = self.neo_token_dict[fee_asset]

        expiry_time_original = str(script[3])
        # expiryTime
        pad_length = int(expiry_time_original.split()[0][9:]) * 2
        expiry_time_original = self.zero_pad_if_odd_length_string(expiry_time_original.split()[1][2:],
                                                                  output_size=pad_length)
        expiry_time = reverse_hex(expiry_time_original)

        hash_of_secret_original = str(script[4])
        # hashOfSecret
        pad_length = int(hash_of_secret_original.split()[0][9:]) * 2
        hash_of_secret_original = self.zero_pad_if_odd_length_string(hash_of_secret_original.split()[1][2:],
                                                                     output_size=pad_length)
        hash_of_secret = reverse_hex(hash_of_secret_original)

        amount_original = str(script[5])
        # amount
        if amount_original.startswith('PUSH') and not amount_original.startswith('PUSHBYTES'):
            amount_original = amount_original.split()[0]
            amount = int(amount_original[4:])
            amount_fixed8 = SwitcheoFixed8(amount).ToString()
        else:
            pad_length = int(amount_original.split()[0][9:]) * 2
            amount_original = self.zero_pad_if_odd_length_string(amount_original.split()[1][2:],
                                                                 output_size=pad_length)
            amount = int(reverse_hex(amount_original), 16)
            amount_fixed8 = SwitcheoFixed8(amount).ToString()

        asset_original = str(script[6])
        # assetID
        pad_length = int(asset_original.split()[0][9:]) * 2
        asset_original = self.zero_pad_if_odd_length_string(asset_original.split()[1][2:],
                                                            output_size=pad_length)
        asset = reverse_hex(asset_original)
        asset_name = self.neo_token_dict[asset]

        taker_address_original = str(script[7])
        # takerAddress
        pad_length = int(taker_address_original.split()[0][9:]) * 2
        taker_address_original = self.zero_pad_if_odd_length_string(taker_address_original.split()[1][2:],
                                                                    output_size=pad_length)
        taker_address = neo_get_address_from_scripthash(scripthash=reverse_hex(taker_address_original))

        maker_address_original = str(script[8])
        # makerAddress
        pad_length = int(maker_address_original.split()[0][9:]) * 2
        maker_address_original = self.zero_pad_if_odd_length_string(maker_address_original.split()[1][2:],
                                                                    output_size=pad_length)
        maker_address = neo_get_address_from_scripthash(scripthash=reverse_hex(maker_address_original))

        create_atomic_swap_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
            'switcheo_transaction_type': 'createAtomicSwap',
            'burn_token_original': burn_token_original,
            'burn_token': burn_token,
            'fee_amount_original': fee_amount_original,
            'fee_amount': fee_amount,
            'fee_amount_fixed8': fee_amount_fixed8,
            'fee_asset_original': fee_asset_original,
            'fee_asset': fee_asset,
            'fee_asset_name': fee_asset_name,
            'expiry_time_original': expiry_time_original,
            'expiry_time': expiry_time,
            'hash_of_secret_original': hash_of_secret_original,
            'hash_of_secret': hash_of_secret,
            'amount_original': amount_original,
            'amount': amount,
            'amount_fixed8': amount_fixed8,
            'asset_original': asset_original,
            'asset': asset,
            'asset_name': asset_name,
            'taker_address_original': taker_address_original,
            'taker_address': taker_address,
            'maker_address_original': maker_address_original,
            'maker_address': maker_address
        }
        return create_atomic_swap_dict

    def deserialize_deploy(self, block, txn, script):
        pass

    def deserialize_deposit(self, block, txn, script):
        contract_hash = None
        for s in script:
            if str(s).split()[0] == "APPCALL":
                contract_hash = reverse_hex(str(s).split()[1][2:])
        script[1] = self.zero_pad_if_odd_length_string(str(script[1]).split()[1][2:])
        script[2] = self.zero_pad_if_odd_length_string(str(script[2]).split()[1][2:]).rjust(40, '0')
        if len(str(script[0]).split()) == 1 and str(script[0]).split()[0].startswith('PUSH'): # Redeemable Hash Puppies Deposit
            deposit_amount_original = str(script[0]).split()[0]
            deposit_amount = int(deposit_amount_original[4:])
            deposit_amount_fixed8 = SwitcheoFixed8(deposit_amount).ToString()
        elif contract_hash == '0ec5712e0f7c63e4b0fea31029a28cea5e9d551f':
            deposit_amount_original = str(script[0]).split()[1][2:]
            deposit_amount = int(reverse_hex(deposit_amount_original), 16)
            deposit_amount_fixed8 = SwitcheoFixed8(deposit_amount).ToString()
        else:
            hex_string = self.zero_pad_if_odd_length_string(str(script[0]).split()[1][2:])
            hex_bytes = int(str(script[0]).split()[0][-1])
            if hex_bytes < 8:
                deposit_amount_original = hex_string.ljust(16, '0')
            elif hex_bytes == 8:
                deposit_amount_original = hex_string.rjust(16, '0')
            else:
                raise ValueError('Deposit Hex Byte amount greater than 8.')
            deposit_amount = int(reverse_hex(deposit_amount_original), 16)
            deposit_amount_fixed8 = SwitcheoFixed8(deposit_amount).ToString()
        deposit_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
            'switcheo_transaction_type': 'deposit',
            'deposit_amount_original': deposit_amount_original,
            'deposit_amount': deposit_amount,
            'deposit_amount_fixed8': deposit_amount_fixed8,
            'deposit_asset_original': script[1],
            'deposit_asset': reverse_hex(script[1]),
            'deposit_asset_name': self.neo_token_dict[reverse_hex(script[1])],
            'deposit_address_original': script[2],
            'deposit_address': neo_get_address_from_scripthash(scripthash=reverse_hex(script[2])),
            'deposits': []
        }
        for transfer in txn['vout']:
            out_dict = {
                'deposit_address': transfer['address'],
                'deposit_asset': transfer['asset'],
                'deposit_asset_name': self.neo_token_dict[transfer['asset'][2:]],
                'deposit_amount': transfer['value']
            }
            deposit_dict['deposits'].append(out_dict)
        return deposit_dict

    def deserialize_execute_atomic_swap(self, block, txn, script):
        preimage_original = str(script[0])
        pad_length = int(preimage_original.split()[0][9:]) * 2
        preimage_original = self.zero_pad_if_odd_length_string(preimage_original.split()[1][2:],
                                                               output_size=pad_length)
        preimage = reverse_hex(preimage_original)

        hash_of_secret_original = str(script[1])
        # hashOfSecret
        pad_length = int(hash_of_secret_original.split()[0][9:]) * 2
        hash_of_secret_original = self.zero_pad_if_odd_length_string(hash_of_secret_original.split()[1][2:],
                                                                     output_size=pad_length)
        hash_of_secret = reverse_hex(hash_of_secret_original)

        execute_atomic_swap_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
            'switcheo_transaction_type': 'executeAtomicSwap',
            'hash_of_secret_original': hash_of_secret_original,
            'hash_of_secret': hash_of_secret,
            'preimage_original': preimage_original,
            'preimage': preimage
        }
        return execute_atomic_swap_dict

    def deserialize_fill_offer(self, block, txn, script):
        contract_hash = None
        for s in script:
            if str(s).split()[0] == "APPCALL":         # Needed for v1 Contract with 5 variables in block 2087974; tx: C9741EFBDDF1F43D6B8778B3887EE035D44BE49A5EDD093773BEF2FA231DF31E
                contract_hash = reverse_hex(str(s).split()[1][2:])
        if contract_hash in ['0ec5712e0f7c63e4b0fea31029a28cea5e9d551f', '01bafeeafe62e651efc3a530fde170cf2f7b09bd']:
            # if str(script[0]).startswith('PUSH'):
            use_native_token_original = str(script[0])
            use_native_token = True if use_native_token_original[4:] == 1 else False
            if len(str(script[1]).split()) == 1:
                amount_to_fill_original = str(script[1])
                amount_to_fill = int(str(script[1])[4:])
                amount_to_fill_fixed8 = SwitcheoFixed8(amount_to_fill).ToString()
            else:
                amount_to_fill_original = self.zero_pad_if_odd_length_string(str(script[1]).split()[1][2:]).rjust(8, '0')
                amount_to_fill = int(reverse_hex(amount_to_fill_original), 16)
                amount_to_fill_fixed8 = SwitcheoFixed8(amount_to_fill).ToString()
            offer_hash_original = self.zero_pad_if_odd_length_string(str(script[2]).split()[1][2:]).rjust(64, '0')
            offer_hash = reverse_hex(offer_hash_original)
            trading_pair_original = self.zero_pad_if_odd_length_string(str(script[3]).split()[1][2:]).rjust(104, '0')
            trading_pair = reverse_hex(trading_pair_original)
            taker_address_original = self.zero_pad_if_odd_length_string(str(script[4]).split()[1][2:]).rjust(40, '0')
            taker_address = neo_get_address_from_scripthash(scripthash=reverse_hex(taker_address_original))
            fee_amount_original = None
            fee_amount = None
            fee_amount_fixed8 = None
            fee_asset_original = None
            fee_asset = None          # reverse_hex(fee_asset_original)
            fee_asset_name =  None    # self.neo_token_dict[reverse_hex(fee_asset_original)]
            taker_amount_original = None
            taker_amount = None
            taker_amount_fixed8 = None
            fill_offer_dict = {
                'amount_to_fill_original': amount_to_fill_original,
                'amount_to_fill': amount_to_fill,
                'amount_to_fill_fixed8': amount_to_fill_fixed8,
                'block_hash': block['hash'][2:],
                'block_number': block['index'],
                'block_size': block['size'],
                'block_time': block['time'],
                'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
                'contract_hash': txn['contract_hash'],
                'contract_hash_version': txn['contract_hash_version'],
                'transaction_hash': txn['txid'][2:],
                'transaction_type': txn['type'],
                'switcheo_transaction_type': 'fillOffer',
                'fee_amount_original': fee_amount_original,
                'fee_amount': fee_amount,
                'fee_amount_fixed8': fee_amount_fixed8,
                'fee_asset_original': fee_asset_original,
                'fee_asset': fee_asset,
                'fee_asset_name': fee_asset_name,
                'taker_amount_original': taker_amount_original,
                'taker_amount': taker_amount,
                'taker_amount_fixed8': taker_amount_fixed8,
                'trading_pair_original': trading_pair_original,
                'trading_pair': trading_pair,
                'offer_hash_original': offer_hash_original,
                'offer_hash': offer_hash,
                'taker_address_original': taker_address_original,
                'taker_address': taker_address,
                'use_native_token_original': use_native_token_original,
                'use_native_token': use_native_token
            }
        elif contract_hash == '91b83e96f2a7c4fdf0c1688441ec61986c7cae26':
            script[2] = self.zero_pad_if_odd_length_string(str(script[2]).split()[1][2:])
            script[4] = self.zero_pad_if_odd_length_string(str(script[4]).split()[1][2:]).rjust(64, '0')
            script[5] = self.zero_pad_if_odd_length_string(str(script[5]).split()[1][2:]).rjust(40, '0')
            if len(str(script[1]).split()) == 1 and len(str(script[3]).split()) == 1:  # fillOffer with 1 taker and 0 fee: https://neoscan.io/transaction/B12E71381630318405480D69B868477B136B003F4050F6D1370B1B220DEBAF8D
                fee_amount_original = str(script[1]).split()[0]
                fee_amount = int(fee_amount_original[4:])
                fee_amount_fixed8 = SwitcheoFixed8(fee_amount).ToString()
                taker_amount_original = str(script[3]).split()[0]
                taker_amount = int(taker_amount_original[4:])
                taker_amount_fixed8 = SwitcheoFixed8(taker_amount).ToString()
            elif len(str(script[1]).split()) == 1 and len(str(script[3]).split()) == 2: # https://neoscan.io/transaction/2E7C792B63D281F79AE628EEEE80E180D939F98FBC92BE18F44CEF1A9299D6CC
                fee_amount_original = str(script[1]).split()[0]
                fee_amount = int(fee_amount_original[4:])
                fee_amount_fixed8 = SwitcheoFixed8(fee_amount).ToString()
                taker_amount_original = self.zero_pad_if_odd_length_string(str(script[3]).split()[1][2:]).rjust(16, '0')
                taker_amount = int(reverse_hex(taker_amount_original), 16)
                taker_amount_fixed8 = SwitcheoFixed8(taker_amount).ToString()
            else:
                hex_string = self.zero_pad_if_odd_length_string(str(script[1]).split()[1][2:])
                hex_bytes = int(str(script[1]).split()[0][-1])
                if hex_bytes < 8:
                    fee_amount_original = hex_string.ljust(16, '0')
                elif hex_bytes == 8:
                    fee_amount_original = hex_string.rjust(16, '0')
                else:
                    raise ValueError('Fee Hex Byte amount greater than 8.')
                fee_amount = int(reverse_hex(fee_amount_original), 16)
                fee_amount_fixed8 = SwitcheoFixed8(fee_amount).ToString()
                if len(str(script[3]).split()) == 1:
                    taker_amount_original = str(script[3]).split()[0]
                    taker_amount = int(taker_amount_original[4:])
                    taker_amount_fixed8 = SwitcheoFixed8(taker_amount).ToString()
                else:
                    hex_string = self.zero_pad_if_odd_length_string(str(script[3]).split()[1][2:])
                    hex_bytes = int(str(script[3]).split()[0][-1])
                    if hex_bytes < 8:
                        taker_amount_original = hex_string.ljust(16, '0')
                    elif hex_bytes == 8:
                        taker_amount_original = hex_string.rjust(16, '0')
                    else:
                        raise ValueError('Taker Hex Byte amount greater than 8.')
                    taker_amount = int(reverse_hex(taker_amount_original), 16)
                    taker_amount_fixed8 = SwitcheoFixed8(taker_amount).ToString()
            fill_offer_dict = {
                'block_hash': block['hash'][2:],
                'block_number': block['index'],
                'block_size': block['size'],
                'block_time': block['time'],
                'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
                'contract_hash': txn['contract_hash'],
                'contract_hash_version': txn['contract_hash_version'],
                'transaction_hash': txn['txid'][2:],
                'transaction_type': txn['type'],
                'switcheo_transaction_type': 'fillOffer',
                'fee_amount_original': fee_amount_original,
                'fee_amount': fee_amount,
                'fee_amount_fixed8': fee_amount_fixed8,
                'fee_asset_original': script[2],
                'fee_asset': reverse_hex(script[2]),
                'fee_asset_name': self.neo_token_dict[reverse_hex(script[2])],
                'taker_amount_original': taker_amount_original,
                'taker_amount': taker_amount,
                'taker_amount_fixed8': taker_amount_fixed8,
                'offer_hash_original': self.zero_pad_if_odd_length_string(script[4]),
                'offer_hash': reverse_hex(script[4]),
                'taker_address_original': script[5],
                'taker_address': neo_get_address_from_scripthash(scripthash=reverse_hex(script[5]))
            }
        elif contract_hash in ['a32bcf5d7082f740a4007b16e812cf66a457c3d4', 'b9a70a85136ed73f1f94e83edfee68c00daf412f']:
            maker_fee_burn_original = None
            maker_fee_burn = None
            maker_fee_burn_amount_original = None
            maker_fee_hex_string = None
            maker_fee_burn_amount = None
            maker_fee_burn_amount_fixed8 = None
            taker_fee_burn_original = None
            taker_fee_burn = None
            taker_fee_burn_amount_original = None
            taker_fee_hex_string = None
            taker_fee_burn_amount = None
            taker_fee_burn_amount_fixed8 = None
            taker_fee_asset_original = None
            taker_fee_asset = None
            taker_fee_asset_name = None
            taker_amount_original = None

            maker_fee_burn_original = str(script[0])
            # bool burnMakerFee
            if maker_fee_burn_original == 'PUSH1':
                maker_fee_burn = True
            elif maker_fee_burn_original == 'PUSH0':
                maker_fee_burn = False

            maker_fee_burn_amount_original = str(script[1])
            # BigInteger makerFeeAmount
            if maker_fee_burn_amount_original.startswith('PUSH') and not maker_fee_burn_amount_original.startswith('PUSHBYTES'):
                maker_fee_burn_amount_original = maker_fee_burn_amount_original.split()[0]
                maker_fee_burn_amount = int(maker_fee_burn_amount_original[4:])
                maker_fee_burn_amount_fixed8 = SwitcheoFixed8(maker_fee_burn_amount).ToString()
            else:
                maker_fee_burn_amount_original = self.zero_pad_if_odd_length_string(maker_fee_burn_amount_original.split()[1][2:])
                maker_fee_burn_amount = int(reverse_hex(maker_fee_burn_amount_original), 16)
                maker_fee_burn_amount_fixed8 = SwitcheoFixed8(maker_fee_burn_amount).ToString()

            taker_fee_burn_original = str(script[2])
            # bool burnTakerFee
            if taker_fee_burn_original == 'PUSH1':
                taker_fee_burn = True
            elif taker_fee_burn_original == 'PUSH0':
                taker_fee_burn = False

            taker_fee_burn_amount_original = str(script[3])
            # BigInteger takerFeeAmount
            if taker_fee_burn_amount_original.startswith('PUSH') and not taker_fee_burn_amount_original.startswith('PUSHBYTES'):
                taker_fee_burn_amount_original = taker_fee_burn_amount_original.split()[0]
                taker_fee_burn_amount = int(taker_fee_burn_amount_original[4:])
                taker_fee_burn_amount_fixed8 = SwitcheoFixed8(taker_fee_burn_amount).ToString()
            else:
                taker_fee_burn_amount_original = self.zero_pad_if_odd_length_string(taker_fee_burn_amount_original.split()[1][2:])
                taker_fee_burn_amount = int(reverse_hex(taker_fee_burn_amount_original), 16)
                taker_fee_burn_amount_fixed8 = SwitcheoFixed8(taker_fee_burn_amount).ToString()

            taker_fee_asset_original = str(script[4])
            # byte[] takerFeeAssetID
            pad_length = int(taker_fee_asset_original.split()[0][9:]) * 2
            taker_fee_asset_original = self.zero_pad_if_odd_length_string(taker_fee_asset_original.split()[1][2:],
                                                                          output_size=pad_length)
            taker_fee_asset = reverse_hex(taker_fee_asset_original)
            taker_fee_asset_name = self.neo_token_dict[taker_fee_asset]

            taker_amount_original = str(script[5])
            # BigInteger amountToTake
            if taker_amount_original.startswith('PUSH') and not taker_amount_original.startswith('PUSHBYTES'):
                taker_amount_original = taker_amount_original.split()[0]
                taker_amount = int(taker_amount_original[4:])
                taker_amount_fixed8 = SwitcheoFixed8(taker_amount).ToString()
            else:
                pad_length = int(taker_amount_original.split()[0][9:]) * 2
                taker_amount_original = self.zero_pad_if_odd_length_string(taker_amount_original.split()[1][2:], output_size = pad_length)
                taker_amount = int(reverse_hex(taker_amount_original), 16)
                taker_amount_fixed8 = SwitcheoFixed8(taker_amount).ToString()

            offer_hash_original = self.zero_pad_if_odd_length_string(str(script[6]).split()[1][2:])
            # byte[] offerHash
            offer_hash = reverse_hex(offer_hash_original)

            taker_address_original = str(script[7])
            # byte[] fillerAddress
            pad_length = int(taker_address_original.split()[0][9:]) * 2
            taker_address_original = self.zero_pad_if_odd_length_string(taker_address_original.split()[1][2:],
                                                                        output_size=pad_length)
            taker_address = neo_get_address_from_scripthash(scripthash=reverse_hex(taker_address_original))

            fill_offer_dict = {
                'block_hash': block['hash'][2:],
                'block_number': block['index'],
                'block_size': block['size'],
                'block_time': block['time'],
                'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
                'contract_hash': txn['contract_hash'],
                'contract_hash_version': txn['contract_hash_version'],
                'transaction_hash': txn['txid'][2:],
                'transaction_type': txn['type'],
                'switcheo_transaction_type': 'fillOffer',
                'maker_fee_burn_original': maker_fee_burn_original,
                'maker_fee_burn': maker_fee_burn,
                'maker_fee_burn_amount_original': maker_fee_burn_amount_original,
                'maker_fee_burn_amount': maker_fee_burn_amount,
                'maker_fee_burn_amount_fixed8': maker_fee_burn_amount_fixed8,
                'taker_fee_burn_original': taker_fee_burn_original,
                'taker_fee_burn': taker_fee_burn,
                'taker_fee_burn_amount_original': taker_fee_burn_amount_original,
                'taker_fee_burn_amount': taker_fee_burn_amount,
                'taker_fee_burn_amount_fixed8': taker_fee_burn_amount_fixed8,
                'taker_fee_asset_original': taker_fee_asset_original,
                'taker_fee_asset': taker_fee_asset,
                'taker_fee_asset_name': taker_fee_asset_name,
                'taker_amount_original': taker_amount_original,
                'taker_amount': taker_amount,
                'taker_amount_fixed8': taker_amount_fixed8,
                'offer_hash_original': offer_hash_original,
                'offer_hash': offer_hash,
                'taker_address_original': taker_address_original,
                'taker_address': taker_address
            }
        return fill_offer_dict

    def deserialize_freeze_trading(self, block, txn, script):
        freeze_trading_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
            'switcheo_transaction_type': 'freezeTrading',
            'trade_state_original': str(script[0]),
            'trade_state': 'Inactive' if int(str(script[0])[4:]) == 0 else 'Active'
        }
        return freeze_trading_dict

    def deserizlize_generate_tokens(self, block, txn, script):
        pass

    def deserialize_initialize(self, block, txn, script):
        pass

    def deserialize_make_offer(self, block, txn, script):
        contract_hash = None
        offer_hash = None
        for s in script:
            if str(s).split()[0] == "APPCALL":  # Needed for v1 Contract with 5 variables in block 2087928; tx: E839E289CC8D435EA49EC5FA66427085A10D3D2508FBC164C0BA2DB53BCB0198
                contract_hash = reverse_hex(str(s).split()[1][2:])
        if contract_hash in ['0ec5712e0f7c63e4b0fea31029a28cea5e9d551f', '01bafeeafe62e651efc3a530fde170cf2f7b09bd']:
            want_amount_original = None
            want_amount = None
            want_amount_fixed8 = None
            want_asset_id_original = None
            want_asset_original = None
            want_asset = None
            want_asset_name = None
            offer_amount_original = None
            offer_amount = None
            offer_amount_fixed8 = None
            offer_asset_id_original = None
            offer_asset_original = None
            offer_asset = None
            offer_asset_name = None
            offer_hash_orignal = None
            maker_address_original = None
            maker_address = None
            switcheo_transaction_id_original = self.zero_pad_if_odd_length_string(str(script[4]).split()[1][2:]).rjust(64, '0')
            switcheo_transaction_id = 'v1.1' if contract_hash == '0ec5712e0f7c63e4b0fea31029a28cea5e9d551f' else 'v1.5'
        elif contract_hash == '91b83e96f2a7c4fdf0c1688441ec61986c7cae26':
            want_asset_original = self.zero_pad_if_odd_length_string(str(script[2]).split()[1][2:])
            want_asset = reverse_hex(want_asset_original)
            want_asset_name = self.neo_token_dict[want_asset]
            offer_asset_original = self.zero_pad_if_odd_length_string(str(script[4]).split()[1][2:])
            offer_asset = reverse_hex(offer_asset_original)
            offer_asset_name = self.neo_token_dict[offer_asset]
            maker_address_original = self.zero_pad_if_odd_length_string(str(script[5]).split()[1][2:]).rjust(40, '0')
            maker_address = neo_get_address_from_scripthash(scripthash=reverse_hex(maker_address_original))
            # if script[2] == 'c4cbd934b09e3889e742a357d17b6c6f8e002823' and str(script[1]).split()[0].startswith('PUSH'): # Redeemable Hash Puppies Deposit
            if len(str(script[1]).split()) == 1 and len(str(script[3]).split()) == 1:
                want_amount_original = str(script[1]).split()[0]
                want_amount = int(want_amount_original[4:])
                want_amount_fixed8 = SwitcheoFixed8(want_amount).ToString()
                offer_amount_original = str(script[3]).split()[0]
                offer_amount = int(offer_amount_original[4:])
                offer_amount_fixed8 = SwitcheoFixed8(offer_amount).ToString()
            elif len(str(script[1]).split()) == 1 and len(str(script[3]).split()) == 2:
                want_amount_original = str(script[1]).split()[0]
                want_amount = int(want_amount_original[4:])
                want_amount_fixed8 = SwitcheoFixed8(want_amount).ToString()
                offer_amount_original = self.zero_pad_if_odd_length_string(str(script[3]).split()[1][2:]).rjust(16, '0')
                offer_amount = int(reverse_hex(offer_amount_original), 16)
                offer_amount_fixed8 = SwitcheoFixed8(offer_amount).ToString()
            else:
                hex_string = self.zero_pad_if_odd_length_string(str(script[1]).split()[1][2:])
                hex_bytes = int(str(script[1]).split()[0][-1])
                if hex_bytes < 8:
                    want_amount_original = hex_string.ljust(16, '0')
                elif hex_bytes == 8:
                    want_amount_original = hex_string.rjust(16, '0')
                else:
                    raise ValueError('Want Hex Byte amount greater than 8.')
                want_amount = int(reverse_hex(want_amount_original), 16)
                want_amount_fixed8 = SwitcheoFixed8(want_amount).ToString()
                if len(str(script[3]).split()) == 1:
                    offer_amount_original = str(script[3]).split()[0]
                    offer_amount = int(offer_amount_original[4:])
                    offer_amount_fixed8 = SwitcheoFixed8(offer_amount).ToString()
                else:
                    hex_string = self.zero_pad_if_odd_length_string(str(script[3]).split()[1][2:])
                    hex_bytes = int(str(script[3]).split()[0][-1])
                    if hex_bytes < 8:
                        offer_amount_original = hex_string.ljust(16, '0')
                    elif hex_bytes == 8:
                        offer_amount_original = hex_string.rjust(16, '0')
                    else:
                        raise ValueError('Offer Hex Byte amount greater than 8.')
                    offer_amount = int(reverse_hex(offer_amount_original), 16)
                    offer_amount_fixed8 = SwitcheoFixed8(offer_amount).ToString()
            if len(str(script[0]).split()[1][2:]) == 16:
                switcheo_transaction_id_original = str(script[0]).split()[1][2:]
                switcheo_transaction_id = 'v1'
            else:
                switcheo_transaction_id_original = self.zero_pad_if_odd_length_string(str(script[0]).split()[1][2:]).rjust(72, '0') # Unknown nonce from v1.5: https://neoscan.io/transaction/7BC7A3A2BB81AE772821C79A0357F0B905832852CF3150594FA56B63E5402C24
                switcheo_transaction_id = bytes.fromhex(switcheo_transaction_id_original).decode('utf-8')
                offer_hash = create_offer_hash(neo_address=maker_address,
                                               offer_asset_amt=offer_amount,
                                               offer_asset_hash=offer_asset,
                                               want_asset_amt=want_amount,
                                               want_asset_hash=want_asset,
                                               txn_uuid=switcheo_transaction_id)
        elif contract_hash in ['a32bcf5d7082f740a4007b16e812cf66a457c3d4', 'b9a70a85136ed73f1f94e83edfee68c00daf412f']:
            maker_fee_amount_original = str(script[1])
            # byte[] makerFeeAvailableAmount
            if maker_fee_amount_original.startswith('PUSH') and not maker_fee_amount_original.startswith('PUSHBYTES'):
                maker_fee_amount_original = maker_fee_amount_original.split()[0]
                maker_fee_amount = int(maker_fee_amount_original[4:])
                maker_fee_amount_fixed8 = SwitcheoFixed8(maker_fee_amount).ToString()
            else:
                maker_fee_amount_original = self.zero_pad_if_odd_length_string(maker_fee_amount_original.split()[1][2:])
                maker_fee_amount = int(reverse_hex(maker_fee_amount_original), 16)
                maker_fee_amount_fixed8 = SwitcheoFixed8(maker_fee_amount).ToString()

            maker_fee_asset_original = str(script[2])
            # byte[] makerFeeAssetID
            pad_length = int(maker_fee_asset_original.split()[0][9:]) * 2
            maker_fee_asset_original = self.zero_pad_if_odd_length_string(maker_fee_asset_original.split()[1][2:],
                                                                          output_size=pad_length)
            maker_fee_asset = reverse_hex(maker_fee_asset_original)
            maker_fee_asset_name = self.neo_token_dict[maker_fee_asset]

            want_amount_original = str(script[3])
            # byte[] wantAmount
            if want_amount_original.startswith('PUSH') and not want_amount_original.startswith('PUSHBYTES'):
                want_amount_original = want_amount_original.split()[0]
                want_amount = int(want_amount_original[4:])
                want_amount_fixed8 = SwitcheoFixed8(want_amount).ToString()
            else:
                pad_length = int(want_amount_original.split()[0][9:]) * 2
                want_amount_original = self.zero_pad_if_odd_length_string(want_amount_original.split()[1][2:],
                                                                          output_size=pad_length)
                want_amount = int(reverse_hex(want_amount_original), 16)
                want_amount_fixed8 = SwitcheoFixed8(want_amount).ToString()

            want_asset_original = str(script[4])
            # byte[] wantAssetID
            pad_length = int(want_asset_original.split()[0][9:]) * 2
            want_asset_original = self.zero_pad_if_odd_length_string(want_asset_original.split()[1][2:],
                                                                     output_size=pad_length)
            want_asset = reverse_hex(want_asset_original)
            want_asset_name = self.neo_token_dict[want_asset]

            offer_amount_original = str(script[5])
            # byte[] offerAmount
            if offer_amount_original.startswith('PUSH') and not offer_amount_original.startswith('PUSHBYTES'):
                offer_amount_original = offer_amount_original.split()[0]
                offer_amount = int(offer_amount_original[4:])
                offer_amount_fixed8 = SwitcheoFixed8(offer_amount).ToString()
            else:
                pad_length = int(offer_amount_original.split()[0][9:]) * 2
                offer_amount_original = self.zero_pad_if_odd_length_string(offer_amount_original.split()[1][2:],
                                                                           output_size=pad_length)
                offer_amount = int(reverse_hex(offer_amount_original), 16)
                offer_amount_fixed8 = SwitcheoFixed8(offer_amount).ToString()

            offer_asset_original = str(script[6])
            # byte[] offerAssetID
            pad_length = int(offer_asset_original.split()[0][9:]) * 2
            offer_asset_original = self.zero_pad_if_odd_length_string(offer_asset_original.split()[1][2:],
                                                                      output_size=pad_length)
            offer_asset = reverse_hex(offer_asset_original)
            offer_asset_name = self.neo_token_dict[offer_asset]

            maker_address_original = str(script[7])
            # byte[] makerAddress
            pad_length = int(maker_address_original.split()[0][9:]) * 2
            maker_address_original = self.zero_pad_if_odd_length_string(maker_address_original.split()[1][2:],
                                                                        output_size=pad_length)
            maker_address = neo_get_address_from_scripthash(scripthash=reverse_hex(maker_address_original))

            # byte[] nonce
            switcheo_transaction_id_original = self.zero_pad_if_odd_length_string(str(script[0]).split()[1][2:]).rjust(72, '0')
            switcheo_transaction_id = bytes.fromhex(switcheo_transaction_id_original).decode('utf-8')
            offer_hash = create_offer_hash(neo_address=maker_address,
                                           offer_asset_amt=offer_amount,
                                           offer_asset_hash=offer_asset,
                                           want_asset_amt=want_amount,
                                           want_asset_hash=want_asset,
                                           txn_uuid=switcheo_transaction_id)

        make_offer_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
            'switcheo_transaction_type': 'makeOffer',
            'switcheo_transaction_id_original': switcheo_transaction_id_original,
            'switcheo_transaction_id': switcheo_transaction_id,
            'want_amount_original': want_amount_original,
            'want_amount': want_amount,
            'want_amount_fixed8': want_amount_fixed8,
            'want_asset_original': want_asset_original,
            'want_asset': want_asset,
            'want_asset_name': want_asset_name,
            'offer_amount_original': offer_amount_original,
            'offer_amount': offer_amount,
            'offer_amount_fixed8': offer_amount_fixed8,
            'offer_asset_original': offer_asset_original,
            'offer_asset': offer_asset,
            'offer_asset_name': offer_asset_name,
            'maker_address_original': maker_address_original,
            'maker_address': maker_address,
            'offer_hash': offer_hash
        }
        return make_offer_dict

    def deserialize_mint_tokens(self, block, txn, script):
        pass

    def deserialize_remove_from_whitelist(self, block, txn, script):
        pass

    def deserialize_set_taker_fee(self, block, txn, script):
        # https://neoscan.io/transaction/3BA488FABCAF208C3FA5A8A06CCD9FF03D27291B1C3B826F6D528547F16A3453
        # https://neoscan.io/transaction/3D8A37A29093535C5692A8334CB3ABB4DD8DEE69646D6DFA67CD1EDB57B7200F
        # taker_fee_amount_original = str(script[0]).split()[1][2:]
        # taker_fee_amount = int(reverse_hex(taker_fee_amount_original), 16)
        # taker_fee_amount_fixed8 = SwitcheoFixed8(taker_fee_amount).ToString()
        # # "takerFee".AsByteArray().Concat(assetID)
        # neo_address_original = str(script[2]).split()[1][2:]
        # neo_address = neo_get_address_from_scripthash(reverse_hex(neo_address_original))
        # set_taker_dict = {
        #     'block_hash': block['hash'][2:],
        #     'block_number': block['index'],
        #     'block_size': block['size'],
        #     'block_time': block['time'],
        #     'transaction_hash': txn['txid'][2:],
        #     'transaction_type': txn['type'],
        #     'switcheo_transaction_type': 'withdrawal',
        #     'taker_fee_amount_original': taker_fee_amount_original,
        #     'taker_fee_amount': taker_fee_amount,
        #     'taker_fee_amount_fixed8': taker_fee_amount_fixed8,
        #     'neo_address_original': neo_address_original,
        #     'neo_address': neo_address
        # }
        # return set_taker_dict
        pass

    def deserialize_transfer(self, block, txn, script):
        contract_hash = None
        for s in script:
            if str(s).split()[0] == "APPCALL":  # Needed for v1 Contract with 5 variables in block 2087928; tx: E839E289CC8D435EA49EC5FA66427085A10D3D2508FBC164C0BA2DB53BCB0198
                contract_hash = reverse_hex(str(s).split()[1][2:])
        if contract_hash == '78e6d16b914fe15bc16150aeb11d0c2a8e532bdd':
            transfer_dict = {
                'block_hash': block['hash'][2:],
                'block_number': block['index'],
                'block_size': block['size'],
                'block_time': block['time'],
                'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
                'contract_hash': txn['contract_hash'],
                'contract_hash_version': txn['contract_hash_version'],
                'transaction_hash': txn['txid'][2:],
                'transaction_type': txn['type'],
                'switcheo_transaction_type': 'transfer',
                'contract_hash': contract_hash
            }
            return transfer_dict
        elif contract_hash in ['a32bcf5d7082f740a4007b16e812cf66a457c3d4', 'b9a70a85136ed73f1f94e83edfee68c00daf412f', '91b83e96f2a7c4fdf0c1688441ec61986c7cae26', '01bafeeafe62e651efc3a530fde170cf2f7b09bd', 'ab38352559b8b203bde5fddfa0b07d8b2525e132']:
            transfer_index = 0
            if str(script[1]).split()[0] == 'DROP':
                transfer_index = 2
            if len(str(script[transfer_index]).split()) == 1:
                transfer_amount_original = str(script[transfer_index]).split()[0]
                transfer_amount = int(transfer_amount_original[4:])
                transfer_amount_fixed8 = transfer_amount
            elif transfer_index == 0 and str(script[transfer_index]).split()[0][9:] != '8':
                pad_length = int(str(script[transfer_index]).split()[0][9:]) * 2
                transfer_hex_pad = self.zero_pad_if_odd_length_string(str(script[transfer_index]).split()[1][2:], output_size=pad_length)
                transfer_amount_original = self.zero_pad_if_odd_length_string(reverse_hex(transfer_hex_pad), output_size=16)
                transfer_amount = int(transfer_amount_original, 16)
                transfer_amount_fixed8 = SwitcheoFixed8(transfer_amount).ToString()
            elif transfer_index == 2 and str(script[transfer_index]).split()[0][9:] != '8':
                pad_length = int(str(script[transfer_index]).split()[0][9:]) * 2
                transfer_hex_pad = self.zero_pad_if_odd_length_string(str(script[transfer_index]).split()[1][2:], output_size=pad_length)
                transfer_amount_original = self.zero_pad_if_odd_length_string(reverse_hex(transfer_hex_pad), output_size=16)
                transfer_amount = int(transfer_amount_original, 16)
                transfer_amount_fixed8 = SwitcheoFixed8(transfer_amount).ToString()
            else:
                hex_string = self.zero_pad_if_odd_length_string(str(script[transfer_index]).split()[1][2:])
                hex_bytes = int(str(script[transfer_index]).split()[0][-1])
                if hex_bytes < 8:
                    transfer_amount_original = hex_string.ljust(16, '0')
                elif hex_bytes == 8:
                    transfer_amount_original = hex_string.rjust(16, '0')
                else:
                    raise ValueError('Transfer Hex Byte amount greater than 8.')
                transfer_amount = int(reverse_hex(transfer_amount_original), 16)
                transfer_amount_fixed8 = SwitcheoFixed8(transfer_amount).ToString()
            to_address_original = self.zero_pad_if_odd_length_string(str(script[transfer_index + 1]).split()[1][2:], output_size=40)
            from_address_original = self.zero_pad_if_odd_length_string(str(script[transfer_index + 2]).split()[1][2:], output_size=40)
            transfer_dict = {
                'block_hash': block['hash'][2:],
                'block_number': block['index'],
                'block_size': block['size'],
                'block_time': block['time'],
                'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
                'contract_hash': txn['contract_hash'],
                'contract_hash_version': txn['contract_hash_version'],
                'transaction_hash': txn['txid'][2:],
                'transaction_type': txn['type'],
                'switcheo_transaction_type': 'transfer',
                'transfer_amount_original': transfer_amount_original,
                'transfer_amount': transfer_amount,
                'transfer_amount_fixed8': transfer_amount_fixed8,
                'to_address_original': to_address_original,
                'to_address': neo_get_address_from_scripthash(scripthash=reverse_hex(to_address_original)),
                'from_address_original': from_address_original,
                'from_address': neo_get_address_from_scripthash(scripthash=reverse_hex(from_address_original))
            }
            return transfer_dict

    def deserialize_unfreeze_trading(self, block, txn, script):
        unfreeze_trading_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
            'switcheo_transaction_type': 'unfreezeTrading',
            'trade_state_original': str(script[0]),
            'trade_state': 'Active' if int(str(script[0])[4:]) == 1 else 'Inactive'
        }
        return unfreeze_trading_dict

    def deserialize_withdraw(self, block, txn, script):
        withdraw_dict = {
            'block_hash': block['hash'][2:],
            'block_number': block['index'],
            'block_size': block['size'],
            'block_time': block['time'],
            'block_date': datetime.datetime.utcfromtimestamp(block['time']).strftime('%Y-%m-%d'),
            'contract_hash': txn['contract_hash'],
            'contract_hash_version': txn['contract_hash_version'],
            'transaction_hash': txn['txid'][2:],
            'transaction_type': txn['type'],
            'switcheo_transaction_type': 'withdrawal',
            'withdrawals': []
        }
        for transfer in txn['vout']:
            withdrawal_dict = {
                'withdraw_address': transfer['address'],
                'withdraw_asset': transfer['asset'],
                'withdraw_asset_name': self.neo_token_dict[transfer['asset'][2:]],
                'withdraw_amount': transfer['value']
            }
            withdraw_dict['withdrawals'].append(withdrawal_dict)
        return withdraw_dict

    def deserialize_withdraw_assets(self, block, txn, script):
        pass

    def deserialize_withdrawal(self, block, txn, script):
        pass

    def ingest_missing_neo_blocks(self):
        neo_block_start_height = 2000000
        self.neo_rpc_client = self.get_neo_node()
        neo_block_height = self.get_neo_block_height()
        switcheo_blocks_ingested = self.ni.get_collection_count(collection='blocks')
        switcheo_blocks_ingested_offset = switcheo_blocks_ingested + neo_block_start_height
        switcheo_blocks_ingested_list = set(range(neo_block_start_height, switcheo_blocks_ingested_offset))
        missing_blocks = self.ni.get_missing_blocks(block_height=neo_block_height,
                                                    block_offset=neo_block_start_height,
                                                    blocks_ingested=switcheo_blocks_ingested,
                                                    blocks_ingested_list=switcheo_blocks_ingested_list)
        missing_blocks.sort()
        for block_number_chunk in self.chunk_list(input_list=missing_blocks, chunk_size=10):
            neo_blocks = self.get_neo_bulk_blocks(block_number_list=block_number_chunk)
            self.ingest_switcheo_transactions(neo_blocks=neo_blocks)

    def ingest_switcheo_transactions(self, neo_blocks):
        for neo_block in neo_blocks:
            for transaction in neo_block['tx']:
                switcheo_transaction = self.deserialize_transaction(neo_block, transaction)
                print(switcheo_transaction)
                if switcheo_transaction is not None:
                    self.switcheo_transactions.append(switcheo_transaction)
                    if switcheo_transaction['switcheo_transaction_type'] == 'fillOffer':
                        self.switcheo_fees.append(switcheo_transaction)
                    if switcheo_transaction['switcheo_transaction_type'] in ['freezeTrading', 'unfreezeTrading']:
                        self.switcheo_freezes.append(switcheo_transaction)
                    if switcheo_transaction['switcheo_transaction_type'] in ['cancel', 'fillOffer', 'makeOffer']:
                        self.deserialize_offer_hash(txn=switcheo_transaction)
                    # if switcheo_transaction['switcheo_transaction_type'] in ['deposit', 'fillOffer', 'makeOffer', 'transfer']:
                    #     self.address_stats(txns=[switcheo_transaction], txn_date=switcheo_transaction['block_date'])
                if len(self.switcheo_transactions) % 10 == 0:
                    self.ni.mongo_upsert_many(collection='transactions', upsert_list_dict=self.switcheo_transactions)
                    self.switcheo_transactions.clear()
                    self.ni.mongo_upsert_many(collection='fees', upsert_list_dict=self.switcheo_fees)
                    self.switcheo_fees.clear()
                    self.ni.mongo_upsert_many(collection='freezes', upsert_list_dict=self.switcheo_freezes)
                    self.switcheo_freezes.clear()
        if len(self.switcheo_transactions) % 10 != 0:
            self.ni.mongo_upsert_many(collection='transactions', upsert_list_dict=self.switcheo_transactions)
            self.ni.mongo_upsert_many(collection='fees', upsert_list_dict=self.switcheo_fees)
            self.ni.mongo_upsert_many(collection='freezes', upsert_list_dict=self.switcheo_freezes)
        self.ni.mongo_upsert_many(collection='blocks', upsert_list_dict=neo_blocks)

    def deserialize_offer_hash(self, txn):
        return self.offer_hash_functions[txn['switcheo_transaction_type']](txn)

    def offer_hash_cancel(self, txn):
        return self.ni.mongo_db['offer_hash'].update_one(
                filter={'_id': txn['offer_hash']},
                update={
                    '$set':
                        {
                            'cancel_txn': txn,
                            'status': 'closed',
                            'maker_amount_open': 0
                        }
                },
                upsert=True
            )

    def offer_hash_make(self, txn):
        txn['_id'] = txn['offer_hash']
        txn['status'] = 'open'
        txn['maker_amount_open'] = txn['offer_amount']
        txn['amount_filled'] = 0
        return self.ni.mongo_db['offer_hash'].update_one(
                filter={'_id': txn['_id']},
                update={'$set': txn},
                upsert=True
            )

    def offer_hash_fill(self, txn):
        self.ni.mongo_db['offer_hash'].update_one(
            filter={'_id': txn['offer_hash']},
            update={
                '$addToSet': {
                    'fill_txns': {
                        '$each': [txn]
                    }
                }
            },
            upsert=True
        )
        offer_hash = self.ni.mongo_db['offer_hash'].find_one({'_id': txn['offer_hash']})
        print(offer_hash)
        if 'maker_amount_open' in offer_hash and offer_hash['maker_amount_open'] is not None and txn['taker_amount'] is not None:
            maker_amount_open = int(offer_hash['maker_amount_open']) - txn['taker_amount']
        elif txn['taker_amount'] is not None:
            maker_amount_open = 0 - txn['taker_amount']
        else:
            maker_amount_open = None
        if 'amount_filled' in offer_hash and offer_hash['amount_filled'] is not None and txn['taker_amount'] is not None:
            amount_filled = int(offer_hash['amount_filled']) + txn['taker_amount']
        elif txn['taker_amount'] is not None:
            amount_filled = txn['taker_amount']
        else:
            amount_filled = None
        # if maker_amount_open == 0:
        #     return self.ni.mongo_db['offer_hash'].update_one(
        #             filter={'_id': txn['offer_hash']},
        #             update={
        #                 '$set':
        #                     {
        #                         'status': 'filled',
        #                         'maker_amount_open': 0,
        #                         'amount_filled': amount_filled,
        #                     }
        #             },
        #             upsert=True
        #         )
        # else:
        #     print(txn)
        #     print(maker_amount_open)
        #     print(amount_filled)
        #     return self.ni.mongo_db['offer_hash'].update_one(
        #             filter={'_id': txn['offer_hash']},
        #             update={
        #                 '$set':
        #                     {
        #                         'maker_amount_open': maker_amount_open,
        #                         'amount_filled': amount_filled,
        #                     }
        #             },
        #             upsert=True
        #         )

    def deserialize_address(self, txn):
        return self.address_functions[txn['switcheo_transaction_type']](txn)

    def address_cancel(self, txn):
        offer_hash = self.ni.mongo_db['offer_hash'].find_one({'_id': txn['offer_hash']})
        if 'maker_address' in offer_hash:
            cancel = {
                'block_date': txn['block_date'],
                'block_number': txn['block_number'],
                'block_time': txn['block_time'],
                'offer_hash': txn['offer_hash'],
                'transaction_hash': txn['transaction_hash'],
                # 'amount_filled': offer_hash['amount_filled'],
                'offer_amount': offer_hash['offer_amount'],
                'offer_amount_fixed8': offer_hash['offer_amount_fixed8'],
                'offer_asset_name': offer_hash['offer_asset_name'],
                'want_amount': offer_hash['want_amount'],
                'want_amount_fixed8': offer_hash['want_amount_fixed8'],
                'want_asset_name': offer_hash['want_asset_name']
            }
            address = offer_hash['maker_address']
            return self.ni.mongo_db['addresses'].update_one(
                filter={'_id': address},
                update={
                    '$addToSet': {
                        'cancels': {
                            '$each': [cancel]
                        }
                    }
                },
                upsert=True
            )

    def address_deposit(self, txn):
        balance = {}
        # address = self.ni.mongo_db['addresses'].find_one({'_id': })
        # if address is None:
        #     address = {
        #         '_id': txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
            #          txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
            # }
        deposit = {
            'block_date': txn['block_date'],
            'block_number': txn['block_number'],
            'block_time': txn['block_time'],
            'deposit_amount': txn['deposit_amount'],
            'deposit_amount_fixed8': txn['deposit_amount_fixed8'],
            'deposit_asset_name': txn['deposit_asset_name'],
            'transaction_hash': txn['transaction_hash']
        }
        address = txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
        return self.ni.mongo_db['addresses'].update_one(
            filter={'_id': address},
            update={
                '$addToSet': {
                    'deposits': {
                        '$each': [deposit]
                    }
                }
            },
            upsert=True
        )
        # if 'balance' not in address:
        #     address['balance'] = []
        #     balance['asset_amount'] = deposit['deposit_amount']
        #     balance['asset_name'] = deposit['deposit_asset_name']
        #     address['balance'].append(balance)
        # else:
        #     i = 0
        #     asset_exists = False
        #     for asset in address['balance']:
        #         i += 1
        #         if asset['asset_name'] == deposit['deposit_asset_name']:
        #             asset_exists = True
        #             address['balance'][i]['asset_name'] = asset['asset_amount'] + deposit['deposit_amount']
        #             break
        #     if not asset_exists:
        #         balance['asset_amount'] = deposit['deposit_amount']
        #         balance['asset_name'] = deposit['deposit_asset_name']
        #         address['balance'].append(balance)
        # if 'stats' not in address:
        #     address['stats'] = {}
        # address['stats']['deposits'] = len(address['deposits'])
        # return address

    def address_fill(self, txn):
        if txn['taker_amount'] is not None:
            # print(txn)
            # address = self.ni.mongo_db['addresses'].find_one(
            #     {'_id': txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]})
            # if address is None:
            #     address = {
            #         '_id': txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
            #     }
            # print(address)
            offer_hash = self.ni.mongo_db['offer_hash'].find_one({'_id': txn['offer_hash']})
            if 'want_amount' in offer_hash:
                fill = {
                    'block_date': txn['block_date'],
                    'block_number': txn['block_number'],
                    'block_time': txn['block_time'],
                    'fee_amount': txn['fee_amount'],
                    'fee_amount_fixed8': txn['fee_amount_fixed8'],
                    'fee_asset_name': txn['fee_asset_name'],
                    'offer_hash': txn['offer_hash'],
                    'taker_amount': txn['taker_amount'],
                    'taker_amount_fixed8': txn['taker_amount_fixed8'],
                    'taker_address': txn[self.address_transaction_dict[txn['switcheo_transaction_type']]],
                    'transaction_hash': txn['transaction_hash'],
                    'maker_address': offer_hash['maker_address'],
                    'maker_offer_amount': offer_hash['offer_amount'],
                    'maker_offer_amount_fixed8': offer_hash['offer_amount_fixed8'],
                    'maker_offer_asset_name': offer_hash['offer_asset_name'],
                    'maker_want_amount': offer_hash['want_amount'],
                    'maker_want_amount_fixed8': offer_hash['want_amount_fixed8'],
                    'maker_want_asset_name': offer_hash['want_asset_name']
                }
            else:
                fill = {
                    'block_date': txn['block_date'],
                    'block_number': txn['block_number'],
                    'block_time': txn['block_time'],
                    'fee_amount': txn['fee_amount'],
                    'fee_amount_fixed8': txn['fee_amount_fixed8'],
                    'fee_asset_name': txn['fee_asset_name'],
                    'offer_hash': txn['offer_hash'],
                    'taker_amount': txn['taker_amount'],
                    'taker_amount_fixed8': txn['taker_amount_fixed8'],
                    'taker_address': txn[self.address_transaction_dict[txn['switcheo_transaction_type']]],
                    'transaction_hash': txn['transaction_hash']
                }
            address = txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
            return self.ni.mongo_db['addresses'].update_one(
                filter={'_id': address},
                update={
                    '$addToSet': {
                        'fills': {
                            '$each': [fill]
                        }
                    }
                },
                upsert=True
            )

    def address_make(self, txn):
        make = {
            'block_date': txn['block_date'],
            'block_number': txn['block_number'],
            'block_time': txn['block_time'],
            'offer_hash': txn['offer_hash'],
            'offer_amount': txn['offer_amount'],
            'offer_amount_fixed8': txn['offer_amount_fixed8'],
            'offer_asset_name': txn['offer_asset_name'],
            'offer_ratio': round(txn['want_amount'] / txn['offer_amount'], 8),
            'want_amount': txn['want_amount'],
            'want_amount_fixed8': txn['want_amount_fixed8'],
            'want_asset_name': txn['want_asset_name'],
            'transaction_hash': txn['transaction_hash']
        }
        address = txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
        return self.ni.mongo_db['addresses'].update_one(
            filter={'_id': address},
            update={
                '$addToSet': {
                    'makes': {
                        '$each': [make]
                    }
                }
            },
            upsert=True
        )

    def address_withdrawal(self, txn):
        withdraw = {
            'block_date': txn['block_date'],
            'block_number': txn['block_number'],
            'block_time': txn['block_time'],
            'withdrawals': []
        }
        for withdrawal in txn['withdrawals']:
            withdraw_dict = {
                'withdraw_address': withdrawal['withdraw_address'],
                'withdraw_asset_name': withdrawal['withdraw_asset_name'],
                'withdraw_amount': withdrawal['withdraw_amount']
            }
            withdraw['withdrawals'].append(withdraw_dict)
        address = txn['withdrawals'][0][self.address_transaction_dict[txn['switcheo_transaction_type']]]
        return self.ni.mongo_db['addresses'].update_one(
            filter={'_id': address},
            update={
                '$addToSet': {
                    'withdrawals': {
                        '$each': [withdraw]
                    }
                }
            },
            upsert=True
        )

    def address_stats(self, txns, txn_date):
        addresses = {}
        address_transactions = []
        for txn in txns:
            if txn['switcheo_transaction_type'] == 'fillOffer' and txn['fee_amount_original'] != 'PUSH0':
                offer_hash = self.ni.mongo_db['offer_hash'].find_one({'_id': txn['offer_hash']})
                try:
                    maker_address = offer_hash['maker_address']
                except KeyError:
                    continue
                trade_pair = offer_hash['offer_asset_name'] + "_" + offer_hash['want_asset_name']
                if trade_pair not in self.neo_trade_pair_list:
                    trade_pair = offer_hash['want_asset_name'] + "_" + offer_hash['offer_asset_name']
                    if trade_pair not in self.neo_trade_pair_list:
                        exit("Incorrect trade pair - " + trade_pair)
                taker_address = txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
                addresses[taker_address] = self.ni.mongo_db['addresses'].find_one({'_id': taker_address})
                addresses[maker_address] = self.ni.mongo_db['addresses'].find_one({'_id': maker_address})
                taker_address_date = (taker_address, txn_date)
                taker_address_date_dict = {'address': taker_address, 'date': txn_date}
                maker_address_date = (maker_address, txn_date)
                maker_address_date_dict = {'address': maker_address, 'date': txn_date}
                addresses[taker_address_date] = self.ni.mongo_db['addresses_date'].find_one({'_id': taker_address_date_dict})
                addresses[maker_address_date] = self.ni.mongo_db['addresses_date'].find_one({'_id': maker_address_date_dict})
                if addresses[taker_address] is None:
                    addresses[taker_address] = {}
                if addresses[taker_address_date] is None:
                    addresses[taker_address_date] = {}
                if 'fees_paid' not in addresses[taker_address]:
                    addresses[taker_address]['fees_paid'] = {}
                if 'fees_paid' not in addresses[taker_address_date]:
                    addresses[taker_address_date]['fees_paid'] = {}
                if 'trade_count' not in addresses[taker_address]:
                    addresses[taker_address]['trade_count'] = {}
                if 'trade_count' not in addresses[taker_address_date]:
                    addresses[taker_address_date]['trade_count'] = {}
                if 'amount_traded' not in addresses[taker_address]:
                    addresses[taker_address]['amount_traded'] = {}
                if 'amount_traded' not in addresses[taker_address_date]:
                    addresses[taker_address_date]['amount_traded'] = {}
                if 'total_amount_traded' not in addresses[taker_address]:
                    addresses[taker_address]['total_amount_traded'] = {}
                if 'total_amount_traded' not in addresses[taker_address_date]:
                    addresses[taker_address_date]['total_amount_traded'] = {}
                if 'asset_balance' not in addresses[taker_address]:
                    addresses[taker_address]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'asset_balance' not in addresses[taker_address_date]:
                    addresses[taker_address_date]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'trade_type_count' not in addresses[taker_address]:
                    addresses[taker_address]['trade_type_count'] = {}
                if 'trade_type_count' not in addresses[taker_address_date]:
                    addresses[taker_address_date]['trade_type_count'] = {}
                if 'makes' not in addresses[taker_address]:
                    addresses[taker_address]['makes'] = {}
                if 'makes' not in addresses[taker_address_date]:
                    addresses[taker_address_date]['makes'] = {}
                if 'takes' not in addresses[taker_address]:
                    addresses[taker_address]['takes'] = {}
                if 'takes' not in addresses[taker_address_date]:
                    addresses[taker_address_date]['takes'] = {}

                if addresses[maker_address] is None:
                    addresses[maker_address] = {}
                if addresses[maker_address_date] is None:
                    addresses[maker_address_date] = {}
                if 'fees_paid' not in addresses[maker_address]:
                    addresses[maker_address]['fees_paid'] = {}
                if 'fees_paid' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['fees_paid'] = {}
                if 'trade_count' not in addresses[maker_address]:
                    addresses[maker_address]['trade_count'] = {}
                if 'trade_count' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['trade_count'] = {}
                if 'amount_traded' not in addresses[maker_address]:
                    addresses[maker_address]['amount_traded'] = {}
                if 'amount_traded' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['amount_traded'] = {}
                if 'total_amount_traded' not in addresses[maker_address]:
                    addresses[maker_address]['total_amount_traded'] = {}
                if 'total_amount_traded' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['total_amount_traded'] = {}
                if 'asset_balance' not in addresses[maker_address]:
                    addresses[maker_address]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'asset_balance' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'trade_type_count' not in addresses[maker_address]:
                    addresses[maker_address]['trade_type_count'] = {}
                if 'trade_type_count' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['trade_type_count'] = {}
                if 'makes' not in addresses[maker_address]:
                    addresses[maker_address]['makes'] = {}
                if 'makes' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['makes'] = {}
                if 'takes' not in addresses[maker_address]:
                    addresses[maker_address]['takes'] = {}
                if 'takes' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['takes'] = {}

            elif txn['switcheo_transaction_type'] == 'makeOffer':
                maker_address = txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
                addresses[maker_address] = self.ni.mongo_db['addresses'].find_one({'_id': maker_address})
                maker_address_date = (maker_address, txn_date)
                maker_address_date_dict = {'address': maker_address, 'date': txn_date}
                addresses[maker_address_date] = self.ni.mongo_db['addresses_date'].find_one({'_id': maker_address_date_dict})
                if addresses[maker_address] is None:
                    addresses[maker_address] = {}
                if addresses[maker_address_date] is None:
                    addresses[maker_address_date] = {}
                if 'fees_paid' not in addresses[maker_address]:
                    addresses[maker_address]['fees_paid'] = {}
                if 'fees_paid' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['fees_paid'] = {}
                if 'trade_count' not in addresses[maker_address]:
                    addresses[maker_address]['trade_count'] = {}
                if 'trade_count' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['trade_count'] = {}
                if 'amount_traded' not in addresses[maker_address]:
                    addresses[maker_address]['amount_traded'] = {}
                if 'amount_traded' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['amount_traded'] = {}
                if 'total_amount_traded' not in addresses[maker_address]:
                    addresses[maker_address]['total_amount_traded'] = {}
                if 'total_amount_traded' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['total_amount_traded'] = {}
                if 'asset_balance' not in addresses[maker_address]:
                    addresses[maker_address]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'asset_balance' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'trade_type_count' not in addresses[maker_address]:
                    addresses[maker_address]['trade_type_count'] = {}
                if 'trade_type_count' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['trade_type_count'] = {}
                if 'makes' not in addresses[maker_address]:
                    addresses[maker_address]['makes'] = {}
                if 'makes' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['makes'] = {}
                if 'takes' not in addresses[maker_address]:
                    addresses[maker_address]['takes'] = {}
                if 'takes' not in addresses[maker_address_date]:
                    addresses[maker_address_date]['takes'] = {}
                try:
                    trade_pair = txn['offer_asset_name'] + "_" + txn['want_asset_name']
                except TypeError:
                    continue
                if trade_pair not in self.neo_trade_pair_list:
                    trade_pair = txn['want_asset_name'] + "_" + txn['offer_asset_name']
                    if trade_pair not in self.neo_trade_pair_list:
                        exit("Incorrect trade pair - " + trade_pair)

            if txn['switcheo_transaction_type'] == 'fillOffer':
                if txn['taker_amount'] is not None:
                    if txn['fee_amount_original'] == 'PUSH0':
                        offer_hash = []
                    if 'want_amount' in offer_hash:
                        offer_ratio = round(int(offer_hash['want_amount']) / int(offer_hash['offer_amount']), 8)
                        # Taker Fees Paid
                        if txn['fee_asset_name'] not in addresses[taker_address]['fees_paid']:
                            addresses[taker_address]['fees_paid'][txn['fee_asset_name']] = txn['fee_amount']
                        else:
                            addresses[taker_address]['fees_paid'][txn['fee_asset_name']] += txn['fee_amount']
                        if txn['fee_asset_name'] not in addresses[taker_address_date]['fees_paid']:
                            addresses[taker_address_date]['fees_paid'][txn['fee_asset_name']] = txn['fee_amount']
                        else:
                            addresses[taker_address_date]['fees_paid'][txn['fee_asset_name']] += txn['fee_amount']

                        # Number of Taker Trades (fills)
                        if trade_pair not in addresses[taker_address]['trade_count']:
                            addresses[taker_address]['trade_count'][trade_pair] = 1
                        else:
                            addresses[taker_address]['trade_count'][trade_pair] += 1
                        if trade_pair not in addresses[taker_address_date]['trade_count']:
                            addresses[taker_address_date]['trade_count'][trade_pair] = 1
                        else:
                            addresses[taker_address_date]['trade_count'][trade_pair] += 1

                        # Number of Maker Trades (fills)
                        if trade_pair not in addresses[maker_address]['trade_count']:
                            addresses[maker_address]['trade_count'][trade_pair] = 1
                        else:
                            addresses[maker_address]['trade_count'][trade_pair] += 1
                        if trade_pair not in addresses[maker_address_date]['trade_count']:
                            addresses[maker_address_date]['trade_count'][trade_pair] = 1
                        else:
                            addresses[maker_address_date]['trade_count'][trade_pair] += 1

                        # Amount of Taker Tokens Traded (filled)
                        if offer_hash['want_asset_name'] not in addresses[taker_address]['amount_traded']:
                            addresses[taker_address]['amount_traded'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[taker_address]['amount_traded'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)
                        if offer_hash['want_asset_name'] not in addresses[taker_address_date]['amount_traded']:
                            addresses[taker_address_date]['amount_traded'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[taker_address_date]['amount_traded'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)

                        if offer_hash['want_asset_name'] not in addresses[taker_address]['total_amount_traded']:
                            addresses[taker_address]['total_amount_traded'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[taker_address]['total_amount_traded'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)
                        if offer_hash['want_asset_name'] not in addresses[taker_address_date]['total_amount_traded']:
                            addresses[taker_address_date]['total_amount_traded'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[taker_address_date]['total_amount_traded'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)

                        if offer_hash['offer_asset_name'] not in addresses[taker_address]['total_amount_traded']:
                            addresses[taker_address]['total_amount_traded'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[taker_address]['total_amount_traded'][offer_hash['offer_asset_name']] += txn['taker_amount']
                        if offer_hash['offer_asset_name'] not in addresses[taker_address_date]['total_amount_traded']:
                            addresses[taker_address_date]['total_amount_traded'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[taker_address_date]['total_amount_traded'][offer_hash['offer_asset_name']] += txn['taker_amount']

                        # Amount of Maker Tokens Traded (filled)
                        if offer_hash['offer_asset_name'] not in addresses[maker_address]['amount_traded']:
                            addresses[maker_address]['amount_traded'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[maker_address]['amount_traded'][offer_hash['offer_asset_name']] += txn['taker_amount']
                        if offer_hash['offer_asset_name'] not in addresses[maker_address_date]['amount_traded']:
                            addresses[maker_address_date]['amount_traded'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[maker_address_date]['amount_traded'][offer_hash['offer_asset_name']] += txn['taker_amount']

                        if offer_hash['offer_asset_name'] not in addresses[maker_address]['total_amount_traded']:
                            addresses[maker_address]['total_amount_traded'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[maker_address]['total_amount_traded'][offer_hash['offer_asset_name']] += txn['taker_amount']
                        if offer_hash['offer_asset_name'] not in addresses[maker_address_date]['total_amount_traded']:
                            addresses[maker_address_date]['total_amount_traded'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[maker_address_date]['total_amount_traded'][offer_hash['offer_asset_name']] += txn['taker_amount']

                        if offer_hash['want_asset_name'] not in addresses[maker_address]['total_amount_traded']:
                            addresses[maker_address]['total_amount_traded'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[maker_address]['total_amount_traded'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)
                        if offer_hash['want_asset_name'] not in addresses[maker_address_date]['total_amount_traded']:
                            addresses[maker_address_date]['total_amount_traded'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[maker_address_date]['total_amount_traded'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)

                        # Increment Balance of Taker Account
                        if offer_hash['offer_asset_name'] not in addresses[taker_address]['asset_balance']['smart_contract']:
                            addresses[taker_address]['asset_balance']['smart_contract'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[taker_address]['asset_balance']['smart_contract'][offer_hash['offer_asset_name']] += txn['taker_amount']
                        if offer_hash['offer_asset_name'] not in addresses[taker_address_date]['asset_balance']['smart_contract']:
                            addresses[taker_address_date]['asset_balance']['smart_contract'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[taker_address_date]['asset_balance']['smart_contract'][offer_hash['offer_asset_name']] += txn['taker_amount']

                        if offer_hash['offer_asset_name'] not in addresses[taker_address]['asset_balance']['total']:
                            addresses[taker_address]['asset_balance']['total'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[taker_address]['asset_balance']['total'][offer_hash['offer_asset_name']] += txn['taker_amount']
                        if offer_hash['offer_asset_name'] not in addresses[taker_address_date]['asset_balance']['total']:
                            addresses[taker_address_date]['asset_balance']['total'][offer_hash['offer_asset_name']] = txn['taker_amount']
                        else:
                            addresses[taker_address_date]['asset_balance']['total'][offer_hash['offer_asset_name']] += txn['taker_amount']

                        # Decrement Balance of Taker Account
                        if offer_hash['want_asset_name'] not in addresses[taker_address]['asset_balance']['smart_contract']:
                            addresses[taker_address]['asset_balance']['smart_contract'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio * -1)
                        else:
                            addresses[taker_address]['asset_balance']['smart_contract'][offer_hash['want_asset_name']] -= int(txn['taker_amount'] * offer_ratio)
                        if offer_hash['want_asset_name'] not in addresses[taker_address_date]['asset_balance']['smart_contract']:
                            addresses[taker_address_date]['asset_balance']['smart_contract'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio * -1)
                        else:
                            addresses[taker_address_date]['asset_balance']['smart_contract'][offer_hash['want_asset_name']] -= int(txn['taker_amount'] * offer_ratio)

                        if offer_hash['want_asset_name'] not in addresses[taker_address]['asset_balance']['total']:
                            addresses[taker_address]['asset_balance']['total'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio * -1)
                        else:
                            addresses[taker_address]['asset_balance']['total'][offer_hash['want_asset_name']] -= int(txn['taker_amount'] * offer_ratio)
                        if offer_hash['want_asset_name'] not in addresses[taker_address_date]['asset_balance']['total']:
                            addresses[taker_address_date]['asset_balance']['total'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio * -1)
                        else:
                            addresses[taker_address_date]['asset_balance']['total'][offer_hash['want_asset_name']] -= int(txn['taker_amount'] * offer_ratio)

                        if txn['fee_asset_name'] not in addresses[taker_address]['asset_balance']['smart_contract']:
                            addresses[taker_address]['asset_balance']['smart_contract'][txn['fee_asset_name']] = int(txn['fee_amount'] * -1)
                        else:
                            addresses[taker_address]['asset_balance']['smart_contract'][txn['fee_asset_name']] -= txn['fee_amount']
                        if txn['fee_asset_name'] not in addresses[taker_address_date]['asset_balance']['smart_contract']:
                            addresses[taker_address_date]['asset_balance']['smart_contract'][txn['fee_asset_name']] = int(txn['fee_amount'] * -1)
                        else:
                            addresses[taker_address_date]['asset_balance']['smart_contract'][txn['fee_asset_name']] -= txn['fee_amount']

                        if txn['fee_asset_name'] not in addresses[taker_address]['asset_balance']['total']:
                            addresses[taker_address]['asset_balance']['total'][txn['fee_asset_name']] = int(txn['fee_amount'] * -1)
                        else:
                            addresses[taker_address]['asset_balance']['total'][txn['fee_asset_name']] -= txn['fee_amount']
                        if txn['fee_asset_name'] not in addresses[taker_address_date]['asset_balance']['total']:
                            addresses[taker_address_date]['asset_balance']['total'][txn['fee_asset_name']] = int(txn['fee_amount'] * -1)
                        else:
                            addresses[taker_address_date]['asset_balance']['total'][txn['fee_asset_name']] -= txn['fee_amount']

                        # Increment Balance of Maker Account
                        if offer_hash['want_asset_name'] not in addresses[maker_address]['asset_balance']['smart_contract']:
                            addresses[maker_address]['asset_balance']['smart_contract'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[maker_address]['asset_balance']['smart_contract'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)
                        if offer_hash['want_asset_name'] not in addresses[maker_address_date]['asset_balance']['smart_contract']:
                            addresses[maker_address_date]['asset_balance']['smart_contract'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[maker_address_date]['asset_balance']['smart_contract'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)

                        if offer_hash['want_asset_name'] not in addresses[maker_address]['asset_balance']['total']:
                            addresses[maker_address]['asset_balance']['total'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[maker_address]['asset_balance']['total'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)
                        if offer_hash['want_asset_name'] not in addresses[maker_address_date]['asset_balance']['total']:
                            addresses[maker_address_date]['asset_balance']['total'][offer_hash['want_asset_name']] = int(txn['taker_amount'] * offer_ratio)
                        else:
                            addresses[maker_address_date]['asset_balance']['total'][offer_hash['want_asset_name']] += int(txn['taker_amount'] * offer_ratio)

                        # Decrement Balance of Maker Account
                        if offer_hash['offer_asset_name'] not in addresses[maker_address]['asset_balance']['smart_contract']:
                            addresses[maker_address]['asset_balance']['smart_contract'][offer_hash['offer_asset_name']] = int(txn['taker_amount'] * -1)
                        else:
                            addresses[maker_address]['asset_balance']['smart_contract'][offer_hash['offer_asset_name']] -= txn['taker_amount']
                        if offer_hash['offer_asset_name'] not in addresses[maker_address_date]['asset_balance']['smart_contract']:
                            addresses[maker_address_date]['asset_balance']['smart_contract'][offer_hash['offer_asset_name']] = int(txn['taker_amount'] * -1)
                        else:
                            addresses[maker_address_date]['asset_balance']['smart_contract'][offer_hash['offer_asset_name']] -= txn['taker_amount']

                        if offer_hash['offer_asset_name'] not in addresses[maker_address]['asset_balance']['total']:
                            addresses[maker_address]['asset_balance']['total'][offer_hash['offer_asset_name']] = int(txn['taker_amount'] * -1)
                        else:
                            addresses[maker_address]['asset_balance']['total'][offer_hash['offer_asset_name']] -= txn['taker_amount']
                        if offer_hash['offer_asset_name'] not in addresses[maker_address_date]['asset_balance']['total']:
                            addresses[maker_address_date]['asset_balance']['total'][offer_hash['offer_asset_name']] = int(txn['taker_amount'] * -1)
                        else:
                            addresses[maker_address_date]['asset_balance']['total'][offer_hash['offer_asset_name']] -= txn['taker_amount']

                        # Increment taker trade count for Taker Account
                        if 'taker' not in addresses[taker_address]['trade_type_count']:
                            addresses[taker_address]['trade_type_count']['taker'] = 1
                        else:
                            addresses[taker_address]['trade_type_count']['taker'] += 1
                        if 'taker' not in addresses[taker_address_date]['trade_type_count']:
                            addresses[taker_address_date]['trade_type_count']['taker'] = 1
                        else:
                            addresses[taker_address_date]['trade_type_count']['taker'] += 1

                        # Number of Taker Actions
                        if trade_pair not in addresses[taker_address]['takes']:
                            addresses[taker_address]['takes'][trade_pair] = 1
                        else:
                            addresses[taker_address]['takes'][trade_pair] += 1
                        if trade_pair not in addresses[taker_address_date]['takes']:
                            addresses[taker_address_date]['takes'][trade_pair] = 1
                        else:
                            addresses[taker_address_date]['takes'][trade_pair] += 1

                        # Number of Taker Wants and Offers
                        if 'wants' not in addresses[taker_address]['takes']:
                            addresses[taker_address]['takes']['wants'] = {}
                        if 'wants' not in addresses[taker_address_date]['takes']:
                            addresses[taker_address_date]['takes']['wants'] = {}
                        if 'offers' not in addresses[taker_address]['takes']:
                            addresses[taker_address]['takes']['offers'] = {}
                        if 'offers' not in addresses[taker_address_date]['takes']:
                            addresses[taker_address_date]['takes']['offers'] = {}
                        if offer_hash['want_asset_name'] not in addresses[taker_address]['takes']['wants']:
                            addresses[taker_address]['takes']['wants'][offer_hash['want_asset_name']] = 1
                        else:
                            addresses[taker_address]['takes']['wants'][offer_hash['want_asset_name']] += 1
                        if offer_hash['want_asset_name'] not in addresses[taker_address_date]['takes']['wants']:
                            addresses[taker_address_date]['takes']['wants'][offer_hash['want_asset_name']] = 1
                        else:
                            addresses[taker_address_date]['takes']['wants'][offer_hash['want_asset_name']] += 1
                        if offer_hash['offer_asset_name'] not in addresses[taker_address]['takes']['offers']:
                            addresses[taker_address]['takes']['offers'][offer_hash['offer_asset_name']] = 1
                        else:
                            addresses[taker_address]['takes']['offers'][offer_hash['offer_asset_name']] += 1
                        if offer_hash['offer_asset_name'] not in addresses[taker_address_date]['takes']['offers']:
                            addresses[taker_address_date]['takes']['offers'][offer_hash['offer_asset_name']] = 1
                        else:
                            addresses[taker_address_date]['takes']['offers'][offer_hash['offer_asset_name']] += 1

                        # Rich List Transaction Log
                        maker_want_rich_list_dict = {
                            '_id': maker_address + "_" + txn['transaction_hash'] + "_maker_want",
                            'block_number': txn['block_number'],
                            'block_date': txn['block_date'],
                            'transaction_type': txn['switcheo_transaction_type'],
                            'asset': offer_hash['want_asset_name'],
                            'amount': int(txn['taker_amount'] * offer_ratio),
                            'smart_contract': int(txn['taker_amount'] * offer_ratio),
                            'total': int(txn['taker_amount'] * offer_ratio)
                        }
                        address_transactions.append(maker_want_rich_list_dict)

                        maker_offer_rich_list_dict = {
                            '_id': maker_address + "_" + txn['transaction_hash'] + "_maker_offer",
                            'block_number': txn['block_number'],
                            'block_date': txn['block_date'],
                            'transaction_type': txn['switcheo_transaction_type'],
                            'asset': offer_hash['offer_asset_name'],
                            'amount': txn['taker_amount'],
                            'smart_contract': int(txn['taker_amount'] * -1),
                            'total': int(txn['taker_amount'] * -1)
                        }
                        address_transactions.append(maker_offer_rich_list_dict)

                        taker_want_rich_list_dict = {
                            '_id': taker_address + "_" + txn['transaction_hash'] + "_taker_want",
                            'block_number': txn['block_number'],
                            'block_date': txn['block_date'],
                            'transaction_type': txn['switcheo_transaction_type'],
                            'asset': offer_hash['want_asset_name'],
                            'amount': int(txn['taker_amount'] * offer_ratio),
                            'smart_contract': int(txn['taker_amount'] * offer_ratio * -1),
                            'total': int(txn['taker_amount'] * offer_ratio * -1)
                        }
                        address_transactions.append(taker_want_rich_list_dict)

                        taker_offer_rich_list_dict = {
                            '_id': taker_address + "_" + txn['transaction_hash'] + "_taker_offer",
                            'block_number': txn['block_number'],
                            'block_date': txn['block_date'],
                            'transaction_type': txn['switcheo_transaction_type'],
                            'asset': offer_hash['offer_asset_name'],
                            'amount': txn['taker_amount'],
                            'smart_contract': txn['taker_amount'],
                            'total': txn['taker_amount']
                        }
                        address_transactions.append(taker_offer_rich_list_dict)

            elif txn['switcheo_transaction_type'] == 'makeOffer':
                # Increment maker trade count for Maker Account
                if 'maker' not in addresses[maker_address]['trade_type_count']:
                    addresses[maker_address]['trade_type_count']['maker'] = 1
                else:
                    addresses[maker_address]['trade_type_count']['maker'] += 1
                if 'maker' not in addresses[maker_address_date]['trade_type_count']:
                    addresses[maker_address_date]['trade_type_count']['maker'] = 1
                else:
                    addresses[maker_address_date]['trade_type_count']['maker'] += 1

                # Number of Maker Offers
                if trade_pair not in addresses[maker_address]['makes']:
                    addresses[maker_address]['makes'][trade_pair] = 1
                else:
                    addresses[maker_address]['makes'][trade_pair] += 1
                if trade_pair not in addresses[maker_address_date]['makes']:
                    addresses[maker_address_date]['makes'][trade_pair] = 1
                else:
                    addresses[maker_address_date]['makes'][trade_pair] += 1

                # Number of Maker Wants and Offers
                if 'wants' not in addresses[maker_address]['makes']:
                    addresses[maker_address]['makes']['wants'] = {}
                if 'wants' not in addresses[maker_address_date]['makes']:
                    addresses[maker_address_date]['makes']['wants'] = {}
                if 'offers' not in addresses[maker_address]['makes']:
                    addresses[maker_address]['makes']['offers'] = {}
                if 'offers' not in addresses[maker_address_date]['makes']:
                    addresses[maker_address_date]['makes']['offers'] = {}
                if txn['want_asset_name'] not in addresses[maker_address]['makes']['wants']:
                    addresses[maker_address]['makes']['wants'][txn['want_asset_name']] = 1
                else:
                    addresses[maker_address]['makes']['wants'][txn['want_asset_name']] += 1
                if txn['want_asset_name'] not in addresses[maker_address_date]['makes']['wants']:
                    addresses[maker_address_date]['makes']['wants'][txn['want_asset_name']] = 1
                else:
                    addresses[maker_address_date]['makes']['wants'][txn['want_asset_name']] += 1
                if txn['offer_asset_name'] not in addresses[maker_address]['makes']['offers']:
                    addresses[maker_address]['makes']['offers'][txn['offer_asset_name']] = 1
                else:
                    addresses[maker_address]['makes']['offers'][txn['offer_asset_name']] += 1
                if txn['offer_asset_name'] not in addresses[maker_address_date]['makes']['offers']:
                    addresses[maker_address_date]['makes']['offers'][txn['offer_asset_name']] = 1
                else:
                    addresses[maker_address_date]['makes']['offers'][txn['offer_asset_name']] += 1

            elif txn['switcheo_transaction_type'] == 'deposit':
                deposit_address = txn[self.address_transaction_dict[txn['switcheo_transaction_type']]]
                addresses[deposit_address] = self.ni.mongo_db['addresses'].find_one({'_id': deposit_address})
                deposit_address_date = (deposit_address, txn_date)
                deposit_address_date_dict = {'address': deposit_address, 'date': txn_date}
                addresses[deposit_address_date] = self.ni.mongo_db['addresses_date'].find_one({'_id': deposit_address_date_dict})

                if addresses[deposit_address] is None:
                    addresses[deposit_address] = {}
                if addresses[deposit_address_date] is None:
                    addresses[deposit_address_date] = {}
                if 'asset_balance' not in addresses[deposit_address]:
                    addresses[deposit_address]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'asset_balance' not in addresses[deposit_address_date]:
                    addresses[deposit_address_date]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'fees_paid' not in addresses[deposit_address]:
                    addresses[deposit_address]['fees_paid'] = {}
                if 'fees_paid' not in addresses[deposit_address_date]:
                    addresses[deposit_address_date]['fees_paid'] = {}
                if 'trade_count' not in addresses[deposit_address]:
                    addresses[deposit_address]['trade_count'] = {}
                if 'trade_count' not in addresses[deposit_address_date]:
                    addresses[deposit_address_date]['trade_count'] = {}
                if 'amount_traded' not in addresses[deposit_address]:
                    addresses[deposit_address]['amount_traded'] = {}
                if 'amount_traded' not in addresses[deposit_address_date]:
                    addresses[deposit_address_date]['amount_traded'] = {}
                if 'total_amount_traded' not in addresses[deposit_address]:
                    addresses[deposit_address]['total_amount_traded'] = {}
                if 'total_amount_traded' not in addresses[deposit_address_date]:
                    addresses[deposit_address_date]['total_amount_traded'] = {}
                if 'trade_type_count' not in addresses[deposit_address]:
                    addresses[deposit_address]['trade_type_count'] = {}
                if 'trade_type_count' not in addresses[deposit_address_date]:
                    addresses[deposit_address_date]['trade_type_count'] = {}
                if 'makes' not in addresses[deposit_address]:
                    addresses[deposit_address]['makes'] = {}
                if 'makes' not in addresses[deposit_address_date]:
                    addresses[deposit_address_date]['makes'] = {}
                if 'takes' not in addresses[deposit_address]:
                    addresses[deposit_address]['takes'] = {}
                if 'takes' not in addresses[deposit_address_date]:
                    addresses[deposit_address_date]['takes'] = {}

                # Increment Smart Contract balance of Address
                if txn['deposit_asset_name'] not in addresses[deposit_address]['asset_balance']['smart_contract']:
                    addresses[deposit_address]['asset_balance']['smart_contract'][txn['deposit_asset_name']] = txn['deposit_amount']
                else:
                    addresses[deposit_address]['asset_balance']['smart_contract'][txn['deposit_asset_name']] += txn['deposit_amount']
                if txn['deposit_asset_name'] not in addresses[deposit_address_date]['asset_balance']['smart_contract']:
                    addresses[deposit_address_date]['asset_balance']['smart_contract'][txn['deposit_asset_name']] = txn['deposit_amount']
                else:
                    addresses[deposit_address_date]['asset_balance']['smart_contract'][txn['deposit_asset_name']] += txn['deposit_amount']

                # Decrement On Chain balance of Address
                if txn['deposit_asset_name'] not in addresses[deposit_address]['asset_balance']['on_chain']:
                    addresses[deposit_address]['asset_balance']['on_chain'][txn['deposit_asset_name']] = int(txn['deposit_amount'] * -1)
                else:
                    addresses[deposit_address]['asset_balance']['on_chain'][txn['deposit_asset_name']] -= txn['deposit_amount']
                if txn['deposit_asset_name'] not in addresses[deposit_address_date]['asset_balance']['on_chain']:
                    addresses[deposit_address_date]['asset_balance']['on_chain'][txn['deposit_asset_name']] = int(txn['deposit_amount'] * -1)
                else:
                    addresses[deposit_address_date]['asset_balance']['on_chain'][txn['deposit_asset_name']] -= txn['deposit_amount']

                # Rich List Transaction Log
                deposit_rich_list_dict = {
                    '_id': deposit_address + "_" + txn['transaction_hash'] + "_deposit",
                    'block_number': txn['block_number'],
                    'block_date': txn['block_date'],
                    'transaction_type': txn['switcheo_transaction_type'],
                    'asset': txn['deposit_asset_name'],
                    'amount': txn['deposit_amount'],
                    'on_chain': int(txn['deposit_amount'] * -1),
                    'smart_contract': txn['deposit_amount']
                }
                address_transactions.append(deposit_rich_list_dict)

            elif txn['switcheo_transaction_type'] == 'transfer' and txn['contract_hash_version'] == 'SWTH':
                transfer_to_address = txn['to_address']
                transfer_from_address = txn['from_address']

                addresses[transfer_to_address] = self.ni.mongo_db['addresses'].find_one({'_id': transfer_to_address})
                transfer_to_address_date = (transfer_to_address, txn_date)
                transfer_to_address_date_dict = {'address': transfer_to_address, 'date': txn_date}
                addresses[transfer_to_address_date] = self.ni.mongo_db['addresses_date'].find_one({'_id': transfer_to_address_date_dict})

                if addresses[transfer_to_address] is None:
                    addresses[transfer_to_address] = {}
                if addresses[transfer_to_address_date] is None:
                    addresses[transfer_to_address_date] = {}
                if 'asset_balance' not in addresses[transfer_to_address]:
                    addresses[transfer_to_address]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'asset_balance' not in addresses[transfer_to_address_date]:
                    addresses[transfer_to_address_date]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'fees_paid' not in addresses[transfer_to_address]:
                    addresses[transfer_to_address]['fees_paid'] = {}
                if 'fees_paid' not in addresses[transfer_to_address_date]:
                    addresses[transfer_to_address_date]['fees_paid'] = {}
                if 'trade_count' not in addresses[transfer_to_address]:
                    addresses[transfer_to_address]['trade_count'] = {}
                if 'trade_count' not in addresses[transfer_to_address_date]:
                    addresses[transfer_to_address_date]['trade_count'] = {}
                if 'amount_traded' not in addresses[transfer_to_address]:
                    addresses[transfer_to_address]['amount_traded'] = {}
                if 'amount_traded' not in addresses[transfer_to_address_date]:
                    addresses[transfer_to_address_date]['amount_traded'] = {}
                if 'total_amount_traded' not in addresses[transfer_to_address]:
                    addresses[transfer_to_address]['total_amount_traded'] = {}
                if 'total_amount_traded' not in addresses[transfer_to_address_date]:
                    addresses[transfer_to_address_date]['total_amount_traded'] = {}
                if 'trade_type_count' not in addresses[transfer_to_address]:
                    addresses[transfer_to_address]['trade_type_count'] = {}
                if 'trade_type_count' not in addresses[transfer_to_address_date]:
                    addresses[transfer_to_address_date]['trade_type_count'] = {}
                if 'makes' not in addresses[transfer_to_address]:
                    addresses[transfer_to_address]['makes'] = {}
                if 'makes' not in addresses[transfer_to_address_date]:
                    addresses[transfer_to_address_date]['makes'] = {}
                if 'takes' not in addresses[transfer_to_address]:
                    addresses[transfer_to_address]['takes'] = {}
                if 'takes' not in addresses[transfer_to_address_date]:
                    addresses[transfer_to_address_date]['takes'] = {}

                addresses[transfer_from_address] = self.ni.mongo_db['addresses'].find_one({'_id': transfer_from_address})
                transfer_from_address_date = (transfer_from_address, txn_date)
                transfer_from_address_date_dict = {'address': transfer_from_address, 'date': txn_date}
                addresses[transfer_from_address_date] = self.ni.mongo_db['addresses_date'].find_one({'_id': transfer_from_address_date_dict})

                if addresses[transfer_from_address] is None:
                    addresses[transfer_from_address] = {}
                if addresses[transfer_from_address_date] is None:
                    addresses[transfer_from_address_date] = {}
                if 'asset_balance' not in addresses[transfer_from_address]:
                    addresses[transfer_from_address]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'asset_balance' not in addresses[transfer_from_address_date]:
                    addresses[transfer_from_address_date]['asset_balance'] = {'on_chain': {}, 'smart_contract': {}, 'total': {}}
                if 'fees_paid' not in addresses[transfer_from_address]:
                    addresses[transfer_from_address]['fees_paid'] = {}
                if 'fees_paid' not in addresses[transfer_from_address_date]:
                    addresses[transfer_from_address_date]['fees_paid'] = {}
                if 'trade_count' not in addresses[transfer_from_address]:
                    addresses[transfer_from_address]['trade_count'] = {}
                if 'trade_count' not in addresses[transfer_from_address_date]:
                    addresses[transfer_from_address_date]['trade_count'] = {}
                if 'amount_traded' not in addresses[transfer_from_address]:
                    addresses[transfer_from_address]['amount_traded'] = {}
                if 'amount_traded' not in addresses[transfer_from_address_date]:
                    addresses[transfer_from_address_date]['amount_traded'] = {}
                if 'total_amount_traded' not in addresses[transfer_from_address]:
                    addresses[transfer_from_address]['total_amount_traded'] = {}
                if 'total_amount_traded' not in addresses[transfer_from_address_date]:
                    addresses[transfer_from_address_date]['total_amount_traded'] = {}
                if 'trade_type_count' not in addresses[transfer_from_address]:
                    addresses[transfer_from_address]['trade_type_count'] = {}
                if 'trade_type_count' not in addresses[transfer_from_address_date]:
                    addresses[transfer_from_address_date]['trade_type_count'] = {}
                if 'makes' not in addresses[transfer_from_address]:
                    addresses[transfer_from_address]['makes'] = {}
                if 'makes' not in addresses[transfer_from_address_date]:
                    addresses[transfer_from_address_date]['makes'] = {}
                if 'takes' not in addresses[transfer_from_address]:
                    addresses[transfer_from_address]['takes'] = {}
                if 'takes' not in addresses[transfer_from_address_date]:
                    addresses[transfer_from_address_date]['takes'] = {}

                # Increment Total balance of to Address
                if 'SWTH' not in addresses[transfer_to_address]['asset_balance']['total']:
                    addresses[transfer_to_address]['asset_balance']['total']['SWTH'] = txn['transfer_amount']
                else:
                    addresses[transfer_to_address]['asset_balance']['total']['SWTH'] += txn['transfer_amount']
                if 'SWTH' not in addresses[transfer_to_address_date]['asset_balance']['total']:
                    addresses[transfer_to_address_date]['asset_balance']['total']['SWTH'] = txn['transfer_amount']
                else:
                    addresses[transfer_to_address_date]['asset_balance']['total']['SWTH'] += txn['transfer_amount']

                # Increment On Chain balance of to Address
                if 'SWTH' not in addresses[transfer_to_address]['asset_balance']['on_chain']:
                    addresses[transfer_to_address]['asset_balance']['on_chain']['SWTH'] = txn['transfer_amount']
                else:
                    addresses[transfer_to_address]['asset_balance']['on_chain']['SWTH'] += txn['transfer_amount']
                if 'SWTH' not in addresses[transfer_to_address_date]['asset_balance']['on_chain']:
                    addresses[transfer_to_address_date]['asset_balance']['on_chain']['SWTH'] = txn['transfer_amount']
                else:
                    addresses[transfer_to_address_date]['asset_balance']['on_chain']['SWTH'] += txn['transfer_amount']

                # Decrement Total balance of from Address
                if 'SWTH' not in addresses[transfer_from_address]['asset_balance']['total']:
                    addresses[transfer_from_address]['asset_balance']['total']['SWTH'] = int(txn['transfer_amount'] * -1)
                else:
                    addresses[transfer_from_address]['asset_balance']['total']['SWTH'] -= txn['transfer_amount']
                if 'SWTH' not in addresses[transfer_from_address_date]['asset_balance']['total']:
                    addresses[transfer_from_address_date]['asset_balance']['total']['SWTH'] = int(txn['transfer_amount'] * -1)
                else:
                    addresses[transfer_from_address_date]['asset_balance']['total']['SWTH'] -= txn['transfer_amount']

                # Decrement On Chain balance of from Address
                if 'SWTH' not in addresses[transfer_from_address]['asset_balance']['on_chain']:
                    addresses[transfer_from_address]['asset_balance']['on_chain']['SWTH'] = int(txn['transfer_amount'] * -1)
                else:
                    addresses[transfer_from_address]['asset_balance']['on_chain']['SWTH'] -= txn['transfer_amount']
                if 'SWTH' not in addresses[transfer_from_address_date]['asset_balance']['on_chain']:
                    addresses[transfer_from_address_date]['asset_balance']['on_chain']['SWTH'] = int(txn['transfer_amount'] * -1)
                else:
                    addresses[transfer_from_address_date]['asset_balance']['on_chain']['SWTH'] -= txn['transfer_amount']

                # Rich List Transaction Log
                transfer_to_rich_list_dict = {
                    '_id': transfer_to_address + "_" + txn['transaction_hash'] + "_transfer_to",
                    'block_number': txn['block_number'],
                    'block_date': txn['block_date'],
                    'transaction_type': txn['switcheo_transaction_type'],
                    'asset': 'SWTH',
                    'amount': txn['transfer_amount'],
                    'on_chain': txn['transfer_amount'],
                    'total': txn['transfer_amount']
                }
                address_transactions.append(transfer_to_rich_list_dict)

                transfer_from_rich_list_dict = {
                    '_id': transfer_from_address + "_" + txn['transaction_hash'] + "_transfer_from",
                    'block_number': txn['block_number'],
                    'block_date': txn['block_date'],
                    'transaction_type': txn['switcheo_transaction_type'],
                    'asset': 'SWTH',
                    'amount': txn['transfer_amount'],
                    'on_chain': int(txn['transfer_amount'] * -1),
                    'total': int(txn['transfer_amount'] * -1)
                }
                address_transactions.append(transfer_from_rich_list_dict)

        self.ni.mongo_upsert_many(collection='address_transactions', upsert_list_dict=address_transactions)
        for address in addresses.keys():
            if type(address) is tuple:
                address_key = address[0]
                date_key = address[1]
                address_composite_date = {'address': address_key, 'date': date_key}
                self.ni.mongo_db['addresses_date'].update_one(
                    filter={'_id': address_composite_date},
                    update={
                        '$set': {
                            'fees_paid': addresses[address]['fees_paid'],
                            'trade_count': addresses[address]['trade_count'],
                            'amount_traded': addresses[address]['amount_traded'],
                            'total_amount_traded': addresses[address]['total_amount_traded'],
                            'asset_balance': addresses[address]['asset_balance'],
                            'trade_type_count': addresses[address]['trade_type_count'],
                            'makes': addresses[address]['makes'],
                            'takes': addresses[address]['takes'],
                        }
                    },
                    upsert=True
                )
            else:
                self.ni.mongo_db['addresses'].update_one(
                    filter={'_id': address},
                    update={
                        '$set': {
                            'fees_paid': addresses[address]['fees_paid'],
                            'trade_count': addresses[address]['trade_count'],
                            'amount_traded': addresses[address]['amount_traded'],
                            'total_amount_traded': addresses[address]['total_amount_traded'],
                            'asset_balance': addresses[address]['asset_balance'],
                            'trade_type_count': addresses[address]['trade_type_count'],
                            'makes': addresses[address]['makes'],
                            'takes': addresses[address]['takes'],
                        }
                    },
                    upsert=True
                )
                address_composite_date = {'address': address, 'date': txn_date}
                self.ni.mongo_db['addresses_date'].update_one(
                    filter={'_id': address_composite_date},
                    update={'$set': {'snapshot': addresses[address]}},
                    upsert=True
                )
                self.update_rich_list(address=address)

    def get_address_balance(self, address):
        asset_dict = {}
        balance_dict = self._get(url='https://api.neoscan.io/api/main_net/v1/get_balance/' + address)
        for asset in balance_dict['balance']:
            asset_dict[asset['asset_symbol']] = asset['amount']
        return asset_dict

    def ingest_current_address_balance(self, addresses):
        # addresses = self.ni.mongo_db['addresses'].find().distinct('_id')
        print(len(addresses))
        i = 0
        for address in addresses:
            i += 1
            print(i)
            self.ni.mongo_db['addresses'].update_one(
                filter={'_id': address},
                update={
                    '$set': {
                        'baseline_balance': self.get_address_balance(address=address),
                    }
                },
                upsert=True,
            )

    def update_rich_list(self, address):
        addr = self.ni.mongo_db['addresses'].find_one({'_id': address})
        if 'baseline_balance' in addr and'SWTH' in addr['baseline_balance']:
            total_amt = int(addr['baseline_balance']['SWTH'] * 100000000)
        else:
            total_amt = 0
        try:
            address_regex = re.compile("^" + addr['_id'])
            on_chain_amt = 0
            smart_contract_amt = 0
            for txn in self.ni.mongo_db['address_transactions'].find({'_id': {'$regex': address_regex}, }).sort(
                    'block_number'):
                if txn['asset'] == 'SWTH':
                    if txn['block_date'] >= '2018-10-30' and 'total' in txn:
                        total_amt += txn['total']
                    if 'on_chain' in txn:
                        on_chain_amt += txn['on_chain']
                    if 'smart_contract' in txn:
                        smart_contract_amt += txn['smart_contract']
            balance_dict = {
                'total': total_amt,
                'on_chain': on_chain_amt,
                'smart_contract': smart_contract_amt
            }
            self.ni.mongo_db['addresses'].update_one(
                filter={'_id': addr['_id']},
                update={
                    '$set': {
                        'rich_list': balance_dict,
                    }
                },
                upsert=True
            )
        except TypeError:
            pass

    def get_contract_balance(self, address, asset):
        function_name = 'getBalance'
        function_params = [{
            "type": "ByteArray",
            "value": reverse_hex(neo_get_scripthash_from_address(address=address))
        }, {
            "type": "ByteArray",
            "value": reverse_hex(self.sc.get_token_details()[asset]['hash'])
        }]
        script_test = self.neo_rpc_client.invokefunction(script_hash=self.contract_hash,
                                                         operation=function_name,
                                                         params=function_params)
        # print(reverse_hex('26ae7c6c9861ec418468c1f0fdc4a7f2963eb891'))
        # print(script_test)
        # print(reverse_hex(script_test['stack'][0]['value']))
        # print(int(reverse_hex(script_test['stack'][0]['value']), 16))
        disassembler = NeoDisassembler(bytecode=script_test['script'])
        for disassemble in disassembler.disassemble():
            print(disassemble)
