class ReceiptAdjustment:

    def __init__(self, **kwargs):
        self.name = ''
        self.amount = 0
        
        return super().__init__(**kwargs)

    def set_name(self, name):
        self.name = name
        
    def set_amount(self, amount):
        self.amount = amount