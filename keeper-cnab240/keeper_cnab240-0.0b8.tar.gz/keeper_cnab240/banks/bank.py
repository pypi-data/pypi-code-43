from enum import Enum
from keeper_cnab240.company import Company
from keeper_cnab240.payment import Payment


class Bank:
    def __init__(self, name, slug, code, segment_position_identifier=None, segment_identifier_length=1,
                 segment_header_identifier_name=None, payments_status=None, payment_types=None):
        self.name = name
        self.slug = slug
        self.code = code
        self.available_segments = dict()
        self.segment_position_identifier = segment_position_identifier
        self.segment_identifier_length = segment_identifier_length
        self.segment_header_identifier_name = segment_header_identifier_name
        self.payments_status = payments_status
        self.payment_types = payment_types

    def set_segment(self, segment_name, segment_class, payment_types=None, segment_alias=None, shipping_only=False):
        if payment_types is None:
            payment_types = dict()
        params = dict(
            segment_name=segment_name,
            segment_class=segment_class,
            payment_types=payment_types,
            shipping_only=shipping_only,
        )

        if segment_alias:
            params['segment_alias'] = segment_alias
        else:
            params['segment_alias'] = segment_name

        for payment_type in payment_types:
            if payment_type not in self.available_segments:
                self.available_segments[payment_type] = list()

            if payment_types[payment_type] not in self.available_segments:
                self.available_segments[payment_types[payment_type]] = list()

            self.available_segments[payment_type].append(params)
            self.available_segments[payment_types[payment_type]].append(params)

    def get_file_header(self):
        pass

    def get_file_footer(self):
        pass

    def get_segment(self, segment):
        pass

    def get_payment_segment(self, payment_type):
        payment_type = payment_type if not issubclass(type(payment_type), Enum) else payment_type.name
        if payment_type in self.available_segments:
            return self.available_segments[payment_type]
        raise Exception('Payment Type not Found')

    def identify_payment_segment(self, payment_line):
        if not self.segment_position_identifier or not self.segment_header_identifier_name:
            return None

        for _segments in self.available_segments:
            for segment_data in self.available_segments[_segments]:
                if not segment_data['shipping_only']:
                    if payment_line[self.segment_position_identifier:
                                    (self.segment_position_identifier + self.segment_identifier_length)
                                    ] == segment_data['segment_alias']:
                        return segment_data

        return None

    def get_payments_status(self):
        return self.payments_status

    def get_payments_types(self):
        return self.payment_types

    def verify_payment(self, payment: Payment, company: Company):
        return payment
