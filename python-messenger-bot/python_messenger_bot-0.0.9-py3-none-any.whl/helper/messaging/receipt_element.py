from .element import Element

class ReceiptElement(Element):

    def __init__(self, **kwargs):
        self.subtitle = ''
        self.quantity = 0
        self.price = 0
        self.currency = ''
        self.image_url = ''
        
        return super().__init__(**kwargs)

    def set_subtitle(self, subtitle):
        self.subtitle = subtitle
        
    def set_quantity(self, quantity):
        self.quantity = quantity
        
    def set_price(self, price):
        self.price = price
        
    def set_currency(self, currency):
        self.currency = currency
        
    def set_image_url(self, image_url):
        self.image_url = image_url