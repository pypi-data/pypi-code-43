from inoon_lora_packet.packet import Packet, HexConverter, ErrorType


class ErrorV3Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'err_type',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [ErrorType[k] for k in ErrorType._member_map_]},
        ]

    def __str__(self):
        code_desc = {
            ErrorType.lora_over_re_tx: 'OverReTx',
            ErrorType.lora_join_fail: 'JoinFail',
            ErrorType.lora_rx: 'RxFail',
            ErrorType.lora_nok: 'Nok',
            ErrorType.lora_tx_inf: 'TxInfinite',
            ErrorType.lora_skip_high_g: 'SkipHighG',
            ErrorType.lora_flash_store: 'Flash Store failed',
            ErrorType.lora_flash_load: 'Flash Load failed',
            ErrorType.lora_flash_clear: 'Flash Clear failed',
            ErrorType.lora_flash_update: 'Flash Update failed',
            ErrorType.lora_power: 'LoRa Power failed',
            ErrorType.lora_beacon_start: 'ADV. TX failed',
            ErrorType.lora_fw_check: 'SoluM FW fail',
            ErrorType.mems_check: 'BMA280 err',
        }

        msg = ''
        msg += 'ERR | '
        msg += 'Type: {} | '.format(code_desc[self.err_type])
        return msg

    @property
    def code(self):
        """For V2 compatibility"""
        return self.err_type

    @classmethod
    def encode(cls, err_type):
        return format(err_type, '02x').lower()
