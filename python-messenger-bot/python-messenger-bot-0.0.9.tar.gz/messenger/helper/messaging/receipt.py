from .receipt_adjustment import ReceiptAdjustment
from .receipt_element import ReceiptElement

class Receipt(ReceiptAdjustment, ReceiptElement):

    def __init__(self, **kwargs):
        self.attachment_type = 'template'

        self.recipient_id = ''
        self.recipient_phone_number = ''
        self.recipient_user_ref = ''
        self.recipient_name = ''

        self.payload_template_type = 'receipt'
        self.payload_shareable = True
        self.payload_recipient_name = ''
        self.payload_merchant_name = ''
        self.payload_order_number = 0
        self.payload_currency = ''
        self.payload_payment_method = ''
        self.payload_timestamp = 0
        self.payload_elements = []
        self.payload_address_street1 = ''
        self.payload_address_street2 = ''
        self.payload_address_city = ''
        self.payload_address_postal_code = ''
        self.payload_address_state = ''
        self.payload_address_country = ''
        self.payload_summary_subtotal = ''
        self.payload_summary_shipping_cost = ''
        self.payload_summary_total_tax = ''
        self.payload_summary_total_cost = ''
        self.payload_adjustments = []

        return super().__init__(**kwargs)