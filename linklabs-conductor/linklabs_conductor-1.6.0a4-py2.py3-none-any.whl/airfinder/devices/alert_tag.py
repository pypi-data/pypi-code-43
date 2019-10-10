""" Represents an Alert Tag """
from datetime import datetime

from conductor.airfinder.base import DownlinkMessageSpec
from conductor.airfinder.devices.tag import Tag


class AlertTagDownlinkMessageSpecV1(DownlinkMessageSpec):
    """ Message Spec for the Alert Tag v1.0. """

    header = {
        'def': ['msg_type', 'msg_spec_vers'],
        'struct': '>BB',
        'defaults': [0x00, 0x01]
    }

    msg_types = {
            'Configuration': {
                'def': ['mask', 'heartbeat', 'alert_heartbeat',
                        'alert_loc_upd', 'net_lost_scan_count',
                        'net_lost_scan_int', 'max_symble_retries',
                        'button_hold_len', 'audible_alarm_en'],
                'struct': '>BHBBBHBBB',
                'defaults': [0x00, 0x0258, 0x1e, 0x0f, 0x03,
                             0x012c, 0x03, 0x03, 0x01]
            },
            'Ack': {'type': 6},
            'Close': {'type': 7}
    }


class AlertTagDownlinkMessageSpecV2(AlertTagDownlinkMessageSpecV1):
    """ Message Spec for the Alert Tag v2.0. """

    def __init__(self):
        super().__init__()
        # Update Message Spec Version.
        self.header.update({'defaults': [0x00, 0x02]})

        # Update Configuration Message.
        #   - Add U Lite Flags Field.
        #   - Increase Change Mask from uint8 -> uint16.
        self.msg_types["Configuration"].update({
            'def': ['mask', 'heartbeat', 'alert_heartbeat',
                    'alert_loc_upd', 'net_lost_scan_count',
                    'net_lost_scan_int', 'max_symble_retries',
                    'button_hold_len', 'audible_alarm_en', 'ulite_flags'],
            'struct': '>HHBBBHBBBB',
            'defaults': [0x00, 0x0258, 0x1e, 0x0f, 0x03,
                         0x012c, 0x03, 0x03, 0x01, 0b01000000]
        })


class AlertTag(Tag):
    """ TODO """
    application = ''

    def _get_spec(self):
        if self.msg_spec_vers.major == 1:
            return AlertTagDownlinkMessageSpecV1()
        elif self.msg_spec_vers.major == 2:
            return AlertTagDownlinkMessageSpecV2()
        else:
            raise Exception("Unsupported Message Specification")

    def configure(self, time_to_live_s=60.0, **kwargs):
        """ TODO """
        pld = self._get_spec().build('Configuration', **kwargs)
        return self._send_message(pld, time_to_live_s)

    def send_ack(self, time_to_live_s=60.0):
        """ TODO """
        pld = self._get_spec().build("Ack")
        return self._send_message(pld, time_to_live_s)

    def send_alert_close(self, time_to_live_s=60.0):
        """ TODO """
        pld = self._get_sepc().build("Close")
        return self._send_message(pld, time_to_live_s)

    @property
    def acknowledged(self):
        return bool(self.metadata_json.get('acknowledged'))

    @property
    def alertModeFlags(self):
        return self.metadata_json.get('alertModeFlags')

    @property
    def alertModeHeartbeatInterval(self):
        return self.metadata_json.get('alertModeHeartbeatInterval')

    @property
    def alertModeLength(self):
        return self.metadata_json.get('alertModeLength')

    @property
    def alertModeLocationUpdateRate(self):
        return self.metadata_json.get('alertModeLocationUpdateRate')

    @property
    def audibleAlarmEnabled(self):
        return bool(self.metadata_json.get('audibleAlarmEnabled'))

    @property
    def averageRssi(self):
        return self.metadata_json.get('averageRssi')

    @property
    def batteryVoltage(self):
        return self.metadata_json.get('batteryVoltage')

    @property
    def buttonHoldLength(self):
        return self.metadata_json.get('buttonHoldLength')

    @property
    def diagnosticInfo(self):
        return self.metadata_json.get('diagnosticInfo')

    @property
    def firmwareVersion(self):
        return self.metadata_json.get('firmwareVersion')

    @property
    def hardwareId(self):
        return self.metadata_json.get('hardwareId')

    @property
    def uptime(self):
        val = self.metadata_json.get('uptime')
        return datetime.TimeDelta(seconds=int(val)) if val else None
