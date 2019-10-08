from keeper_cnab240.banks.bank import Bank
from keeper_cnab240.banks.Itau.file_header import FileHeader
from keeper_cnab240.banks.Itau.file_footer import FileFooter
from keeper_cnab240.banks.Itau.payment_methods import PaymentMethods
from keeper_cnab240.banks.Itau.payment_status import PaymentStatus
from keeper_cnab240.banks.Itau.payment_types import PaymentTypes
from keeper_cnab240.banks.Itau.segments.A import SegmentA, SegmentAFooter, SegmentAHeader
from keeper_cnab240.banks.Itau.segments.ANF import SegmentANF
from keeper_cnab240.banks.Itau.segments.J import SegmentJ, SegmentJFooter, SegmentJHeader
from keeper_cnab240.banks.Itau.segments.J52 import SegmentJ52
from keeper_cnab240.company import Company
from keeper_cnab240.exceptions.InvalidPaymentMethod import InvalidPaymentMethod
from keeper_cnab240.payment import Payment


class Itau(Bank):
    bank_code = 341

    def __init__(self):
        super().__init__('Itaú', 'Itau', self.bank_code, 13, 1, 'payment_way',
                         payments_status=PaymentStatus,
                         payment_types=PaymentTypes)

        # Segment A
        super().set_segment('AHeader', SegmentAHeader, PaymentMethods.segment_a_anf(), shipping_only=True)
        super().set_segment('A', SegmentA, PaymentMethods.segment_a())
        super().set_segment('ANF', SegmentANF, PaymentMethods.segment_anf(), 'A')
        super().set_segment('AFooter', SegmentAFooter, PaymentMethods.segment_a_anf(), shipping_only=True)

        # Segment J
        super().set_segment('JHeader', SegmentJHeader, PaymentMethods.segment_j(), shipping_only=True)
        super().set_segment('J', SegmentJ, PaymentMethods.segment_j())
        super().set_segment('J52', SegmentJ52, PaymentMethods.segment_j(), shipping_only=True)
        super().set_segment('JFooter', SegmentJFooter, PaymentMethods.segment_j(), shipping_only=True)
    
    def get_file_header(self):
        file_header = FileHeader()
        file_header.set_bank(self)
        return file_header
    
    def get_file_footer(self):
        file_footer = FileFooter()
        file_footer.set_bank(self)
        return file_footer
    
    @staticmethod
    def get_company_document_id(document_type):
        return 2 if document_type == 'cnpj' else 1

    def verify_payment(self, payment: Payment, company: Company):
        payment = super().verify_payment(payment, company)
        if payment.get_attribute('type').value in PaymentMethods.transfer_methods():
            same_bank = int(payment.get_attribute('favored_bank')) == int(self.bank_code)
            same_owner = payment.get_attribute('favored_document_number') == company.document
            cur_payment_type = payment.get_attribute('type').value
            new_payment_type = None
            if same_bank and same_owner:
                new_payment_type = PaymentMethods.CC_D
            elif same_bank and not same_owner:
                new_payment_type = PaymentMethods.CC_ITAU
            elif not same_bank and same_owner:
                if cur_payment_type in PaymentMethods.transfer_doc_methods():
                    new_payment_type = PaymentMethods.DOC_MESMO_TITULAR
                elif cur_payment_type in PaymentMethods.transfer_ted_methods():
                    new_payment_type = PaymentMethods.TED_MESMO_TITULAR
                else:
                    raise InvalidPaymentMethod('{} is not a valid payment same owner transfer out of Itau'
                                               .format(cur_payment_type))
            elif not same_bank and not same_owner:
                if cur_payment_type in PaymentMethods.transfer_doc_methods():
                    new_payment_type = PaymentMethods.DOC_OUTRO_TITULAR
                elif cur_payment_type in PaymentMethods.transfer_ted_methods():
                    new_payment_type = PaymentMethods.TED_OUTRO_TITULAR
                else:
                    raise InvalidPaymentMethod('{} is not a valid payment other owner transfer out of Itau'
                                               .format(cur_payment_type))

            payment.set_attribute('type', new_payment_type)

        return payment
