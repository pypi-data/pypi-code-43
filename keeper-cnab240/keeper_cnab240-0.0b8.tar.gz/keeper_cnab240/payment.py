from functools import reduce
import json
import re


class Payment:
    PaymentsStatus = None

    def __init__(self, payments_status=None, **kwargs):
        self.attributes = dict(
            type=None,
            pay_date=None,
            effective_pay_date=None,
            favored_name=None,
            favored_document_number=None,
            favored_bank=None,
            agency=None,
            account=None,
            account_digit=None,
            our_number=None,
            currency_type='REA',
            your_number=None,
            ispb_code=None,
            goal_detail=None,
            payment_document_number=None,
            doc_goal=None,
            ted_goal=None,
            nf_document=None,
            identify_type=2,
            barcode=None,
            dv=None,
            due_rule=None,
            amount=None,
            amount_slip_original=None,
            free_field=None,
            free_field_slip_original=None,
            due_date=None,
            title_amount=None,
            discounts=None,
            additions=None,
            payment_amount=None,
            effective_paid_amount=None,
            favored_message=None,
            occurrences=None,
            move_type=None,
            assembly=None,
            payer_document_type=None,
            payer_document_number=None,
            payer_name=None,
            recipient_document_type=None,
            recipient_document_number=None,
            recipient_name=None,
            payee_document_type=None,
            payee_document_number=None,
            payee_name=None,
            slip_number=None
        )

        kwargs_keys = kwargs.keys()
        if 'slip_number' in kwargs_keys and kwargs['slip_number'] is not None:
            self.parse_slip(kwargs['slip_number'])

        for attr_name in self.attributes.keys():
            if attr_name in kwargs_keys:
                self.attributes[attr_name] = kwargs[attr_name]

        self.PaymentsStatus = payments_status

    def get_attribute(self, attr_name):
        if attr_name in self.attributes.keys():
            return self.attributes[attr_name]
        raise Exception('Payment does not have attribute called "' + attr_name + '"')

    def set_attribute(self, attr_name, attr_value):
        self.attributes[attr_name] = attr_value

    def get_attributes(self):
        return self.attributes

    def get_dict(self):
        return self.get_attributes()

    def get_json(self):
        return json.dumps(self.get_attributes())

    def parse_slip(self, slip_number):
        clean_number = re.sub('[^0-9]', '', str(slip_number))
        num_len = len(clean_number)

        if num_len == 44 or num_len == 47:
            self.attributes['favored_bank'] = int(clean_number[0:3])
            self.attributes['currency_type'] = int(clean_number[3:4])
            self.attributes['dv'] = int(clean_number[4:5] if num_len == 44 else clean_number[32:33])
            self.attributes['due_rule'] = int(clean_number[5:9] if num_len == 44 else clean_number[33:37])
            self.attributes['amount_slip_original'] = clean_number[9:19] if num_len == 44 else clean_number[37:47]
            self.attributes['amount'] = float(self.attributes['amount_slip_original'])/100
            self.attributes['free_field_slip_original'] = clean_number[19:44] if num_len == 44 else clean_number[4:9] + clean_number[10:20] + clean_number[21:31]
            self.attributes['free_field'] = int(self.attributes['free_field_slip_original'])
            self.validate_dv()
        else:
            raise Exception('Invalid slip number')

    def validate_dv(self):
        digits = str(self.attributes['favored_bank']) +\
            str(self.attributes['currency_type']) +\
            str(self.attributes['due_rule']) +\
            self.attributes['amount_slip_original'] +\
            self.attributes['free_field_slip_original']

        calculate = map(lambda x, y: x * y, (([2, 3, 4, 5, 6, 7, 8, 9] * 6)[0:43])[::-1], [int(e) for e in digits])
        final = reduce(lambda x, acc: x + acc, calculate)
        mod = final % 11
        dv = 11 - mod if 1 < mod < 10 else 1
        if dv != self.attributes['dv']:
            raise Exception('Invalid DV number')

        return True

    def status(self):
        occurrences = list(map(lambda x: self.get_attribute('occurrences')[x-2:x], list(range(2, 12, 2))))
        response = []
        for occ in occurrences:
            occ = occ if occ not in (0, 00, '00') else 'ZEROS'
            if len(occ) >= 2 and self.PaymentsStatus is not None and hasattr(self.PaymentsStatus, occ):
                response.append(self.PaymentsStatus(occ).get())

        return response
