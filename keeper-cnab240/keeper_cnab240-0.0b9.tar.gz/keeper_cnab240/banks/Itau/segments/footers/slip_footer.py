from keeper_cnab240.segment_section import SegmentSection


class SlipFooter(SegmentSection):
    def __init__(self, data=None):
        super().__init__('SlipFooter', data, {
            'bank_code': {
                'type': 'int',
                'length': 3,
                'default': 341,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 0,
                'end': 3,
                'value': None,
            },
            'lot_code': {
                'type': 'int',
                'length': 4,
                'default': 0000,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 3,
                'end': 7,
                'value': None,
            },
            'register_type': {
                'type': 'int',
                'length': 1,
                'default': 5,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 7,
                'end': 8,
                'value': None,
            },
            'register_whites': {
                'type': 'whites',
                'length': 9,
                'default': ' ',
                'pad_content': ' ',
                'pad_direction': 'right',
                'required': False,
                'start': 8,
                'end': 17,
                'value': None,
            },
            'registers_quantity': {
                'type': 'int',
                'length': 6,
                'default': 4,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 17,
                'end': 23,
                'value': None,
            },
            'total_amount': {
                'type': 'float',
                'length': 18,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': True,
                'start': 23,
                'end': 41,
                'value': None,
            },
            'total_amount_zeros': {
                'type': 'zeros',
                'length': 18,
                'default': 0,
                'pad_content': 0,
                'pad_direction': 'left',
                'required': False,
                'start': 41,
                'end': 59,
                'value': None,
            },
            'total_amount_whites': {
                'type': 'whites',
                'length': 171,
                'default': ' ',
                'pad_content': ' ',
                'pad_direction': 'right',
                'required': False,
                'start': 59,
                'end': 230,
                'value': None,
            },
            'occurrences': {
                'type': 'string',
                'length': 10,
                'default': '',
                'pad_content': ' ',
                'pad_direction': 'right',
                'required': False,
                'start': 230,
                'end': 240,
                'value': None,
            },
        })
    
    def set_data(self, data=None):
        if data is None:
            data = dict()

        data['total_amount'] = data['payment_amount']
        super().set_data(data)
