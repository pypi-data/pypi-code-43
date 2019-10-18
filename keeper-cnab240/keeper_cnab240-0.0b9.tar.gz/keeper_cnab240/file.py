from datetime import datetime
from enum import Enum
from keeper_cnab240.payment import Payment
from pydoc import locate
import os
import random


class File:
    def __init__(self, bank, company=None, payments=None):
        if payments is None:
            payments = []
        self.company = company
        self.payments = payments

        self.banks_codes = {
            '341': 'Itau',
        }

        self.bank = self.import_bank(bank)
        self.header = self.import_header()
        self.footer = self.import_footer()
        self.body = []
        self.lots_quantity = 1
        self.lines = []
        self.line_cursor = 0
    
    @staticmethod
    def import_bank(bank):
        bank_class_file = locate('keeper_cnab240.banks.' + bank + '.' + bank)
        bank_class = getattr(bank_class_file, bank)
        return bank_class()
        
    def get_bank_name_by_code(self, bank_code):
        return self.banks_codes[str(bank_code)]

    def import_header(self):
        return self.bank.get_file_header()
    
    def import_footer(self):
        return self.bank.get_file_footer()
    
    def verify(self):
        if self.header is None or self.footer is None:
            raise Exception('Header and Footer cannot be None')
        return True
    
    def add_payment(self, payment: Payment):
        payment = self.bank.verify_payment(payment, self.company)
        self.payments.append(payment)
    
    def process_payments(self):
        for payment in self.payments:
            register_number = 1
            payment_segments = self.bank.get_payment_segment(payment.get_attribute('type'))
            for _segment in payment_segments:
                segment = _segment['segment_class']()
                segment.set_bank(self.bank)
                segment.set_company(self.company)

                segment_data = payment.attributes
                payment_type = payment.get_attribute('type')
                payment_type = payment_type if not issubclass(type(payment_type), Enum) else payment_type.name
                segment_data['payment_way'] = _segment['payment_types'][payment_type]

                segment_data['lot_code'] = self.lots_quantity
                segment_data['register_number'] = register_number
                segment.set_data(segment_data)

                if hasattr(segment, 'get_header_line') and hasattr(segment, 'header'):
                    self.body.append(segment.get_header_line())

                if hasattr(segment, 'attributes') and segment.attributes is not None:
                    self.body.append(segment.to_line())

                if hasattr(segment, 'get_footer_line') and hasattr(segment, 'footer'):
                    self.body.append(segment.get_footer_line())

            self.lots_quantity += 1
            register_number += 1

    def generate(self, file_path=None, file_name=None):
        self.verify()
        self.lines.append(self.header.to_line())
        self.process_payments()

        for line in self.body:
            self.lines.append(line)

        self.footer.set_data(dict(
            lots_quantity=self.lots_quantity - 1,
            registers_quantity=len(self.lines) + 1,
        ))
        self.lines.append(self.footer.to_line())
        if file_path:
            return self.save_file(file_path, file_name)

        return True
    
    def read_file_content(self, file_content=""):
        self.payments = []
        if not file_content:
            raise Exception('File content cannot be empty.')

        self.lines = file_content.splitlines()

        line_index = 0
        payment_header_line = None
        for line in self.lines:
            if line_index == 0:
                self.header.set_attributes_from_line(line)
                if hasattr(self.header, 'extract_company'):
                    self.company = self.header.extract_company()
            elif line_index == (len(self.lines) - 1):
                self.footer.set_attributes_from_line(line)
            else:
                if line[8] == 'C':
                    payment_header_line = line
                elif line[8] != 'C' and line[8] != ' ':
                    payment_segment_data = self.bank.identify_payment_segment(line)
                    if not payment_segment_data:
                        raise Exception('Cannot identify payment segment: ' + payment_header_line + ', ' + line)

                    segment_class = payment_segment_data['segment_class']
                    payment_segment = segment_class()
                    payment_segment.set_attributes_from_line(line)
                    
                    payment = Payment(payments_status=self.bank.get_payments_status())
                    for attr_name, attr_value in payment_segment.get_dict().items():
                        payment.set_attribute(attr_name, attr_value)
                    
                    self.payments.append(payment)
            
            line_index += 1
    
    def get_content(self):
        return '\r\n'.join('%s' % line for line in self.lines) + '\r\n'
    
    def save_file(self, file_path, file_name):
        if not file_name:
            file_name = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S_") + str(random.randint(0, 10000) * 5) + '.rem'
        
        file_full_path = os.path.join(file_path, file_name)
        f = open(file_full_path, 'w')
        f.write(self.get_content())
        f.close()

        return file_full_path
    
    def next_line(self, append_line_break=False):
        if self.line_cursor > (len(self.lines) - 1):
            return None
        
        line = ""

        if append_line_break and self.line_cursor > 0:
            line += "\r\n"
        
        line += self.lines[self.line_cursor]
        
        self.line_cursor += 1
        return line
