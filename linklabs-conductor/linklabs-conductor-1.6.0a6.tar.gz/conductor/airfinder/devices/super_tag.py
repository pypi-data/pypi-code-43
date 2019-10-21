""" Represents a Supertag and its functionality. """

from conductor.subject import DownlinkSubject
from conductor.airfinder.base import DownlinkMessageSpec
from conductor.airfinder.devices.tag import Tag


class SupertagDownlinkMessageSpecV1(DownlinkMessageSpec):
    """ Supertag Message Specification v1.0.0. """

    header = {
        'def': ['msg_type', 'msg_spec_vers'],
        'struct': '>BB',
        'defaults': [0x00, 0x01]
    }

    msg_types = {
        'Configuration': {
            'def': ['mask', 'heartbeat', 'no_ap_heartbeat', 'no_sym_heartbeat',
                    'loc_upd', 'no_ap_loc_upd', 'no_sym_loc_upd',
                    'scans_per_fix', 'max_wifi_aps', 'max_cell_ids',
                    'loc_upd_order', 'net_lost_timeout', 'ref_lost_timeout',
                    'net_scan_int'],
            'struct': '>HIIIIIIBBBBHHH',
            'defaults': [0x0000, 0x0000003c, 0x00015180, 0x00015180,
                         0x0000000b, 0x00005460, 0x00005460, 0x04,
                         0x0a, 0x00, 0x1b, 0x0258, 0x0258, 0x00b4]
        }
    }


class SupertagDownlinkMessageSpecV2(SupertagDownlinkMessageSpecV1):
    """ Supertag Message Specification v2.0.0"""

    def __init__(self):
        super().__init__()

        # Update Message Spec Version.
        self.header.update({'defaults': [0x00, 0x02]})

        # Update Configuration Message.
        #   - Increase Change Mask Size
        #   - Added Help Mode fields
        #   - Added Accelerometer fields
        #   - Added Caching fields
        #   - Added GPS Power Settings
        self.msg_types['Configuration'].update({
            'def': ['mask', 'heartbeat', 'no_ap_heartbeat', 'no_sym_heartbeat',
                    'loc_upd', 'no_ap_loc_upd', 'no_sym_loc_upd',
                    'help_loc_upd', 'scans_per_fix', 'max_wifi_aps',
                    'max_cell_ids', 'loc_upd_order', 'acc_en', 'acc_dur',
                    'acc_thresh', 'shock_thresh', 'cache_en', 'cache_len',
                    'gps_pwr_mode', 'gps_timeout', 'net_lost_timeout',
                    'ref_lost_timeout', 'net_scan_int'],
            'struct': '>IIIIIIIIBBBBBHHHBBBHHHH',
            'defaults': [0x00000000, 0x0000003c, 0x00015180, 0x00015180,
                         0x0000000b, 0x0000003c, 0x00005460, 0x0000000b, 0x04,
                         0x0a, 0x00, 0x1b, 0x01, 0x0003, 0x0050, 0x00a0, 0x00,
                         0x00, 0x00, 0x00b4, 0x0258, 0x0258, 0x00b4]
        })

        # Add new Message Types
        #   - Test Mode Enable
        #   - Help Mode Ack
        self.msg_types.update({
            'EnableTestMode': {},
            'Ack': {
                'def': ['help_rxed'],
                'struct': '>H',
                'defaults': [0x1105]
            }
        })


class SercommDownlinkMessageSpecV1(SupertagDownlinkMessageSpecV2):
    """ Sercomm Message Spec V1.0.0. """

    def __init__(self):
        super().__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x01]})

        # Remove Ack from Message Spec.
        self.msg_types.pop('Ack')

        # Update new message types
        #   - Update Configuration
        #       + Removed Shock Threshold
        #       + Added Sym Retries
        #       + Added Network Token
        #   - Added Battery Consumption Window
        #   - Added Setting Diagnostic Mode
        #   - Added Requesting Consumption
        #   - Added Setting Throttling
        #   - Added FTP Information
        self.msg_types.update({
            'Configuration': {
                'def': ['mask', 'heartbeat', 'no_ap_heartbeat',
                        'no_sym_heartbeat', 'loc_upd', 'no_ap_loc_upd',
                        'no_sym_loc_upd', 'help_loc_upd', 'scans_per_fix',
                        'max_wifi_aps', 'max_cell_ids', 'loc_upd_order',
                        'acc_en', 'acc_dur', 'acc_thresh', 'cache_en',
                        'cache_len', 'gps_pwr_mode', 'gps_timeout',
                        'net_lost_timeout', 'ref_lost_timeout', 'net_scan_int',
                        'sym_retries', 'net_tok'],
                'struct': '>IIIIIIIIBBBBBHHBBBHHHHBI',
                'defaults': [0x00000000, 0x0000003c, 0x00015180, 0x00015180,
                             0x0000000b, 0x0000003c, 0x00005460, 0x0000000b,
                             0x04, 0x0a, 0x00, 0x1b, 0x01, 0x0003, 0x0050,
                             0x00, 0x00, 0x00, 0x00b4, 0x0258, 0x0258, 0x00b4,
                             0x05, 0x4f50454e]

            },
            'BattConsumptionWindow': {
                'def': ['mask', 'batt_cap', 'start_up_pwr', 'alive_time_pwr',
                        'loc_upd_pwr', 'net_scan_pwr', 'ble_conn_pwr',
                        'lte_success_pwr', 'lte_failed_pwr', 'gps_avg_pwr',
                        'wifi_avg_pwr', 'temp_read_pwr', 'batt_read_pwr',
                        'led_pwr', 'ftp_pwr'],
                'struct': '>IIIIHHHIIIIHHII',
                'defaults': [0x00000000, 0x00000000, 0x00000000, 0x00000000,
                             0x0000, 0x0000, 0x0000, 0x00000000, 0x00000000,
                             0x00000000, 0x00000000, 0x0000, 0x0000,
                             0x00000000, 0x00000000]
            },
            'SetDiagnosticMode': {
                'def': ['enable'],
                'struct': '>B',
                'defaults': [0x00]
            },
            'ConsumptionRequest': {},
            'SetThrottling': {
                'def': ['mask', 'enable', 'mode', 'win_len', 'min_batt',
                        'win_limit', 'batt_cap'],
                'struct': '>HBBIIBI',
                'defaults': [0x00, 0x00, 0x01, 0x0000001e, 0x00011940, 0x5a,
                             0x01010100]
            },
            'FtpAvailable': {
                'def': ['app_vers_major', 'app_vers_minor', 'app_vers_tag',
                        'modem_vers_major', 'modem_vers_minor',
                        'modem_vers_tag'],
                'struct': '>BBHBBH',
                'defaults': [0x00, 0x00, 0x0000, 0x00, 0x00, 0x0000]
            }
        })


class Supertag(Tag, DownlinkSubject):
    """ """
    application = ''

    def _get_spec(self):
        if self.msg_spec_vers.major == 1:
            return SupertagDownlinkMessageSpecV1()
        elif self.msg_spec_vers.major == 2:
            return SupertagDownlinkMessageSpecV2()
        else:
            raise Exception("No Supported Message Specification.")

    def _send_message(self, payload, time_to_live_s):
        body = {}
        body['commandTargets'] = {'targetNodeAddresses': [self.subject_id]}
        return self._send_message_with_body(body, payload, True,
                                            time_to_live_s, 0, 10)

    def configure(self, time_to_live_s=60.0, access_point=None, **kwargs):
        pld = self._get_spec().build_message("Configuration", **kwargs)
        return self._send_message(pld, time_to_live_s)

    def ack(self, time_to_live_s=60.0, access_point=None):
        """ TODO """
        pld = self._get_spec().build_message("Ack")
        return self._send_message(pld, time_to_live_s)

    def activate_test_mode(self, time_to_live_s=60.0, access_point=None):
        """ TODO """
        pld = self.get_spec().build_message("EnableTestMode")
        return self._send_message(pld, time_to_live_s)


class SercommSupertag(Supertag):
    """ """
    application = ''

    def __init__(self):
        super().__init__()
        del self.ack  # Not Supported in Sercomm Supertag.

    def _get_spec(self):
        if self.msg_spec_vers.major == 1:
            return SercommDownlinkMessageSpecV1()
        else:
            raise Exception("No Supported Message Specification.")

    def set_batt_window(self, time_to_live_s=60.0, access_point=None,
                        **kwargs):
        """ TODO """
        pld = self.get_spec().build_message("BattConsumptionWindow", **kwargs)
        return self._send_message(pld, time_to_live_s)

    def set_diag_mode(self, en, time_to_live_s=60.0, access_point=None):
        """ TODO """
        pld = self.get_spec().build_message("SetDiagnosticMode", enable=en)
        return self._send_message(pld, time_to_live_s)

    def req_batt_consumption(self, time_to_live_s, access_point=None):
        """ TODO """
        pld = self.get_spec().build_message("ConsumptionRequest")
        return self._send_message(pld, time_to_live_s)

    def set_throttling(self, time_to_live_s, access_point=None, **kwargs):
        """ TODO """
        pld = self.get_spec().build_message("SetThrottling", **kwargs)
        return self._send_message(pld, time_to_live_s)

    def ftp_notify(self, time_to_live_s, access_point=None, **kwargs):
        """ TODO """
        pld = self.get_spec().build_message("FtpAvailable", **kwargs)
        return self._send_message(pld, time_to_live_s)
