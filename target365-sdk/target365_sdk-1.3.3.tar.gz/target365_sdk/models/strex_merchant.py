from .model import Model

class StrexMerchant(Model):

    def _accepted_params(self):
        return [
            'merchantId',
            'shortNumberIds', # Array of shortNumberId like 'NO-2002'
            'password',
        ]
