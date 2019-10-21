from inoon_lora_packet.packet import Packet, HexConverter


class MRReportV3Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'mrt_protocol_version',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_battery_level',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_accumulated_runtime_duration',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_observation_time',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'mrt_reserved',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},
        ]

    def __str__(self):
        msg = ''
        msg = 'MRReport | '
        msg += 'Ver: {} | '.format(self.mrt_protocol_version)
        msg += 'BAT. : {} | '.format(self.mrt_battery_level)
        msg += 'RT. : {} | '.format(self.mrt_accumulated_runtime_duration)
        msg += 'Obsv. : {} | '.format(self.mrt_observation_time)
        msg += 'Resv. : {} | '.format(self.mrt_reserved)
        return msg

    @classmethod
    def encode(cls, version, battery, runtime_duration, observe_time, resv):
        enc = ''
        enc += format(version, '02x')
        enc += format(battery, '02x')
        enc += format(runtime_duration, '04x')
        enc += format(observe_time, '04x')
        enc += format(resv, '04x')
        return enc.lower()
