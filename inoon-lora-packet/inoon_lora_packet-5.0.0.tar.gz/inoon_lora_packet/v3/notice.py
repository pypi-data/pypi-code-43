import math

from inoon_lora_packet.packet import (Packet, NoticeType,
                                      HexConverter, InvalidPacketError)


# TODO: Refactoring this...

class NoticeV3Packet(Packet):
    err_desc = {
        0x00: 'No reason.',
        0x01: 'Exceed Alive period.',
        0x02: 'LoRa TX fail.',
        0x04: 'LoRa join fail.',
        0x05: 'Watchdog,',
        0x06: 'No Ack for PowerOff notice.',
        0x07: 'LoRa PowerOff Command.',
        0x08: 'BLE PowerOff.',
        0x09: 'Low Battery.',
        0x0A: 'Exceed Install request.',
        0x0B: 'RESET_CONFIG.',
        0x0C: 'PowefOffUninstallCommand',
        0x0D: 'PowerOffUninstallByResv.',
        0x0E: 'PowerOffDeviceUpsideDown',
        0x0F: 'PowerOffUninstallTimeout',
        0x81: 'Factory reset.',
        0x82: 'Upside down.',
        0x83: 'Watchdod changed.',
        0x84: 'LoRa reset.',
        0x85: 'BLE reset',
        0x86: 'Factory reset',
        0x87: 'LoRa SKT reset',
        0x88: 'LoRa FW update reset.',
        0x89: 'Init config reset',
        0x8a: 'Power up notice fail reset',
        0x8b: 'Report params change reset',
        0x8c: 'Inclination params change reset',
        0x8d: 'Runtime config change reset',
        0x8e: 'ReTx filed reset',
        0x8f: 'Infinite reset test',
        0x90: 'Wave timeout reset',
        0x91: 'LoRa join fail reset',
        0x92: 'NOK reset',
        0x93: 'Abnormal reset',
        0x94: 'Alive Failed reset',
        0x95: 'To Impact Mode',
        0x96: 'To ExcvIncl. Mode',
        0x97: 'To MRMT Mode',
        0x98: 'Boot Complete Remained',
    }

    setup_desc = {
        0: 'Uninstall',
        1: 'Install',
        2: 'ReqInstall'
    }

    def _field_spec(self):
        try:
            notice_type = int(self.raw_packet[:2], 16)

            if notice_type == NoticeType.power_up:
                return PowerUpV3Packet.spec
            elif notice_type == NoticeType.power_off:
                return PowerOffV3Packet.spec
            elif notice_type == NoticeType.setup:
                return SetupV3Packet.spec
            elif notice_type == NoticeType.test_result:
                return TestResultV3Packet.spec
            elif notice_type == NoticeType.rejection_count:
                return RejectionCount.spec
            elif notice_type == NoticeType.app_config:
                return AppModeConfig.spec

            raise InvalidPacketError
        except Exception:
            raise InvalidPacketError

    def __str__(self):
        msg = None
        if self.type == NoticeType.power_up:
            msg = self.__power_up_log_msg()
        elif self.type == NoticeType.power_off:
            msg = self.__power_off_log_msg()
        elif self.type == NoticeType.setup:
            msg = self.__setup_msg()
        elif self.type == NoticeType.test_result:
            msg = self.__test_result_log_msg()
        elif self.type == NoticeType.rejection_count:
            msg = self.__rejection_msg()
        elif self.type == NoticeType.app_config:
            msg = self.__config_msg()

        return msg

    def __power_up_log_msg(self):
        msg = 'ON | '
        msg += 'Reset({}): '.format(self.reset_reason)
        if self.reset_reason & 0x08 == 0x08:
            msg += 'CPU '
        if self.reset_reason & 0x04 == 0x04:
            msg += 'SW '
        if self.reset_reason & 0x02 == 0x02:
            msg += 'WD '
        if self.reset_reason & 0x01 == 0x01:
            msg += 'nRST'
        if self.reset_reason is 0:
            msg += '--'
        msg += ' | '

        msg += 'TurnOnCnt: {} | '.format(self.turn_on_count)
        msg += 'Err({}): {}'.format(self.off_reason,
                                    self.err_desc[self.off_reason])

        return msg

    def __power_off_log_msg(self):
        msg = 'OFF | '
        msg += 'Reason({}): {}'.format(self.reason, self.err_desc[self.reason])

        return msg

    def __test_result_log_msg(self):
        msg = 'TEST_RESULT | '
        msg += 'Enabled' if self.enable == 1 else 'Disabled'
        msg += 'Command {} |'.format(self.command)
        msg += 'CountLimit {} |'.format(self.count_limit)
        msg += 'MoveToNextFlag {} |'.format(self.move_to_next_flag)
        msg += 'CurrentCount {} |'.format(self.current_count)
        msg += 'running_flag {} |'.format(self.running_flag)
        msg += 'resv {} |'.format(self.resv)

        return msg

    def __setup_msg(self):
        return 'SETUP | {} -> {}'.format(self.previous, self.current)

    def __rejection_msg(self):
        msg = ''
        msg += 'REJECT | '
        msg += 'Count: {} | '.format(self.count)
        msg += 'Period: {} | '.format(self.period)
        msg += 'Threshold: {}'.format(self.threshold)

        return msg

    def __config_msg(self):
        msg = ''
        msg += 'APPCFG | '
        msg += 'Mode: {} | '.format(AppModeConfig.mode_desc[self.app_mode])
        msg += 'BMA RNG: {} | '.format(
            AppModeConfig.range_desc[self.bma_range])
        msg += 'HighG THR: {}mg | '.format(self.high_g_threshold)

        msg += '# Sub INTVL: {} | '.format(self.num_sub_interval)
        msg += 'nRF REJ THR: {}mg | '.format(self.nrf_reject_threshold)
        msg += 'nRF IMPACT THR: {}mg | '.format(self.nrf_impact_threshold)

        if self.incl_ck_per <= 60:
            msg += 'INCL CK PER: {}M | '.format(self.incl_ck_per)
        else:
            msg += 'INCL CK PER: {}H | '.format(self.incl_ck_per % 60)

        msg += '# TX SKIP: {} | '.format(self.num_tx_skip)

        x = self.acc_base_x
        y = self.acc_base_y
        z = self.acc_base_z

        if x == 0 and y == 0 and z == 0:
            msg += 'Base: Raw(0, 0, 0) / Deg(--, --, --) | '
        else:
            DEG_TO_RAD = 180 / math.pi
            deg_x = math.atan(x / ((y**2 + z**2)**0.5)) * DEG_TO_RAD
            deg_y = math.atan(y / ((x**2 + z**2)**0.5)) * DEG_TO_RAD
            deg_z = math.atan(((x**2 + y**2)**0.5) / z) * DEG_TO_RAD

            msg += 'Base: Raw({}, {}, {}) / Deg({}, {}, {}) | '.format(
                self.acc_base_x, self.acc_base_y, self.acc_base_z,
                round(deg_x, 2), round(deg_y, 2), round(deg_z, 2))

        msg += 'MRMT State: {} | '.format(
            AppModeConfig.mrmt_state_desc[self.mrmt_stat])
        msg += 'MRMT OP THR: {}mg | '.format(self.mrmt_op_threshold)
        msg += 'MRMT SHOCK THR: {}mg'.format(self.mrmt_shock_threshold)

        return msg


class PowerUpV3Packet():
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [NoticeType.power_up, NoticeType.power_off]},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [4]},

        {'name': 'reset_reason',
         'bytes': '1',
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'turn_on_count',
         'bytes': '1',
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'resv',
         'bytes': '1',
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'off_reason',
         'bytes': '1',
         'convert': HexConverter.hex_to_uint,
         'restrict': [key for key in NoticeV3Packet.err_desc.keys()]},

    ]

    @classmethod
    def encode(cls, reset_reason, turn_on_count, off_reason):
        enc_val = ''
        enc_val += format(1, '02x')
        enc_val += format(4, '02x')
        enc_val += format(reset_reason, '02x')
        enc_val += format(turn_on_count, '02x')
        enc_val += '00'
        enc_val += format(off_reason, '02x')
        return enc_val.lower()


class PowerOffV3Packet():
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [NoticeType.power_up, NoticeType.power_off]},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [1]},

        {'name': 'reason',
         'bytes': '1',
         'convert': HexConverter.hex_to_uint,
         'restrict': [key for key in NoticeV3Packet.err_desc.keys()]},
    ]

    @classmethod
    def encode(cls, reason):
        enc_val = ''
        enc_val += format(2, '02x')
        enc_val += format(1, '02x')
        enc_val += format(reason, '02x')
        return enc_val.lower()


class SetupV3Packet(Packet):
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [2]},

        {'name': 'current',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1, 2]},

        {'name': 'previous',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1, 2]},
    ]

    @classmethod
    def encode(cls, prev_install, current_install):
        enc_val = ''
        enc_val += format(NoticeType.setup, '02x')
        enc_val += format(2, '02x')
        enc_val += format(current_install, '02x')
        enc_val += format(prev_install, '02x')
        return enc_val.lower()


class TestResultV3Packet(Packet):
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [8]},

        {'name': 'enable',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1]},

        {'name': 'command',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': range(1, 7)},

        {'name': 'count_limit',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': range(0, 256)},

        {'name': 'move_to_next_flag',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1]},

        {'name': 'current_count',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': range(0, 256)},

        {'name': 'running_flag',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1]},

        {'name': 'resv',
         'bytes': 2,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},
    ]

    @classmethod
    def encode(cls, enable, command, count_limit, move_to_next_flag,
               current_count, running_flag, resv):
        enc_val = ''
        enc_val += format(NoticeType.test_result, '02x')
        enc_val += format(8, '02x')
        enc_val += format(enable, '02x')
        enc_val += format(command, '02x')
        enc_val += format(count_limit, '02x')
        enc_val += format(move_to_next_flag, '02x')
        enc_val += format(current_count, '02x')
        enc_val += format(running_flag, '02x')
        enc_val += format(resv, '04x')
        return enc_val.lower()


class RejectionCount(Packet):
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [4]},

        {'name': 'count',
         'bytes': 2,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'period',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'threshold',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

    ]

    @classmethod
    def encode(cls, count, period, threshold):
        enc_val = ''
        enc_val += format(NoticeType.rejection_count, '02x')
        enc_val += format(4, '02x')
        enc_val += format(count, '04x')
        enc_val += format(period, '02x')
        enc_val += format(threshold, '02x')

        return enc_val


class AppModeConfig(Packet):
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [28]},

        {'name': 'app_mode',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'bma_range',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'high_g_threshold',
         'bytes': 2,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'num_sub_interval',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'nrf_reject_threshold',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'nrf_impact_threshold',
         'bytes': 2,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'incl_ck_per',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'num_tx_skip',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'acc_base_x',
         'bytes': 2,
         'convert': HexConverter.hex_to_int16,
         'restrict': None},

        {'name': 'acc_base_y',
         'bytes': 2,
         'convert': HexConverter.hex_to_int16,
         'restrict': None},

        {'name': 'acc_base_z',
         'bytes': 2,
         'convert': HexConverter.hex_to_int16,
         'restrict': None},

        {'name': 'mr_resv',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'mrmt_stat',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'mrmt_op_threshold',
         'bytes': 2,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'mrmt_shock_threshold',
         'bytes': 2,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'resv',
         'bytes': 6,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},
    ]

    mode_desc = {
        0: 'exc',
        1: 'mrmt',
        2: 'impact',
    }

    range_desc = {
        0: '--',
        1: '2G',
        2: '4G',
        3: '8G',
        4: '16G',
    }

    mrmt_state_desc = {
        0: 'commission',
        1: 'inactive',
        2: 'active',
    }

    @classmethod
    def encode(cls):
        return ''
