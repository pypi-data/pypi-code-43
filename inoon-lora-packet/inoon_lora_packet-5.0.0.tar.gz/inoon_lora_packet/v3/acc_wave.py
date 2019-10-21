from inoon_lora_packet.packet import (Packet, InvalidPacketError, HexConverter)


class AccWaveV3Packet(Packet):
    axis_ctrl = {
        0: ['x', 'y', 'z'],
        1: ['x'],
        2: ['y'],
        3: ['z']
    }

    range_desc = {
        0: '2G',
        1: '4G',
        2: '8G',
        3: '16G',
    }

    def _field_spec(self):
        return [
            {'name': 'ctrl',
             'bytes': 1,
             'bit_fields': [
                 {'name': 'range', 'bits': 2, 'restrict': [0, 1, 2, 3]},
                 {'name': 'axis', 'bits': 2, 'restrict': [0, 1, 2, 3]},
                 {'name': 'id', 'bits': 4, 'restrict': None}
             ]},
            {'name': 'ctrl2',
             'bytes': 1,
             'bit_fields': [
                 {'name': 'pack_type', 'bits': 4, 'restrict': [0x0, 0x1, 0xF]},
                 {'name': 'seq', 'bits': 4, 'restrict': range(0, 16)},
             ]},
        ]

    def __init__(self, raw_packet):
        super(self.__class__, self).__init__(raw_packet)

        log_packet = raw_packet[4:]
        axises = self.axis_ctrl[self.ctrl.axis]

        bin_str = ''
        for c in log_packet:
            bin_str += '{0:04b}'.format(int(c, base=16))

        bit_size = 16
        scale = 1
        if self.ctrl2.pack_type == 0x1:
            bit_size = 12
            scale = 4

        if len(bin_str) % bit_size != 0:
            raise InvalidPacketError

        frame_max = (1 << bit_size-1) - 1
        frame_count = int(len(bin_str) / bit_size)
        frame_count = int(frame_count / len(axises))

        for axis in axises:
            setattr(self, axis, [])

        for i in range(0, len(bin_str), bit_size * len(axises)):
            offset = 0
            if 'x' in axises:
                frame_str = bin_str[i+offset:i+offset+bit_size]
                parsed_value = int(frame_str, base=2)
                if parsed_value > frame_max:
                    parsed_value = parsed_value - (1 << bit_size)

                getattr(self, 'x').append(parsed_value*scale)
                offset += bit_size

            if 'y' in axises:
                frame_str = bin_str[i+offset:i+offset+bit_size]
                parsed_value = int(frame_str, base=2)
                if parsed_value > frame_max:
                    parsed_value = parsed_value - (1 << bit_size)

                getattr(self, 'y').append(parsed_value*scale)
                offset += bit_size

            if 'z' in axises:
                frame_str = bin_str[i+offset:i+offset+bit_size]
                parsed_value = int(frame_str, base=2)
                if parsed_value > frame_max:
                    parsed_value = parsed_value - (1 << bit_size)

                getattr(self, 'z').append(parsed_value*scale)
                offset += bit_size

    def __str__(self):
        msg = ''
        msg += 'WAVE | '
        msg += 'Rng: {} | '.format(self.range_desc[self.ctrl.range])
        msg += 'Axis: {} | '.format(' '.join(self.axis_ctrl[self.ctrl.axis]))
        msg += 'ID: {} | '.format(self.ctrl.id)

        if self.ctrl2.pack_type == 0x1:
            msg += 'Pack: {}(b) | '.format(12)
        elif self.ctrl2.pack_type == 0x0 or self.ctrl2.pack_type == 0xF:
            msg += 'Pack: {}(b) | '.format(16)
        else:
            msg += 'Pack: -- | '

        if self.ctrl2.seq == 0xF:
            msg += 'Seq: Fin.'
        else:
            msg += 'Seq: {}'.format(self.ctrl2.seq)

        return msg

    @classmethod
    def encode(cls, pckt_id, seq, axis, rng, values):
        """values parameter is dict type.
        """
        enc = ''

        ctrl = ((rng << 2 | axis) << 4) | pckt_id
        enc += '{:02X}'.format(ctrl)
        enc += '{:02X}'.format(seq)

        if axis == 0:
            acc_values = list(zip(values['x'], values['y'], values['z']))

            for value in acc_values:
                enc += HexConverter.int_to_hex(value[0], 2, True)
                enc += HexConverter.int_to_hex(value[1], 2, True)
                enc += HexConverter.int_to_hex(value[2], 2, True)
        else:
            axis_name = ''
            if axis == 1:
                axis_name = 'x'
            elif axis == 2:
                axis_name = 'y'
            else:
                axis_name = 'z'

            for value in values[axis_name]:
                enc += HexConverter.int_to_hex(value, 2, True)

        return enc.lower()
